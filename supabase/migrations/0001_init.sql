-- Cal Ice Hockey — initial schema + row-level security
-- Run via: supabase db push  (or paste into the SQL editor)

create extension if not exists "pgcrypto";

-- ---------- Tables ----------

create table seasons (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,              -- "2025-26"
  is_current boolean not null default false,
  record_override jsonb,                  -- {w,l,t,gf,ga,note} for seasons with no game log
  created_at timestamptz not null default now()
);

create table players (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id) on delete cascade,
  number text not null default '',
  name text not null,
  position text not null check (position in ('F','D','G')),
  shoots text not null default '',        -- 'L' | 'R' | ''
  year text not null default '',          -- class: Fr/So/Jr/Sr/Grad or ''
  height text not null default '',
  hometown text not null default '',      -- "City, ST · Prior Team"
  bio text not null default '',           -- markdown-ish (# headers, - bullets)
  photo_url text,
  gp int not null default 0,
  g int not null default 0,
  a int not null default 0,
  pim int not null default 0,
  ep_player_id int unique,                -- EliteProspects id (sync key), nullable
  created_at timestamptz not null default now()
);
create index players_season_idx on players(season_id);

create table games (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id) on delete cascade,
  date date,
  opponent text not null default '',
  home_away text not null default 'H' check (home_away in ('H','A')),
  venue text not null default '',
  time text not null default '',
  score_us int,                           -- null score_us => not final
  score_them int,
  ot boolean not null default false,
  ep_game_id int unique,
  created_at timestamptz not null default now()
);
create index games_season_idx on games(season_id);

create table coaches (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id) on delete cascade,
  name text not null,
  title text not null default '',
  email text not null default '',
  bio text not null default '',
  photo_url text,
  sort int not null default 0
);

create table news (
  id uuid primary key default gen_random_uuid(),
  date date not null default current_date,
  tag text not null default 'NEWS',
  title text not null,
  blurb text not null default '',
  body text not null default '',          -- markdown, rendered on /news/[id]
  image_url text,
  published boolean not null default true,
  created_at timestamptz not null default now()
);

create table recruits (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null,
  grad_year text not null default '',
  position text not null default '',
  shoots text not null default '',
  height text not null default '',
  current_team text not null default '',
  gpa text not null default '',
  highlight_link text not null default '',
  message text not null default '',
  read boolean not null default false,
  created_at timestamptz not null default now()
);

create table settings (
  key text primary key,                   -- 'tickets_url' | 'contact_email' | 'home_venue'
  value text not null default ''
);
insert into settings (key, value) values
  ('tickets_url', ''), ('contact_email', ''), ('home_venue', 'Oakland Ice Center');

-- ---------- Row Level Security ----------
-- Public: read everything except recruits; insert recruits only.
-- Authenticated (admin app users): full write.

alter table seasons  enable row level security;
alter table players  enable row level security;
alter table games    enable row level security;
alter table coaches  enable row level security;
alter table news     enable row level security;
alter table recruits enable row level security;
alter table settings enable row level security;

-- public read
create policy "public read seasons"  on seasons  for select using (true);
create policy "public read players"  on players  for select using (true);
create policy "public read games"    on games    for select using (true);
create policy "public read coaches"  on coaches  for select using (true);
create policy "public read news"     on news     for select using (published = true);
create policy "public read settings" on settings for select using (true);

-- public recruit submission (insert only; no read)
create policy "public submit recruit" on recruits for insert with check (true);

-- authenticated full access
create policy "admin all seasons"  on seasons  for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all players"  on players  for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all games"    on games    for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all coaches"  on coaches  for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all news"     on news     for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all recruits" on recruits for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
create policy "admin all settings" on settings for all using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- ---------- Storage ----------
-- Create bucket 'media' (public read) in the dashboard or:
-- insert into storage.buckets (id, name, public) values ('media','media', true);
-- Policies: public read; authenticated insert/update/delete.

-- ---------- Helper view: season records ----------
create view season_records as
select
  s.id as season_id,
  s.name,
  count(g.id) filter (where g.score_us is not null)                                as gp,
  count(g.id) filter (where g.score_us > g.score_them)                             as w,
  count(g.id) filter (where g.score_us < g.score_them)                             as l,
  count(g.id) filter (where g.score_us is not null and g.score_us = g.score_them)  as t,
  coalesce(sum(g.score_us)  filter (where g.score_us is not null), 0)              as gf,
  coalesce(sum(g.score_them) filter (where g.score_us is not null), 0)             as ga
from seasons s
left join games g on g.season_id = s.id
group by s.id, s.name;
