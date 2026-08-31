-- Cal Ice Hockey — staff categories and prospects.
--
-- "Coaches" was too narrow: a club program runs on hockey operations staff
-- (coaches, GM, equipment, trainers) plus volunteers (parents, alumni, team
-- managers). They belong on separate pages but are the same kind of record.

alter table coaches add column category text not null default 'hockey_ops'
  check (category in ('hockey_ops', 'volunteer'));

comment on column coaches.category is
  'hockey_ops = coaching and operations staff; volunteer = supporting roles.';

create index coaches_category_idx on coaches(season_id, category);

-- ============================================================
-- Prospects
-- ============================================================
-- Committed players who have not yet joined a roster. Deliberately NOT rows in
-- `people`: a prospect may never arrive, and a career-stats key for someone who
-- never played would be misleading. When one enrols, a person row is created
-- and the prospect is marked converted rather than deleted, so the commitment
-- history survives.

create table prospects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  position text not null default '' check (position in ('F', 'D', 'G', '')),
  shoots text not null default '',
  height text not null default '',
  weight text not null default '',
  hometown text not null default '',
  high_school text not null default '',
  prior_team text not null default '',
  -- The academic year they are expected to arrive, e.g. "2026-27".
  arriving_season text not null default '',
  committed_on date,
  note text not null default '',
  photo_url text,
  -- Set when they turn up on a roster; the record stays for the history.
  converted_person_id uuid references people(id) on delete set null,
  published boolean not null default true,
  sort int not null default 0,
  created_at timestamptz not null default now()
);

alter table prospects enable row level security;

create policy "public read prospects" on prospects for select using (published = true);
create policy "admin all prospects" on prospects for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

comment on table prospects is
  'Committed future players. Not people rows until they actually arrive.';
