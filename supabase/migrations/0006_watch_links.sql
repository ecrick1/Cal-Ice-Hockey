-- Cal Ice Hockey — live stream and replay links per game.
--
-- Two separate columns rather than one "video" field: they serve different
-- moments. The stream matters before and during a game, the replay only after,
-- and a game can have both — the same URL is rarely correct for each.

alter table games add column stream_url text not null default '';
alter table games add column replay_url text not null default '';

comment on column games.stream_url is
  'Live broadcast, shown on upcoming games. External link.';
comment on column games.replay_url is
  'Recording, shown once the game is final. External link.';
