-- Record who wrote it, on every write rather than only the first.
--
-- updated_by had a default of auth.uid(), and a default applies when a column
-- is omitted from an INSERT. The row is inserted once and updated forever
-- after, and an UPDATE does not consult defaults - so every save after the
-- first left the author null. The history table inherited the gap, since it
-- copies the column it is given.
--
-- Which quietly cost the point of the exercise: editing is by invitation so
-- that a change can be traced to somebody, and until now the answer to "who
-- did this" was null for every version.
--
-- Set by the database from the session, not accepted from the client, so it
-- remains a fact rather than a claim.

create or replace function public.stamp_site_state_author()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  new.updated_by := auth.uid();
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists site_state_stamp_author on public.site_state;
create trigger site_state_stamp_author
  before insert or update on public.site_state
  for each row
  execute function public.stamp_site_state_author();
