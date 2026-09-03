-- Asking the editors table who may read the editors table.
--
-- The previous migration gave site_admins a read policy of "you may see this
-- if you are in site_admins", which Postgres has to evaluate by reading
-- site_admins, which requires the policy, which reads site_admins. 42P17,
-- infinite recursion.
--
-- It was not only that table. site_state's write policies ask site_admins the
-- same question, so every save ran into the same recursion - and an UPDATE
-- whose policy errors or fails to match does not raise to the client, it
-- matches no rows. So publishing appeared to work and changed nothing, which
-- is the worst way for a permission check to fail.
--
-- The question is asked once, by a function that owns the answer.
-- SECURITY DEFINER runs it as the function's owner, for whom row-level
-- security on site_admins does not apply, so the lookup cannot re-enter the
-- policy that called it.

create or replace function public.is_editor()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.site_admins a
    where lower(a.email) = lower(nullif(auth.jwt() ->> 'email', ''))
  );
$$;

revoke all on function public.is_editor() from public;
grant execute on function public.is_editor() to authenticated;

-- Every policy that needs the answer now calls the function instead of
-- reaching into the table itself.

drop policy if exists "site_admins visible to editors" on public.site_admins;
create policy "site_admins visible to editors"
  on public.site_admins for select to authenticated
  using (public.is_editor());

drop policy if exists "site_state written by editors" on public.site_state;
create policy "site_state written by editors"
  on public.site_state for insert to authenticated
  with check (public.is_editor());

drop policy if exists "site_state updated by editors" on public.site_state;
create policy "site_state updated by editors"
  on public.site_state for update to authenticated
  using (public.is_editor()) with check (public.is_editor());

drop policy if exists "history readable by editors" on public.site_state_history;
create policy "history readable by editors"
  on public.site_state_history for select to authenticated
  using (public.is_editor());
