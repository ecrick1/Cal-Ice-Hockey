-- Cal Ice Hockey — per-theme opponent logos, and staff account profiles.

-- ============================================================
-- 1. Opponent logos for light and dark backgrounds
-- ============================================================
-- A single logo cannot serve both surfaces: most team marks are dark ink on
-- transparent, which disappears on the console's near-black, while a knocked-out
-- white version disappears on the public site's white cards. Store both and let
-- the renderer pick. Either may be null — the other is the fallback, and initials
-- are the fallback for both.

alter table opponents rename column logo_url to logo_light_url;
alter table opponents add column logo_dark_url text;

comment on column opponents.logo_light_url is 'For light backgrounds (public site cards).';
comment on column opponents.logo_dark_url  is 'For dark backgrounds (admin console, navy bands).';

-- ============================================================
-- 2. Staff profiles
-- ============================================================
-- One row per signed-in staff member, keyed to the Supabase auth user.
-- Auth itself (email, password, sessions) stays in auth.users and is managed
-- through the Supabase client — never mirrored here.

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  avatar_url text,
  -- Console preferences. Per-person, not per-site.
  density text not null default 'comfortable'
    check (density in ('comfortable', 'compact')),
  default_season_id uuid references seasons(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table profiles enable row level security;

-- A profile is private to its owner. Staff names shown publicly (news bylines)
-- are free text on the news row, so nothing here needs a public read policy.
create policy "read own profile"   on profiles for select using (auth.uid() = id);
create policy "insert own profile" on profiles for insert with check (auth.uid() = id);
create policy "update own profile" on profiles for update
  using (auth.uid() = id) with check (auth.uid() = id);

-- Signed-in staff should be able to see each other's names in the console
-- (e.g. "last edited by"), so allow authenticated reads of name/avatar only.
create policy "staff read profiles" on profiles for select
  using (auth.role() = 'authenticated');

-- ============================================================
-- 3. Create a profile automatically on signup
-- ============================================================
-- Without this, a newly invited staff member signs in and has no profile row,
-- so the console has nothing to show until they save one.

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'display_name', ''));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Backfill anyone who already exists.
insert into public.profiles (id, display_name)
select id, coalesce(raw_user_meta_data ->> 'display_name', '')
from auth.users
on conflict (id) do nothing;

-- ============================================================
-- 4. Keep updated_at honest
-- ============================================================

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_touch_updated_at on profiles;
create trigger profiles_touch_updated_at
  before update on profiles
  for each row execute function public.touch_updated_at();
