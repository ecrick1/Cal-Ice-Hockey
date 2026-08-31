-- Cal Ice Hockey — volunteer roles, and staff detail.
--
-- Volunteers stop being a list of people and become a list of openings: what a
-- student-run club needs help with, and how to offer it. Nobody visits that
-- page to read names — they visit it to find out whether they can be useful.

create table volunteer_roles (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  summary text not null default '',
  description text not null default '',
  -- "About 4 hours a week", "Home games only" — plain text, because the honest
  -- answer is rarely a number.
  commitment text not null default '',
  contact_email text not null default '',
  filled boolean not null default false,
  published boolean not null default true,
  sort int not null default 0,
  created_at timestamptz not null default now()
);

alter table volunteer_roles enable row level security;

create policy "public read volunteer roles" on volunteer_roles for select using (published = true);
create policy "admin all volunteer roles" on volunteer_roles for all
  using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');

-- ============================================================
-- Staff detail
-- ============================================================
-- The staff page gets its own layout, which needs more than a name and a title.

alter table coaches add column role_group text not null default 'coaching'
  check (role_group in ('coaching', 'operations', 'medical', 'other'));
alter table coaches add column since text not null default '';
alter table coaches add column phone text not null default '';
alter table coaches add column featured boolean not null default false;

comment on column coaches.role_group is 'Section on the staff page.';
comment on column coaches.featured is 'Leads the staff page — normally the head coach.';

-- The volunteer category is retired now that volunteers are roles, not people.
comment on column coaches.category is
  'Legacy split. Everyone here is staff; role_group drives the page sections.';
