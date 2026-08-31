-- Cal Ice Hockey — an opponent's home rink.
--
-- Scheduling an away game meant typing the same rink name every time, and
-- getting it subtly different each time ("Sharks Ice" / "Sharks Ice at San
-- Jose"). The rink belongs to the opponent, so it lives on the opponent.
--
-- The console fills games.venue from this when the opponent or the home/away
-- side changes, but only while the field still holds whatever was filled in
-- last time. A venue typed by hand is never overwritten — neutral-site and
-- one-off rinks are exactly the case that has to keep working.

alter table opponents add column if not exists home_venue text not null default '';

comment on column opponents.home_venue is
  'Where this team plays at home. Prefills games.venue for away games; never overwrites a hand-entered venue.';
