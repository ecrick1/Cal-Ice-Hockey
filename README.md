# Cal Ice Hockey — Build Kickoff

Two sites, one Supabase database:
- apps/web    -> public site (read-only, fast, ISR)
- apps/admin  -> staff dashboard (magic-link auth; news, roster, stats, schedule, seasons, recruit inbox, settings)

Tickets: external third-party link (settings.tickets_url) — no tickets page is built.

## What's in this folder
- CLAUDE.md                          -> project brief for Claude Code (start here)
- supabase/migrations/0001_init.sql  -> schema + RLS policies + season_records view
- reference/cal-ice-hockey-app.jsx   -> working prototype = design + behavior spec
- assets/logo.svg                    -> Cal script logo

## Build order (each phase ships)
1. pnpm monorepo scaffold + `supabase db push` + seed script from prototype SEED_SITE
2. Public site pages
3. Admin app (auth + screens)
4. Recruit form -> insert + Resend email notification
5. Optional later: EliteProspects API nightly sync (team 10366) — request a key at
   developer.eliteprospects.com; current season tier is free. Sync owns EP fields
   (numbers/heights/results); admins own year/bios/photos/stats.

## First Claude Code prompt
"Read CLAUDE.md and reference/cal-ice-hockey-app.jsx. Execute Phase 1: scaffold the
monorepo, apply the migration, and write scripts/seed.ts that loads SEED_SITE from
the reference file into Supabase. Then stop for review."

---

## Getting started (after Phase 1 scaffold)

Prerequisites: Node 20+ and pnpm (`npm i -g pnpm`).

### 1. Create the Supabase project

Do this yourself at [supabase.com](https://supabase.com) — sign in, **New project**,
pick the `us-west-1` region (closest to Berkeley), and save the database password.

Then from **Project Settings -> API** copy three values:

| Supabase field       | Goes in `.env.local` as          |
| -------------------- | -------------------------------- |
| Project URL          | `NEXT_PUBLIC_SUPABASE_URL`       |
| `anon` `public` key  | `NEXT_PUBLIC_SUPABASE_ANON_KEY`  |
| `service_role` key   | `SUPABASE_SERVICE_ROLE_KEY`      |

```
cp .env.example .env.local
```

The `service_role` key bypasses RLS. It belongs only in `.env.local` (git-ignored)
and in Vercel's server-side env vars — never in a client component.

### 2. Apply the schema

Either paste `supabase/migrations/0001_init.sql` into the Supabase SQL editor, or:

```
pnpm dlx supabase link --project-ref YOUR-PROJECT-REF
pnpm db:push
```

Then create the Storage bucket `media` (public read) under **Storage -> New bucket**.

### 3. Seed and run

```
pnpm install
pnpm seed
pnpm dev:web     # http://localhost:3000
pnpm dev:admin   # http://localhost:3001
```

`pnpm seed` is idempotent. `pnpm seed -- --reset` wipes seasons and news first.

## Repo layout

```
apps/web              public site (Next 15 App Router, ISR 60s)
apps/admin            staff dashboard (dynamic, magic-link auth in Phase 3)
packages/shared       row types, record computation, Supabase client factories, theme.css
scripts/seed.ts       loads the prototype's SEED_SITE into Supabase
supabase/migrations   schema + RLS
reference/            the prototype — design and behavior spec
```

### Which Supabase client to use

| Import                          | Key          | Use for                                     |
| ------------------------------- | ------------ | ------------------------------------------- |
| `@cal/shared/supabase/public`   | anon         | all `apps/web` reads (no cookies -> ISR works) |
| `@cal/shared/supabase/server`   | anon + session | admin server components and actions       |
| `@cal/shared/supabase/browser`  | anon + session | admin client components                   |
| `@cal/shared/supabase/admin`    | service_role | node scripts only — bypasses RLS            |
