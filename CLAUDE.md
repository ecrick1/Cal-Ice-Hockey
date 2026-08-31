# Cal Ice Hockey — Web Platform

Two-site platform for the Cal Ice Hockey club (UC Berkeley, ACHA II), sharing one Supabase project.

1. **`apps/web`** — public site. Read-only. Home/headlines, schedule & results, roster + player bio pages, stats, recruit interest form, news articles. Tickets is an external link (third-party ticketing), not a page we build.
2. **`apps/admin`** — private admin dashboard. Authenticated staff manage: news articles, roster (players, stats, bios, photos), schedule & results, seasons, and the recruit inbox.

## Reference implementation

`reference/cal-ice-hockey-app.jsx` is the working prototype. It is the **spec** for
visual design, page layouts, component structure, and the data model. Port its look
exactly: navy `#041E42`, gold `#FFC72C`, Inter, white Sidearm-style scoreboard cards,
pill buttons, flat SVG icons (no emojis), Cal script logo (`assets/logo.svg`).
The prototype's admin tabs define the admin app's screens.

## Stack

- Next.js 14+ App Router, TypeScript, both apps in one pnpm monorepo (`apps/web`, `apps/admin`, `packages/shared` for types + Supabase client + UI primitives).
- Supabase: Postgres, Auth (email magic link, admin app only), Storage (bucket `media` for player headshots + news images), Row Level Security as in `supabase/migrations/0001_init.sql`.
- Deploy: two Vercel projects from the monorepo (web + admin on separate domains, e.g. `calicehockey.com` and `admin.calicehockey.com`).
- Email notification on recruit submission: Resend free tier, triggered from the form's server action.

## Data rules

- The database is canonical. Public site reads with the anon key (RLS: public SELECT).
- All writes go through the admin app with an authenticated session. No service-role key in any client bundle.
- `recruits`: public may INSERT only (the form); only authenticated users may SELECT/DELETE.
- Records: a season's W-L-T/GF/GA is **computed from games with results**; `seasons.record_override` (jsonb) is used only when a season has no game log (imported historical records). Prototype has this logic — port it.
- Stats live as columns on `players` (gp, g, a, pim). Career view on a player page = sum across seasons matched by `players.name` (prototype behavior).

## Public site requirements (`apps/web`)

- Routes: `/` (headlines + record slab + recruit CTA), `/schedule`, `/roster`, `/roster/[playerId]`, `/stats`, `/news/[id]`, `/recruit`.
- Scoreboard strip on every page (recent finals + upcoming), built from `games`.
- "Tickets" nav pill = external `<a>` to `settings.tickets_url`. No tickets page.
- ISR (revalidate ~60s) or on-demand revalidation from admin writes; site must be fast and cacheable.
- Schedule PDF view and .ics "Add to Calendar" as in the prototype.

## Admin app requirements (`apps/admin`)

Screens (mirror prototype admin tabs, plus what the prototype faked):
- **News**: list, create/edit with date, tag, title, blurb, body (markdown), image upload.
- **Roster**: per-season player table editing all fields incl. GP/G/A/PIM, bio (markdown), headshot upload; add/delete player; copy roster from a previous season.
- **Schedule**: per-season game rows; "Final?" toggle switches time -> score entry; add/delete.
- **Seasons**: create season, set current, record_override editor for historical seasons.
- **Recruit inbox**: list submissions newest-first, expand details, delete; unread badge.
- **Settings**: tickets_url, contact email, home venue name.
- Bulk-paste importer (pipe/tab/comma) for schedule + roster — port from prototype.

## Phases (build in order; each phase ships)

1. Scaffold monorepo + Supabase schema + seed script (`scripts/seed.ts` loads the
   EliteProspects-derived data currently in the prototype's SEED_SITE).
2. Public site pages against the database.
3. Admin app: auth + all screens above.
4. Recruit form -> DB insert + Resend email to staff.
5. (Later, optional) EliteProspects API sync: Vercel Cron nightly upsert of roster/
   results for team 10366. EP fields (number, height, results) are sync-owned;
   admin fields (year, bio, photos, stats) are never overwritten by sync.

## Conventions

- No royal blue anywhere; navy #041E42 + gold #FFC72C + neutrals only.
- Buttons fully rounded (999px). Flat stroke SVG icons only.
- Never invent factual content (players, results, stats). Empty states over fake data.
- Keep components server-rendered where possible; client components only for interactivity.
