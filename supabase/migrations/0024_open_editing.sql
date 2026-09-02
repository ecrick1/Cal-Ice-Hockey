-- Anyone who signs in may edit, and every version is kept so that can be undone.
--
-- The allow-list is removed by choice: editing should not wait on somebody
-- maintaining a list of addresses. What replaces it is not nothing, because
-- "anyone signed in" means anyone at all - the anon key is in the page, and
-- creating an account against it costs an email address.
--
-- So the protection moves from stopping a bad write to surviving one. Every
-- update keeps the version it replaced, with the account that made it and the
-- time. A site wiped at 2am is a single statement away from being back.

-- Who wrote it. Recorded by the database from the session rather than sent by
-- the client, so it is a fact rather than a claim.
alter table public.site_state
  alter column updated_by set default auth.uid();

create table if not exists public.site_state_history (
  id bigserial primary key,
  key text not null,
  value text not null,
  rev integer not null,
  -- Who and when this version was REPLACED, which is what you want when
  -- looking for the change that broke something.
  replaced_at timestamptz not null default now(),
  written_at timestamptz,
  written_by uuid
);

create index if not exists site_state_history_key_rev
  on public.site_state_history (key, id desc);

alter table public.site_state_history enable row level security;

-- Readable by anyone signed in, so an editor can see what changed and when.
-- Not public: it is the same content as the site, but the account ids are not
-- something to publish.
drop policy if exists "history readable by signed in" on public.site_state_history;
create policy "history readable by signed in"
  on public.site_state_history for select to authenticated using (true);

-- Written only by the trigger below, which runs as the table owner. No insert,
-- update or delete policy exists, so no client can forge or erase a version.

create or replace function public.keep_site_state_history()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.site_state_history (key, value, rev, written_at, written_by)
  values (old.key, old.value, old.rev, old.updated_at, old.updated_by);

  /* Four megabytes a version, so this is capped rather than kept forever.
     Twenty is far enough back to cover a bad night and small enough to sit
     inside a free database. */
  delete from public.site_state_history
  where id in (
    select id from public.site_state_history
    where key = old.key
    order by id desc
    offset 20
  );
  return new;
end $$;

drop trigger if exists site_state_keep_history on public.site_state;
create trigger site_state_keep_history
  before update on public.site_state
  for each row
  when (old.value is distinct from new.value)
  execute function public.keep_site_state_history();

-- The write policies, reduced to "you are signed in".
drop policy if exists "site_state written by admins" on public.site_state;
drop policy if exists "site_state updated by admins" on public.site_state;

drop policy if exists "site_state written by anyone signed in" on public.site_state;
create policy "site_state written by anyone signed in"
  on public.site_state for insert to authenticated with check (true);

drop policy if exists "site_state updated by anyone signed in" on public.site_state;
create policy "site_state updated by anyone signed in"
  on public.site_state for update to authenticated
  using (true) with check (true);

-- Still no delete policy. Losing the row drops every visitor back to the seed,
-- and nothing in the console needs to remove it.
