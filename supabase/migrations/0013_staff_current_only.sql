-- Cal Ice Hockey — staff is current, not historical.
--
-- Staff were stored per season, which is wrong for how they are actually used:
-- a program has one staff list, and creating next season should not present
-- an empty one to be retyped. Nobody browses the 2019-20 equipment manager.
--
-- Renaming rather than recreating so the table keeps its policies and grants.
-- The table is empty, so nothing is lost either way.

alter table coaches rename to staff;
alter table staff drop column season_id;
alter table staff drop column category;

comment on table staff is
  'Current hockey operations staff. Not season-scoped — there is one list.';

-- The index and policies followed the rename; only the season index is stale.
drop index if exists coaches_category_idx;
drop index if exists coaches_season_idx;
