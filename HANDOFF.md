# Handoff — Cal Ice Hockey site

Written 2026-09-29, updated 2026-09-30. For picking this project back up
under a different account, or on a different machine entirely — both are
covered below, and they're different problems with different answers.

## What this is

A React prototype for the Cal Ice Hockey club (UC Berkeley, ACHA II) —
schedule, roster, stats, live scoring console, news, recruit form, and now
an admin console for managing who else can edit it. One 24k-line JSX file
compiled to a single bundle, backed by a shared Supabase database so edits
reach every visitor live. See `CLAUDE.md` at the repo root for the full
architecture spec (this doc is about *state and history*, not the spec).

**Nothing here is tied to any Claude account.** The code is a git repo
(now with a real GitHub remote — see below), the site is deployed on
Vercel, the data lives in Supabase.

## Where things live

| What | Where | Notes |
|---|---|---|
| Source | `reference/cal-ice-hockey-app.jsx` | the whole app, one file |
| Dev bundle build | `prototype/build.mjs` → `prototype/app.js` | esbuild |
| Production build | `prototype/dist.mjs` → `dist/` | static export for Vercel |
| Deploy | `cd dist && npx.cmd vercel --prod --yes` | see gotchas below |
| Live site | `cal-ice-hockey.vercel.app` | **currently behind Vercel's own login wall — see Urgent, below** |
| GitHub | `github.com/ecrick1/Cal-Ice-Hockey` | **public** — checked clean of secrets and of recruit/alumni PII before pushing |
| Database | Supabase, table `site_state`, key `cal-hockey-site` | one JSON blob, `rev` column |
| Secrets | `.env.local` (gitignored, **not in git, not on any other machine**) | service-role key, `DATABASE_URL`, Resend key, Supabase URL/anon key |
| Scripts | `scripts/*.mjs` | diagnostics, restore, push, user management — read the top-of-file comment on each before running |

## Urgent — fix this first

**Vercel's own Deployment Protection ("Vercel Authentication") is on for
this project**, and it is actively breaking real sign-in attempts right
now: Supabase correctly hands back a valid session, the browser lands on
`cal-ice-hockey.vercel.app` with the token, and *Vercel itself* redirects
that to `vercel.com/login` before the app ever runs. This has nothing to
do with Supabase config, RLS, or anything in this codebase — it's a
Vercel project setting, dashboard-only (no CLI command for it; checked).

Ordinary page visits are fine **for now**, only because they're being
served from a CDN cache (`X-Vercel-Cache: HIT`) that predates whatever
turned this on — that cache will eventually go stale, and what happens
then is untested.

**Fix:** vercel.com → the project → Settings → Deployment Protection →
turn off Vercel Authentication (or at least exclude Production). A public
club site should never require a Vercel account to view.

## Working from a second machine

The GitHub remote makes this straightforward — clone the code, then
handle the one thing that deliberately isn't in git.

```bash
git clone https://github.com/ecrick1/Cal-Ice-Hockey.git
cd Cal-Ice-Hockey
cp .env.example .env.local   # then fill in the real values below
cd prototype && npm install
```

`.env.local` needs, at minimum:
- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` — safe to
  embed in a client bundle, but still not committed, by convention
- `SUPABASE_SERVICE_ROLE_KEY` — bypasses RLS entirely; this is the one
  that matters. Get it from Supabase dashboard → Project Settings → API.
- `DATABASE_URL` — Supabase → Project Settings → Database → Connection
  string (the pooler one, not direct)
- `RESEND_API_KEY` — not currently set up anywhere (see Open items)

None of this should ever go through git, chat, or email in plain text.
Copy it machine-to-machine by hand (USB drive, a password manager's
secure-note feature, or retype it from the two dashboards above).

Then, from the repo root:
```bash
node prototype/build.mjs      # builds the dev bundle
```
and use whatever this machine's equivalent of the Browser-pane preview
setup is to serve `prototype/` locally and check it.

**To deploy from this machine**, `cd dist && npx vercel login` — that's
an interactive step the person at the keyboard does themselves; nothing
here should authenticate as them. First deploy will ask to link the
Vercel project (say yes to the existing `cal-ice-hockey` project, don't
create a new one). After that, `cd dist && npx vercel --prod --yes` same
as always. **Vercel's CLI exit code lies about success** — see Gotchas.

## Current state (as of this update)

- Git: `master`, 208 commits, working tree clean, remote is the public
  GitHub repo above.
- Database: rev **650**.
- Deploy: live bundle verified byte-identical to a build from committed
  source as of the last push — but see **Urgent** above; "deployed
  correctly" and "reachable by a real visitor" are not currently the same
  claim.
- `git log --oneline` commit messages are full prose explaining *why*,
  not just *what* — read them before asking what changed recently.

## Big things built, roughly in order

1. **Storage moved from `localStorage` to shared Supabase** — the whole
   reason edits reach every visitor now instead of just one browser.
2. **Realtime + coalesced writes**, history kept only when the previous
   version is >60s old.
3. **Live-scoring clock lag** (10s) so the public feed doesn't jump
   backwards on a stop.
4. **Automatic image compression** on every upload path — WebP, 25MB
   source ceiling, SVGs pass through untouched.
5. **Favicon editor** — separate light/dark uploads. *Known weak spot:
   the Cal script wordmark is right at the edge of legibility at 16px.*
6. **A run of CSS/layout bugs**, all the same root cause: a media query
   carries no specificity of its own, so a rule written after it wins.
   Recurring enough in this codebase that it's worth checking rule order
   first, before anything else, when something looks unstyled.
7. **A sync bug**: a browser could end up believing its local copy was
   *ahead* of the database and never fetch again. Fixed by tracking "did
   a write actually fail" as its own flag.
8. **News recap generation** for 2024-25 and 2025-26 (52 articles;
   location dateline, byline `CalIceHockey.com`, linked players, varied
   prose). **The generator script was never committed** — it only ever
   existed as scratch files. Regenerating recaps later means rewriting it.
9. **~90 YouTube replay links**, matched by verifying date *and* opponent
   independently, never one alone.
10. **Admin roles.** `site_admins` gained a `role` column (admin/editor —
    migration `0030_admin_role.sql`). A new console screen
    (`api-manage-users.mjs`, a Vercel serverless function holding the
    service-role key server-side) lets an admin add, remove, and promote
    or demote other editors, re-checking on every single call that the
    caller is currently an admin — not that they were one when they
    signed in. The first version used the public site's light table
    styling with no dark-console override; rebuilt with the same `.card`
    pieces the Sponsors screen already used correctly.
11. **Blank avatars get a color.** A player with no headshot used to get
    the same flat gray silhouette as every other player with no
    headshot — unreadable across a whole roster. Now hashed from the
    player's own id, so the same person is the same color everywhere
    they appear, across all fourteen places this file draws a photo.

## Open items — found but not fixed

**Vercel Deployment Protection** — see Urgent, above. This is the one
that actually matters right now.

**Schedule gaps** (a real broadcast exists, no matching game in the data):
- A 2016-17 Cal-vs-Washington game (Pac-8 tournament, PAC-8's channel).
- 2022-11-10 "Big Freeze vs Stanford" + a same-day Santa Clara game,
  Cal's own channel.
- A January 2017 UCLA weekend (1/20, 1/21), Cal's own channel.
- A 2015 Pac-8 tournament game at Lake Tahoe (dead video, low priority).

**Date/opponent mismatches** — a video's date doesn't match who the
schedule says Cal played that day. Left unlinked rather than guessed:
- "U of Utah" (Cal's channel), 2022-01-28 and 2022-01-16 — schedule shows
  San Jose State and Santa Clara those dates.
- "Cal vs USC," 2019-11-15 — schedule shows Stanford.
- "Cal vs. Davis," 2016-11-04 — schedule shows Washington.
- Two UW videos say "10/7/17 vs Cal"; schedule only has 10/6/17.

**No play-by-play at all**: every game 2010-11 through 2019-20 (133
games) has a final score and nothing else — no recap possible without
someone reconstructing the play log by hand.

**No YouTube channel found**: San Jose State, UCLA, Washington State, UC
San Diego, Santa Clara, UC Davis. USC's channel exists but is exhausted.

**Standing, never built**:
- Recruit submissions still stored browser-local — need their own
  Supabase table with public-INSERT-only RLS before centralizing.
- `RESEND_API_KEY` isn't set anywhere — recruit-form email notifications
  and auth-email custom SMTP both need it, neither is wired up. Discussed
  and deliberately deferred: needs a verified sending domain (or a
  subdomain of one already owned) before it's worth doing.
- Supabase dashboard: confirm "Allow new users to sign up" is off.
- `http://localhost:3002` isn't in the Supabase redirect allow-list, so
  the *link* half of sign-in doesn't work against local dev — the *code*
  half does (doesn't depend on a redirect at all).
- `calicehockey.net` is a **different, unrelated site** — don't confuse
  it with this project.

## Gotchas that cost time, so you don't re-learn them

- **Vercel CLI exit codes lie.** Verify a deploy by diffing the served
  `app.js` byte-for-byte against the local build — `cmp -s live.js
  prototype/app.js` — never by trusting the CLI's own status line.
- **YouTube's oembed endpoint 401s for videos with embedding disabled**,
  identical-looking to "video was deleted." Fetch the watch page HTML and
  check `"status":"OK"` before concluding a link is dead.
- **`npx.ps1` is blocked by PowerShell execution policy** on the original
  machine — use `npx.cmd`, don't change the policy.
- **Never run heavy DB diagnostics against the live database**, especially
  mid-game — `db-diag.mjs` once made the site unloadable for 30 seconds.
  `db-size.mjs` is the safe replacement.
- **An open console tab holds a stale local copy.** Reload it before
  editing data via script, or its next save can overwrite your change.
- **A rate-limited sign-in silently drops the code, keeps the link.**
  Supabase caps how often one address can get a new code; ask again too
  soon and the reply has a working link but no `email_otp`. Fixed to warn
  about this explicitly (`scripts/signin-link.mjs`) rather than stay quiet.
- Splitting one file's interleaved changes into separate commits needs
  `git add -p`, which needs real interactive input — doesn't work from an
  automated shell. When two unrelated changes land in the same giant
  file in the same sitting, be honest in the commit message that it's two
  things, rather than force a fake split or a fake single narrative.
- Git commits end with attribution lines per whatever the standing
  instruction is *at the time* — check the most recent commit's sign-off
  and match its style rather than assuming it hasn't changed.

## If you only read one section

Read `CLAUDE.md` for the spec, skim `git log --oneline` for what's
already built, fix **Urgent** before anything else, and check **Open
items** before starting new work — several of these will look like new
bugs if you rediscover them without knowing they're already-known gaps.
