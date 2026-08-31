-- Cal Ice Hockey — manual ordering, and volunteer roles that are simply open.
--
-- 1. A listed volunteer role is an open volunteer role.
--
--    filled/published were two flags answering the same question badly. A role
--    that is covered gets deleted; a role that should not be seen was never
--    posted. Dropping both removes a state nobody could describe out loud
--    ("published but filled") and makes the public list identical to the
--    console list, which is what an editor assumes anyway.

--    The policy has to go first: it reads `published`, so dropping the column
--    underneath it is refused.

drop policy if exists "public read volunteer roles" on volunteer_roles;

alter table volunteer_roles drop column if exists filled;
alter table volunteer_roles drop column if exists published;

create policy "public read volunteer roles" on volunteer_roles for select using (true);

-- 2. Opponents get a manual order.
--
--    Alphabetical is the wrong default for a picker you use forty times a
--    season: the teams you actually play belong at the top. volunteer_roles
--    already had `sort`; this brings opponents in line.

alter table opponents add column if not exists sort int not null default 0;

create index if not exists opponents_sort_idx on opponents (sort, name);

-- 3. Where the interest form goes.
--
--    settings is key/value, so this needs no DDL — recorded here so the keys
--    are documented in one place with the rest of the schema:
--
--      recruit_mode      'inbox' | 'email' | 'link'   (default 'inbox')
--      recruit_email     address for 'email' mode; falls back to contact_email
--      recruit_form_url  external form for 'link' mode; blank restores the
--                        built-in form, so a bad paste cannot strand the page
