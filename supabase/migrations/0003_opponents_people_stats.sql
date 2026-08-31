-- Cal Ice Hockey — opponents, person records, per-player game stats, news authors.
--
-- Changes the data model in three ways:
--
--   1. Opponents become rows, not free text, so they can carry a logo.
--   2. A player is a *person* who appears on a season's roster, rather than a
--      standalone row per season. Career stats follow the person, so they no
--      longer break when a name is spelled differently between seasons.
--   3. Player stats are entered per game. Season and career totals are derived.
--
-- DESTRUCTIVE: moves columns off `players` and drops `games.opponent`.
-- Existing player rows are migrated into `people` first. All current data is
-- seed data and is reproducible with `pnpm seed`.

-- ============================================================
-- 1. Opponents
-- ============================================================

create table opponents (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  short_name text not null default '',      -- badge label, e.g. "SJSU"
  logo_url text,                            -- media bucket; falls back to initials
  created_at timestamptz not null default now()
);

alter table games add column opponent_id uuid references opponents(id) on delete restrict;

-- Nothing to migrate: games is empty. Deleting an opponent that has games is
-- blocked rather than cascading — losing a game log to a mis-click is worse
-- than being told to reassign it first.
alter table games drop column opponent;

-- ============================================================
-- 2. People
-- ============================================================
-- Fields that belong to the human (name, hometown, school, bio, photo) live
-- here. Fields that are true only for one season (number, position, class,
-- captaincy) stay on `players`.
--
-- `name` is deliberately NOT unique: two different players really can share a
-- name, and that is the exact case this table exists to keep separate. The
-- admin UI warns on near-duplicates instead.

create table people (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  hometown text not null default '',
  high_school text not null default '',
  prior_team text not null default '',      -- juniors/club team before Cal
  shoots text not null default '',
  height text not null default '',
  bio text not null default '',
  photo_url text,
  ep_player_id int unique,
  created_at timestamptz not null default now()
);
create index people_name_idx on people (lower(name));

-- Fold existing roster rows into people, one per distinct name.
insert into people (name, hometown, shoots, height, bio, photo_url, ep_player_id)
select distinct on (lower(name))
  name, hometown, shoots, height, bio, photo_url, ep_player_id
from players
order by lower(name), created_at;

alter table players add column person_id uuid references people(id) on delete cascade;

update players p
set person_id = pe.id
from people pe
where lower(pe.name) = lower(p.name);

alter table players alter column person_id set not null;

-- Captaincy: '' | 'C' | 'A'. Per-season, so it belongs here rather than on people.
alter table players add column captain text not null default ''
  check (captain in ('', 'C', 'A'));

-- These now live on people.
alter table players
  drop column name,
  drop column hometown,
  drop column shoots,
  drop column height,
  drop column bio,
  drop column photo_url,
  drop column ep_player_id;

-- gp/g/a/pim stay, but change meaning: they are now a manual fallback for
-- seasons with no box scores (imported history), mirroring how
-- seasons.record_override works. Live seasons derive totals from game_stats.
comment on column players.gp is 'Manual fallback; ignored when game_stats rows exist for this player.';

create index players_person_idx on players(person_id);

-- ============================================================
-- 3. Per-player game stats
-- ============================================================

create table game_stats (
  id uuid primary key default gen_random_uuid(),
  game_id uuid not null references games(id) on delete cascade,
  player_id uuid not null references players(id) on delete cascade,
  dressed boolean not null default true,    -- false = scratched, does not count toward GP
  g int not null default 0,
  a int not null default 0,
  pim int not null default 0,
  saves int,                                -- goalies only
  goals_against int,                        -- goalies only
  created_at timestamptz not null default now(),
  unique (game_id, player_id)
);
create index game_stats_game_idx on game_stats(game_id);
create index game_stats_player_idx on game_stats(player_id);

-- ============================================================
-- 4. News authors
-- ============================================================
-- Free text, not a link to an auth user: the person who wrote a post is not
-- necessarily someone with a login, and "Coach Fazio" reads better than an email.

alter table news add column author text not null default '';

-- ============================================================
-- 5. Row-level security for the new tables
-- ============================================================

alter table opponents  enable row level security;
alter table people     enable row level security;
alter table game_stats enable row level security;

create policy "public read opponents"  on opponents  for select using (true);
create policy "public read people"     on people     for select using (true);
create policy "public read game_stats" on game_stats for select using (true);

create policy "admin all opponents"  on opponents  for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all people"      on people     for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all game_stats"  on game_stats for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- ============================================================
-- 6. Derived stat views
-- ============================================================
-- Same fallback rule as season_records: derive from the log when there is one,
-- otherwise use the manually entered numbers.

create view player_season_stats as
select
  p.id                                            as player_id,
  p.season_id,
  p.person_id,
  pe.name,
  p.number,
  p.position,
  p.year,
  p.captain,
  case when count(gs.id) > 0
       then (count(gs.id) filter (where gs.dressed))::int
       else p.gp end                              as gp,
  case when count(gs.id) > 0
       then coalesce(sum(gs.g), 0)::int
       else p.g end                               as g,
  case when count(gs.id) > 0
       then coalesce(sum(gs.a), 0)::int
       else p.a end                               as a,
  case when count(gs.id) > 0
       then coalesce(sum(gs.g + gs.a), 0)::int
       else p.g + p.a end                         as pts,
  case when count(gs.id) > 0
       then coalesce(sum(gs.pim), 0)::int
       else p.pim end                             as pim,
  coalesce(sum(gs.saves), 0)::int                 as saves,
  coalesce(sum(gs.goals_against), 0)::int         as goals_against,
  count(gs.id) > 0                                as from_box_scores
from players p
join people pe on pe.id = p.person_id
left join game_stats gs on gs.player_id = p.id
group by p.id, p.season_id, p.person_id, pe.name, p.number, p.position, p.year,
         p.captain, p.gp, p.g, p.a, p.pim;

create view player_career_stats as
select
  person_id,
  name,
  count(*)::int        as seasons,
  sum(gp)::int         as gp,
  sum(g)::int          as g,
  sum(a)::int          as a,
  sum(pts)::int        as pts,
  sum(pim)::int        as pim
from player_season_stats
group by person_id, name;
