-- A second tier: who can edit the site, and who can decide who can edit it.
--
-- Until now everyone on site_admins was equal - the only question a write
-- ever asked was "is this address on the list at all". Managing that list
-- was deliberately kept out of the browser entirely (scripts/users.mjs,
-- run from a machine holding the service-role key) precisely because a
-- mistake there hands somebody the whole site.
--
-- Putting a user screen in the console needs a narrower question: not "can
-- this person edit," but "can this person hand editing to someone else."
-- That is a new fact about a row, not a new table - role, alongside email.

alter table public.site_admins
  add column if not exists role text not null default 'editor'
    check (role in ('admin', 'editor'));

-- Assign admins explicitly during setup; migrations do not grant named accounts access.

comment on column public.site_admins.role is
  'admin: can also add, remove, and promote/demote other editors. '
  'editor: can save site content, nothing about who else can.';
