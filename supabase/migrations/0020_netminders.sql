-- Cal Ice Hockey — who is in net.
--
-- Ours references the roster; theirs is free text, same split as everywhere
-- else. 'empty' is a valid value for our side rather than a separate flag,
-- because an empty net is a choice about who is in goal, not a different kind
-- of thing.

alter table games add column if not exists live_goalie_us   text;  -- players.id, or 'empty'
alter table games add column if not exists live_goalie_them text not null default '';

comment on column games.live_goalie_us is
  'Our netminder during a live game: a players.id, the literal ''empty'' for an empty net, or null before anyone is set.';
