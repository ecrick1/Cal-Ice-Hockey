-- The prototype's whole site, in one row, so every visitor reads the same copy.
--
-- The prototype keeps its state as a single JSON document behind an async
-- get/set pair. Backed by localStorage that document is private to a browser,
-- which is why "Publish" only ever published to the person pressing it. This
-- table is the same document in a place everyone can see.
--
-- It is deliberately not the relational schema in the migrations either side
-- of this one. That schema is the real destination; this is the prototype's
-- own shape, stored as-is, so the working site can be shared without being
-- rewritten first. The two can coexist: nothing here touches those tables.

create table if not exists public.site_state (
  key text primary key,
  value text not null,
  -- Denormalised out of the document so a client can ask "is there anything
  -- new" without fetching four megabytes to find out.
  rev integer not null default 0,
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id) on delete set null
);

-- Who may write. An allow-list rather than "any authenticated user", because
-- anyone at all can create an account against a public anon key, and the
-- difference between a reader and an editor here is the whole site.
create table if not exists public.site_admins (
  email text primary key,
  note text not null default '',
  added_at timestamptz not null default now()
);

alter table public.site_state enable row level security;
alter table public.site_admins enable row level security;

-- The site is public: reading it is the point.
drop policy if exists "site_state readable by anyone" on public.site_state;
create policy "site_state readable by anyone"
  on public.site_state for select using (true);

-- Writing is for the allow-list. Checked against the signed-in identity in the
-- JWT, so it cannot be reached by editing anything the browser can see.
drop policy if exists "site_state written by admins" on public.site_state;
create policy "site_state written by admins"
  on public.site_state for insert to authenticated
  with check (exists (select 1 from public.site_admins a
                      where lower(a.email) = lower(auth.jwt() ->> 'email')));

drop policy if exists "site_state updated by admins" on public.site_state;
create policy "site_state updated by admins"
  on public.site_state for update to authenticated
  using (exists (select 1 from public.site_admins a
                 where lower(a.email) = lower(auth.jwt() ->> 'email')))
  with check (exists (select 1 from public.site_admins a
                      where lower(a.email) = lower(auth.jwt() ->> 'email')));

-- No delete policy: the site is edited, never deleted, and a missing row would
-- drop every visitor back to the seed.

-- The list itself is readable only by the people on it, so the club's staff
-- addresses are not published alongside the schedule.
drop policy if exists "site_admins visible to admins" on public.site_admins;
create policy "site_admins visible to admins"
  on public.site_admins for select to authenticated
  using (lower(email) = lower(auth.jwt() ->> 'email'));

-- Open tabs hear about a change instead of waiting to be reloaded.
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'site_state'
  ) then
    alter publication supabase_realtime add table public.site_state;
  end if;
end $$;
