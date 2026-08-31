-- Cal Ice Hockey — where a game is played, shots on goal, opponent assists.
--
-- 1. Location.
--
--    The public schedule used to print "Road" for every away game, which is
--    not a place. A rink belongs to the opponent, and so does the town it is
--    in, so both live on the opponent and prefill the game. Either can be
--    overwritten on the game for a neutral site.

alter table games      add column if not exists location  text not null default '';
alter table opponents  add column if not exists home_city text not null default '';

comment on column games.location is
  'City and state, e.g. "Dallas, TX". Prefilled from opponents.home_city for away games and settings.home_city for home games; a hand-entered value is never overwritten.';

-- settings is key/value, so the home city needs no DDL. Recorded here so the
-- key is documented alongside the schema.
insert into settings (key, value) values ('home_city', '')
  on conflict (key) do nothing;

-- 2. Shots on goal.
--
--    A team counter, not a per-player one. Nobody at a club game is tracking
--    who took which shot, but the shot count is on every scoreboard in the
--    building.

alter table games add column if not exists live_shots_us   int not null default 0;
alter table games add column if not exists live_shots_them int not null default 0;

-- 3. Opponent assists.
--
--    Our assists reference players(id) so a live goal writes straight through
--    to the box score. We do not keep other teams' rosters, so theirs are
--    names, exactly as opponent_game_stats already does.

alter table game_plays add column if not exists assist_names text[] not null default '{}';

comment on column game_plays.assist_ids is
  'Our assists, linked to players so live entry updates the box score.';
comment on column game_plays.assist_names is
  'The opponent''s assists. Free text: we do not keep other teams'' rosters.';
