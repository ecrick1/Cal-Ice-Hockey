-- Cal Ice Hockey — a real game clock, penalties, and play-by-play.
--
-- 0016 gave a game a live score and a typed clock string. This replaces the
-- string with an anchor the clock is computed from, and adds the two things a
-- scorekeeper actually enters during a game.
--
-- The clock is stored as (live_clock_ms, live_started_at):
--
--   stopped: live_clock_ms is what is left, live_started_at is null
--   running: time left = live_clock_ms - (now() - live_started_at)
--
-- Storing the remaining time directly would mean a write per second per game,
-- drift between the scorekeeper and every viewer, and a clock that resets on
-- reload. Every client computes the same number from the same two columns and
-- ticks locally instead.

alter table games add column if not exists live_clock_ms int;
alter table games add column if not exists live_started_at timestamptz;

-- The free-text clock is superseded by the pair above.
alter table games drop column if exists live_clock;

-- Play-by-play. One row per goal or penalty, entered live.
--
-- Our players link to the roster so a goal writes straight through to the box
-- score; the opponent's are free text, exactly as opponent_game_stats already
-- does — we do not keep other teams' rosters.
create table if not exists game_plays (
  id uuid primary key default gen_random_uuid(),
  game_id uuid not null references games(id) on delete cascade,
  kind text not null check (kind in ('goal', 'penalty')),
  team text not null check (team in ('us', 'them')),
  period text not null default '1',
  clock text not null default '',            -- display only, e.g. '12:34'
  -- goal
  scorer_id uuid references players(id) on delete set null,
  scorer_name text not null default '',
  assist_ids uuid[] not null default '{}',
  strength text check (strength in ('EV', 'PP', 'SH', 'EN', 'PS')),
  -- penalty
  minutes int,
  infraction text not null default '',
  -- a penalty stops being served at this many seconds from the opening face-off
  ends_at_secs int,
  ended boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists game_plays_game_idx on game_plays (game_id, created_at);

alter table game_plays enable row level security;

-- Play-by-play is public the moment it is entered; that is the point of it.
create policy "public read game plays" on game_plays for select using (true);
create policy "admin all game plays" on game_plays for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- Only one game can be live at a time. Two live scoreboards would fight over
-- the home page widget and the front of the score strip, and there is only
-- ever one scorekeeper.
create unique index if not exists games_one_live_idx
  on games ((live_period is not null)) where live_period is not null;
