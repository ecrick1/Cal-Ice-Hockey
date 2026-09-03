-- Editing is by invitation again, and the invitation list is the whole gate.
--
-- Open editing was tried and is being reversed on purpose. "Anyone signed in"
-- meant anyone could ask for an account against a key that is printed in the
-- page - so anyone could make the site email them, and anyone who did could
-- then write. The history table made that survivable rather than safe, and
-- surviving vandalism is a poor substitute for not inviting it.
--
-- site_admins is the list. Being on it is what permits a write; it is not a
-- claim the client makes, so nothing the browser can edit affects it.

-- An editor can see who else can edit. It is a club roster, not a secret, and
-- someone who cannot see the list cannot notice a name on it that should not
-- be.
drop policy if exists "site_admins visible to admins" on public.site_admins;
create policy "site_admins visible to editors"
  on public.site_admins for select to authenticated
  using (exists (select 1 from public.site_admins a
                 where lower(a.email) = lower(auth.jwt() ->> 'email')));

-- Adding and removing editors is deliberately NOT possible from the browser.
-- Granting access is the one action where a mistake hands the site away, and
-- it is rare enough to be worth a deliberate step from a machine holding the
-- service key. scripts/users.mjs is that step. No insert, update or delete
-- policy exists here, so the anon and authenticated roles cannot write this
-- table at all.

-- Writes to the site go back to the list.
drop policy if exists "site_state written by anyone signed in" on public.site_state;
drop policy if exists "site_state updated by anyone signed in" on public.site_state;

drop policy if exists "site_state written by editors" on public.site_state;
create policy "site_state written by editors"
  on public.site_state for insert to authenticated
  with check (exists (select 1 from public.site_admins a
                      where lower(a.email) = lower(auth.jwt() ->> 'email')));

drop policy if exists "site_state updated by editors" on public.site_state;
create policy "site_state updated by editors"
  on public.site_state for update to authenticated
  using (exists (select 1 from public.site_admins a
                 where lower(a.email) = lower(auth.jwt() ->> 'email')))
  with check (exists (select 1 from public.site_admins a
                      where lower(a.email) = lower(auth.jwt() ->> 'email')));

-- The version history stays. Being invited does not make somebody careful,
-- and an accident by an editor is the likelier reason to need it now.
drop policy if exists "history readable by signed in" on public.site_state_history;
create policy "history readable by editors"
  on public.site_state_history for select to authenticated
  using (exists (select 1 from public.site_admins a
                 where lower(a.email) = lower(auth.jwt() ->> 'email')));

-- The account actually used to sign in, added alongside the one that was
-- listed. Both belong to the same person; the list had the address on file
-- rather than the address that reached the console.
insert into public.site_admins (email, note)
values ('ethanjcrick@gmail.com', 'signed in 2026-09-03')
on conflict (email) do nothing;
