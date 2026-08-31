-- Cal Ice Hockey — the other team's box score.
--
-- Deliberately NOT modelled as people/players rows. We would have to maintain a
-- roster for every opponent in the league, kept current all season, to record
-- three names off a scoresheet. Instead each line carries the name as written
-- on the sheet — which is all a visiting scorer's summary gives you anyway.
--
-- The consequence, and it is the right trade: opponent players have no career
-- totals and no player pages. They are game records, not people we track.

create table opponent_game_stats (
  id uuid primary key default gen_random_uuid(),
  game_id uuid not null references games(id) on delete cascade,
  name text not null,
  number text not null default '',
  is_goalie boolean not null default false,
  g int not null default 0,
  a int not null default 0,
  pim int not null default 0,
  saves int,
  goals_against int,
  minutes numeric(5,1),
  sort int not null default 0,
  created_at timestamptz not null default now()
);
create index opponent_game_stats_game_idx on opponent_game_stats(game_id);

alter table opponent_game_stats enable row level security;

create policy "public read opponent stats" on opponent_game_stats for select using (true);
create policy "admin all opponent stats" on opponent_game_stats for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

comment on table opponent_game_stats is
  'Opposition scoring summary per game. Names are free text, not roster rows.';
