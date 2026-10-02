# Deploying Cal Ice Hockey from this workspace

The current website is `reference/cal-ice-hockey-app.jsx`, bundled by
`prototype/build.mjs` and packaged by `prototype/dist.mjs`. The Next.js apps
in `apps/` are separate scaffolding and are not the current production site.

## Existing deployment

- Vercel team: `cal-ice-hockey`
- Vercel project: `cal-ice-hockey`
- Project ID: `prj_Y3JbN8231ri1wK7wBpR53YippxBh`
- Public URL: https://cal-ice-hockey.vercel.app
- Supabase project: `mdwbudjoerjczemaxcjo`
- Source repository: https://github.com/ecrick1/Cal-Ice-Hockey

These identities were checked in the signed-in dashboards on September 29,
2026. Vercel shows no Git integration. The imported ZIP does not include Git
history; this workspace has a new, empty Git repository. Do not force-push it
over the existing remote repository.

## Connection settings

The browser bundle needs only these public values in a root `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://mdwbudjoerjczemaxcjo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<existing public anon key>
```

The file is ignored by Git. The private `SUPABASE_SERVICE_ROLE_KEY` belongs
in Vercel's server environment for the manage-users API; it must never be
embedded in the browser bundle. Confirm the existing server environment
contains all three variables before deploying.

With Supabase configured, authenticated admin content edits can affect the
live database immediately, even from localhost. Code edits still require a
Vercel deployment. Without Supabase settings the preview uses localStorage.

## Preparation status

- Public Supabase key is configured in the git-ignored .env.local.
- A read-only Supabase request verified and saved revision 650 (17 seasons, 387 games, 67 articles) in data/backup-2026-09-29/site.json.
- Production bundle and static packaging passed with revision 650.
- Vercel CLI 61.0.0 is authenticated; dist/ is linked to the existing project.
- Production environment variable names were verified, including the server-side service-role key; secret values were not retrieved for this check.
- Connected preview is running at http://localhost:3003.
- No deployment or database write has been performed during preparation.
- Hosted preview and serverless-function checks remain part of release verification.

## Build and deploy

From the project root, with Node and pnpm on PATH:

```
pnpm run build:site
```

This creates `dist/` with the browser bundle, public assets, public site data,
route configuration, and the three serverless functions. Only deploy `dist/`.
Do not deploy the entire source folder or use the monorepo's `build` command.

Authenticate the Vercel CLI, then link the existing project from `dist/`:

```
cd dist
vercel login
vercel link --project cal-ice-hockey --scope cal-ice-hockey
vercel deploy
```

Review the preview's homepage, schedule, roster, news, direct route reloads,
Supabase reads, and server functions. Confirm `/version.json` matches the
verified public data snapshot. Test admin writes only when explicitly intended
to affect live data. Preview deployments also use production data if configured
with the production Supabase project.

When the user asks to publish:

```
vercel deploy --prod
```

Verify the production domain serves the expected bundle and data revision.
The packaging script preserves `dist/.vercel/` across rebuilds. Vercel's
existing deployment history provides the rollback path for code; a code
rollback does not undo database edits.

## Password setup and temporary mail configuration

Supabase custom SMTP was disabled with the owner's approval on 2026-09-29.
Resend had rejected mail because calicehockey.com was not verified. Supabase's
built-in sender is now active, limited to project team addresses and two emails
per hour; switching reset custom email templates. Configure a verified sender
and restore appropriate templates when the domain is available.

The live app handles PASSWORD_RECOVERY sessions by opening the password setup
form in the admin view. Recovery emails should explicitly redirect to
https://cal-ice-hockey.vercel.app/admin, which is within the existing allowlist.
The dashboard's default Site URL still references an older Vercel alias.
A recovery email was requested for the owner's confirmed Gmail account;
password entry and saving are performed by the owner, not the assistant.
