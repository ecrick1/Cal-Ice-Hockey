-- Cal Ice Hockey — everything the prototype holds that this could not store.
--
-- The schema was written when a game was a date, a score and a list of goals.
-- The prototype has since grown live scoring with a real clock, a play-by-play
-- with eight kinds of play, opponent rosters, sponsors, an alumni list and
-- pages built out of blocks. An importer written against a schema that cannot
-- hold its input drops the difference in silence, which is the worst way to
-- find out - so scripts/audit-schema.mjs maps every field the prototype writes
-- to the column it lands in, and this closes the thirty-five it could not.
--
-- Run it and it should report nothing left.

-- ---------------------------------------------------------------- 1. Plays
--
-- The play-by-play was a goal or a penalty. It is now eight things: a goal, a
-- penalty, a shot on goal, a shot that missed, a face-off, a whistle, the
-- start or end of a period, and the goaltender changing.
--
-- Two decisions here.
--
-- Every play is about one person - the scorer, the player who took the
-- penalty, the shooter, whoever won the draw, the goaltender coming on. That
-- was called `scorer` because a goal was the only play that had one. It is
-- renamed rather than joined by a second near-identical column, which is
-- worth doing precisely because there are no rows yet: the cost of the right
-- name is zero today and rises every day after.
--
-- And the rest is jsonb rather than sixteen mostly-null columns. Whether a
-- whistle was for icing, which goaltender froze it, whether a pulled net had
-- an extra attacker - each belongs to one kind of play and is null on the
-- other seven. The common fields stay columns because they are what anything
-- ever filters or sorts on; `detail` holds what only one kind of play knows.

alter table game_plays rename column scorer_id to player_id;
alter table game_plays rename column scorer_name to player_name;

alter table game_plays add column if not exists detail jsonb not null default '{}'::jsonb;

alter table game_plays drop constraint if exists game_plays_kind_check;
alter table game_plays add constraint game_plays_kind_check check (kind in (
  'goal', 'penalty', 'shot', 'miss', 'faceoff', 'stoppage',
  'period', 'game', 'goalie', 'shootout', 'timeout'
));

-- A play-by-play is read in game order, always.
create index if not exists game_plays_game_idx on game_plays (game_id, created_at);

-- ---------------------------------------------------------------- 2. Games
--
-- What a game carries besides its score.

alter table games add column if not exists acha_game_id text;
alter table games add column if not exists tickets_url text;
alter table games add column if not exists forfeit boolean not null default false;
-- Named on the sheet, and a list rather than a column each.
alter table games add column if not exists officials jsonb;
-- The league's own power-play counts for the night: attempts and conversions
-- a side. Roughly a third of games have none recorded, and null says so where
-- zero would claim nobody had a power play.
alter table games add column if not exists power_play jsonb;
-- Three stars, in order.
alter table games add column if not exists stars jsonb;
-- Attempts, in the order they were taken.
alter table games add column if not exists shootout jsonb;
-- The story written before the game and the one written after it.
alter table games add column if not exists preview_id uuid references news(id) on delete set null;
alter table games add column if not exists recap_id uuid references news(id) on delete set null;

-- ------------------------------------------------------- 3. The live game
--
-- 0016 and 0018 gave a live game a clock, a score and shots. Scoring one for
-- real needed the rest of it: the warm-up before the puck drops, the
-- intermission clock between periods, the penalties being served, who has
-- been thrown out, and the arm up for a delayed call.
--
-- `running` is not here on purpose - a clock is running exactly when
-- live_started_at is not null, and a second column saying so is a second
-- column that can disagree.

alter table games add column if not exists live_warmup boolean not null default false;
-- A finished game being typed up rather than scored. The clock is not running
-- and must never be fed to the strength model, which has nothing to expire it.
alter table games add column if not exists live_retro boolean not null default false;
-- The arm is up and play has not stopped: 'us', 'them', or null.
alter table games add column if not exists live_delayed text
  check (live_delayed is null or live_delayed in ('us', 'them'));
-- Penalties are entered one at a time, so between the first name and the
-- second the count is a real number that is about to be wrong. This holds the
-- readout until the whistle is settled.
alter table games add column if not exists live_assessing boolean not null default false;

-- The intermission runs on a clock of its own, anchored the same way the game
-- clock is. It cannot borrow the game clock, which is holding the full period
-- for the one about to start.
alter table games add column if not exists live_break_ms int;
alter table games add column if not exists live_break_at timestamptz;
alter table games add column if not exists live_break_len int;

-- Who was in net before it was emptied, so the goaltender can come back.
alter table games add column if not exists live_pulled_us text;
alter table games add column if not exists live_pulled_them text;

-- Penalties on the clock, players thrown out, and shots by period. Lists and
-- maps rather than columns: a game has any number of each.
alter table games add column if not exists live_penalties jsonb not null default '[]'::jsonb;
alter table games add column if not exists live_ejected jsonb not null default '[]'::jsonb;
alter table games add column if not exists live_period_shots jsonb not null default '{}'::jsonb;

-- ------------------------------------------------------------- 4. People
--
-- Which forward. The position column says F, D or G because that is what the
-- league publishes; a scoresheet says left wing, centre or right wing, and so
-- does ours once somebody has said which.
alter table people add column if not exists spot text
  check (spot is null or spot in ('LW', 'C', 'RW'));
alter table people add column if not exists acha_id text;

-- -------------------------------------------------------- 5. The visitors
--
-- Their own colours, for the crest and the bars on a game page.
alter table opponents add column if not exists color text;
alter table opponents add column if not exists mascot text;
alter table opponents add column if not exists acha_team_id text;

-- Their box score line gains what ours already had, plus the link back to the
-- roster row it came from - so a name corrected on the roster is not a
-- different player on last month's sheet.
alter table opponent_game_stats add column if not exists position text;
alter table opponent_game_stats add column if not exists shots int not null default 0;
alter table opponent_game_stats add column if not exists opponent_player_id uuid
  references opponent_players(id) on delete set null;

-- --------------------------------------------------------------- 6. News
--
-- A recap belongs to the game it is about, so a game page can offer it and a
-- story can link back.
alter table news add column if not exists game_id uuid references games(id) on delete set null;

-- ----------------------------------------------------------- 7. Sponsors
--
-- The people who pay for the ice. A name, a mark and a link out.
create table if not exists sponsors (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  logo_url text,
  url text,
  tier text,
  sort int not null default 0,
  published boolean not null default true,
  created_at timestamptz not null default now()
);

alter table sponsors enable row level security;
create policy "public read sponsors" on sponsors for select using (published);
create policy "admin all sponsors" on sponsors for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- ------------------------------------------------------------- 8. Alumni
--
-- A sign-up rather than a directory: somebody who played here saying where
-- they are now. Private, like the recruit inbox - the public may add
-- themselves and nothing more.
create table if not exists alumni (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text,
  grad_year text,
  years text,
  number text,
  position text,
  city text,
  note text,
  read boolean not null default false,
  created_at timestamptz not null default now()
);

alter table alumni enable row level security;
create policy "public submit alumni" on alumni for insert with check (true);
create policy "admin read alumni" on alumni for select using (auth.role() = 'authenticated');
create policy "admin write alumni" on alumni for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- -------------------------------------------------------------- 9. Pages
--
-- Pages built out of blocks in the console: a hero, prose, cards, figures, a
-- picture, a call to action, questions that open. The blocks are jsonb
-- because their shape is the block type's business and adding a type should
-- not be a migration.
--
-- The menu bar is one ordered document rather than a table of rows: it is
-- always read whole, always written whole, and nesting it in rows would buy
-- nothing but joins.
create table if not exists site_pages (
  id uuid primary key default gen_random_uuid(),
  slug text unique,
  title text not null default 'Untitled page',
  blocks jsonb not null default '[]'::jsonb,
  published boolean not null default true,
  sort int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table site_pages enable row level security;
create policy "public read pages" on site_pages for select using (published);
create policy "admin all pages" on site_pages for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
