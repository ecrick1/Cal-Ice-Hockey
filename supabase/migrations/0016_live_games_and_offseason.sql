-- Cal Ice Hockey — live game state, and off-season mode.
--
-- A game is in exactly one of three states:
--
--   scheduled  no result, not started
--   live       live_period is set and there is no final score
--   final      score_us / score_them are set
--
-- The final score stays the single source of truth for the record, so a live
-- game never moves the W-L-T and season_records needs no change. Ending a game
-- copies the live score into the result columns and clears the live ones in a
-- single update, which is why no row can be both.

alter table games add column if not exists live_period text;        -- '1' | '2' | '3' | 'OT' | 'SO'
alter table games add column if not exists live_clock text;         -- free text, e.g. '12:34'
alter table games add column if not exists live_us int;
alter table games add column if not exists live_them int;
alter table games add column if not exists live_intermission boolean not null default false;
alter table games add column if not exists live_updated_at timestamptz;

-- A row cannot be live and final at once. Cheap to enforce, and the one
-- invariant the public pages depend on when deciding what to render.
alter table games drop constraint if exists games_not_live_and_final;
alter table games add constraint games_not_live_and_final
  check (live_period is null or (score_us is null and score_them is null));

-- The public site asks "is anything live right now" on nearly every page.
create index if not exists games_live_idx on games (live_period) where live_period is not null;

-- Stamp the update time on any live change, so a client can tell a stale
-- scoreboard from a quiet one.
create or replace function set_live_updated_at() returns trigger as $$
begin
  if new.live_period is distinct from old.live_period
     or new.live_us is distinct from old.live_us
     or new.live_them is distinct from old.live_them
     or new.live_clock is distinct from old.live_clock
     or new.live_intermission is distinct from old.live_intermission then
    new.live_updated_at = now();
  end if;
  return new;
end;
$$ language plpgsql;

drop trigger if exists games_live_updated_at on games;
create trigger games_live_updated_at before update on games
  for each row execute function set_live_updated_at();

-- Off-season hides the score strip on the public site.
--
--   off_season  'true' | 'false'   (settings is key/value text)
--
-- No DDL needed; recorded here so the key is documented with the schema.
insert into settings (key, value) values ('off_season', 'false')
  on conflict (key) do nothing;
