-- Cal Ice Hockey — situational scoring, and the names a program goes by.
--
-- Deliberately limited to stats a club team can actually capture from a
-- scoresheet: power play, short handed, game winner. Face-offs, blocks, hits
-- and time on ice need a scorekeeper with a tablet and nobody at this level
-- has one, so a column for them would sit permanently empty.

alter table game_stats add column ppg int not null default 0;
alter table game_stats add column shg int not null default 0;
-- A single flag per game rather than a count: only one goal can win it.
alter table game_stats add column gwg boolean not null default false;
-- Shots are on the scoresheet and are the one volume stat worth having.
alter table game_stats add column shots int not null default 0;

comment on column game_stats.ppg is 'Power play goals. Subset of g.';
comment on column game_stats.shg is 'Short handed goals. Subset of g.';
comment on column game_stats.gwg is 'This player scored the game winner.';

-- Goalie minutes, so goals-against average is real rather than per-appearance.
alter table game_stats add column minutes numeric(5,1);
comment on column game_stats.minutes is 'Goaltender minutes played, for GAA.';

-- ============================================================
-- Program names
-- ============================================================
-- Three names, because a program is written differently depending on where
-- it appears: "Cal Ice Hockey" in navigation, "California Golden Bears Ice
-- Hockey" on a printed schedule, and just "California" on a scorebug next to
-- the opponent. Same pattern as "Canadiens" / "Montréal Canadiens" / "MTL".

insert into settings (key, value) values
  ('org_game_name', 'California'),
  ('org_abbr', 'CAL')
on conflict (key) do nothing;
