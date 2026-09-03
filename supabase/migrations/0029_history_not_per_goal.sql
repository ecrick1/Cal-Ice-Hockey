-- Keeping a version per save is right for editing and wrong for scoring.
--
-- Every save copies the whole document into site_state_history, and that copy
-- is the same size as the save itself: recording one goal moves the site
-- twice. While a game is being scored the saves come constantly - the clock,
-- a penalty, a shot - and each one was buying a version of the site that
-- differs from the one before it by a single number. An hour of hockey filled
-- the history eight times over and pushed everything genuinely worth undoing
-- out of it, at exactly the moment the database had least to spare. Writes
-- timing out mid-game is the same problem seen from the other end.
--
-- So a version is kept when the one before it is more than a minute old.
-- Undo is for "put back what it was before I started", and a minute is finer
-- than anybody has ever wanted that. What it costs is the ability to step back
-- through a burst goal by goal, which was never usable anyway: the eight slots
-- would all have been the same minute of the same game.

create or replace function public.keep_site_state_history()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  cutoff bigint;
  last_at timestamptz;
begin
  select written_at into last_at
  from public.site_state_history
  where key = old.key
  order by id desc
  limit 1;

  /* The first version is always kept: with nothing behind it there is nothing
     to step back to, which is the case where undo matters most. */
  if last_at is null or old.updated_at is null
     or old.updated_at - last_at > interval '60 seconds' then
    insert into public.site_state_history (key, value, rev, written_at, written_by)
    values (old.key, old.value, old.rev, old.updated_at, old.updated_by);

    select id into cutoff
    from public.site_state_history
    where key = old.key
    order by id desc
    offset 8 limit 1;

    if cutoff is not null then
      delete from public.site_state_history
      where key = old.key and id <= cutoff;
    end if;
  end if;

  return new;
end $$;
