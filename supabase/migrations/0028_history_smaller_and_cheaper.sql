-- The version history was outgrowing the database it protects.
--
-- Every save copies the whole four-megabyte document into site_state_history,
-- and twenty of those is eighty megabytes - of a five-hundred megabyte
-- database, to keep undo for a club site. It had reached seventy-five before
-- anything had even been pruned, and the table had never been autovacuumed, so
-- deleted versions would have left their space behind and every touch of it
-- would have got slower. That path ends in writes timing out.
--
-- Eight versions instead of twenty. Eight covers a bad afternoon, which is
-- what this is for; twenty was covering a bad month at four times the price.

create or replace function public.keep_site_state_history()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  cutoff bigint;
begin
  insert into public.site_state_history (key, value, rev, written_at, written_by)
  values (old.key, old.value, old.rev, old.updated_at, old.updated_by);

  /* Find the boundary first, then delete by it. The previous form put an
     ORDER BY ... OFFSET subquery inside the DELETE, which makes the planner
     sort the key's rows on every single save; this reads one id from the
     index and then deletes on a plain comparison. */
  select id into cutoff
  from public.site_state_history
  where key = old.key
  order by id desc
  offset 8 limit 1;

  if cutoff is not null then
    delete from public.site_state_history
    where key = old.key and id <= cutoff;
  end if;

  return new;
end $$;

-- Bring what is already there down to the new depth.
do $$
declare
  cutoff bigint;
begin
  select id into cutoff
  from public.site_state_history
  where key = 'cal-hockey-site'
  order by id desc
  offset 8 limit 1;

  if cutoff is not null then
    delete from public.site_state_history
    where key = 'cal-hockey-site' and id <= cutoff;
  end if;
end $$;

-- A table this size is worth vacuuming on its own schedule rather than waiting
-- for the default thresholds, which are written for tables of small rows and
-- will not fire on seventeen.
alter table public.site_state_history set (
  autovacuum_vacuum_scale_factor = 0,
  autovacuum_vacuum_threshold = 4,
  autovacuum_analyze_scale_factor = 0,
  autovacuum_analyze_threshold = 4
);
alter table public.site_state set (
  autovacuum_vacuum_scale_factor = 0,
  autovacuum_vacuum_threshold = 4
);
