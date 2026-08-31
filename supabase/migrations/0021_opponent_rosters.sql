-- Cal Ice Hockey — opponent rosters, and the goaltender's baseline.
--
-- 1. Opponent rosters.
--
--    Entered once per team and reused every time you play them, so live
--    scoring offers a list instead of a text box and their box score comes out
--    with numbers and positions rather than bare names.
--
--    Deliberately thin — number, name, position. We are not tracking other
--    teams' players, only recording who did what in our games. That is also
--    why this is its own table rather than rows in `players`: those are people
--    the program is responsible for, with photos, bios and season stats.

create table if not exists opponent_players (
  id uuid primary key default gen_random_uuid(),
  opponent_id uuid not null references opponents(id) on delete cascade,
  number text not null default '',
  name text not null,
  position text not null default 'F' check (position in ('F', 'D', 'G')),
  created_at timestamptz not null default now()
);

create index if not exists opponent_players_opponent_idx on opponent_players (opponent_id, number);

alter table opponent_players enable row level security;

-- Public: their names appear in our published box scores, so hiding the list
-- that produces them would be pointless.
create policy "public read opponent players" on opponent_players for select using (true);
create policy "admin all opponent players" on opponent_players for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- 2. The netminder's baseline.
--
--    Saves and goals-against are derived from shots and goals rather than
--    entered: typing them next to a shot counter asks for two numbers that
--    have to agree. These record the shot and goal count when the current
--    goaltender came in, so a pulled goalie keeps what they faced and their
--    replacement starts from zero instead of inheriting the whole game.

alter table games add column if not exists live_net_base_shots int not null default 0;
alter table games add column if not exists live_net_base_goals int not null default 0;
