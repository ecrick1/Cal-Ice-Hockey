# Set up your own Supabase project

This guide is for a **new, empty Supabase project**. It does not copy production
accounts or change the Cal production project. Admin saves write directly to the
configured database, even when the website runs on localhost.

## 1. Install and configure

Install Node.js 22+ and the pnpm version in the root `package.json`, then run
from the repository root:

```sh
pnpm install
cp .env.example .env.local
```

Create your own project in the Supabase dashboard. Fill in these variables in
`.env.local` (already ignored by Git):

| Variable | Value / purpose |
| --- | --- |
| `NEXT_PUBLIC_SUPABASE_URL` | Your project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your publishable key (or legacy anon key); bundled into the browser |
| `SUPABASE_SERVICE_ROLE_KEY` | Legacy service_role JWT; trusted setup scripts and server-side user management only |
| `DATABASE_URL` | Your dashboard Connect → Session pooler URI, with the database password; URL-encode special characters in the password |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3003` during local development |

Keep the existing variable names. The direct REST helpers currently send the
server key as a Bearer token, so use the legacy service_role JWT for those
helpers; migrating them to the new secret-key header flow is separate work.
Never put a private key in any `NEXT_PUBLIC_*` variable. See
[Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys).
Resend and recruit-notification variables are optional scaffold settings and
are not needed to log in with a password.

## 2. Apply the schema

After checking that `DATABASE_URL` points to your **new project**:

```sh
pnpm db:exec --all
```

This applies `supabase/migrations/*.sql` in filename order. Finish all 30
migrations before allowing access: intermediate historical migrations briefly
used broader permissions, which subsequent migrations replace. If a file fails,
stop and investigate; do not serve the partially configured project.

This runner commits each migration separately and does not maintain the Supabase
CLI migration ledger. Do not rerun `--all` on an existing database or follow it
with `supabase db push`. Existing installations must apply only new, unapplied
migration files through their established migration workflow.

Included schema:

- `site_state`: the current website's JSON document, stored as text with key
  `cal-hockey-site`, plus revision and update metadata.
- `site_admins`: editor allow-list with `admin` / `editor` roles.
- `site_state_history`: previous content versions and author metadata.
- Row-level policies, permission helper, history triggers, realtime publication,
  and the public `media` storage bucket.
- Relational tables for the separate Next.js scaffold. Those are not the current
  website's content source; do not use `pnpm seed` to initialize the current site.

No named accounts are granted access by the migrations. Removing historical
identity seeding affects fresh installs only; it does not revoke existing access.

## 3. Create your first admin

In Supabase Authentication → Users, create a user with your email and a password.
For a developer account you control, mark it confirmed when creating it so the
initial password login does not depend on email delivery.

In the SQL editor, replace the example address below with that user's email and
run:

```sql
insert into public.site_admins (email, role, note)
values (lower('you@example.com'), 'admin', 'Project owner')
on conflict (email) do update set role = excluded.role;
```

Both the Auth user and the allow-list row are necessary. An Auth account alone
cannot save website content. Admins can manage other users via the deployed
`/api/manage-users` server function; editors can edit content but not access.
Do not store a password in this SQL or in a committed file.

## 4. Configure login and email

Enable email/password authentication. Set Auth → URL Configuration → Site URL
to `http://localhost:3003` while developing, then to your production origin when
launching. Add these allowed redirect URLs, substituting your own hostname:

- `http://localhost:3003/admin`
- `https://YOUR-SITE.vercel.app/admin`

Add any other local port or preview origin explicitly when using it. The
`NEXT_PUBLIC_SITE_URL` variable does not configure the Supabase dashboard.
See [redirect URL configuration](https://supabase.com/docs/guides/auth/redirect-urls).

Password login works without sending a magic-link email. For magic links,
password recovery, and invitations to ordinary users, configure custom SMTP with
a verified sender domain. Supabase's built-in email service is restricted and
rate-limited; it is not a general production sender. See
[SMTP setup](https://supabase.com/docs/guides/auth/auth-smtp).

## 5. Initialize content and preview

The repository includes a sanitized public-content snapshot, not a live database
backup. Initialize it only into your new project:

```sh
node scripts/site-push.mjs --if-empty
```

This refuses to replace an existing site row. A concurrent insert also fails
instead of overwriting content. It does not create or change admins.

Start these in two terminals from the repository root:

```sh
# Terminal 1: rebuild when source changes
node prototype/build.mjs --watch
```

```sh
# Terminal 2: local website
PORT=3003 node prototype/serve.mjs
```

Open `http://localhost:3003` and `/admin`. The local server does not provide the
Vercel user-management function, so manage the first users in Supabase or test
that feature on a Vercel deployment with server environment variables set.

## 6. Verify your setup

On the new project only:

1. In a signed-out browser, confirm the roster and schedule load.
2. Log in as your admin using a password, change a harmless content field, and
   confirm a separate browser sees it. Restore the field afterward.
3. Create a test Auth user without a `site_admins` row and verify it cannot save.
4. Check that `site_state.rev` advances and history records the edit.
5. After deployment, confirm the admin can manage users while an editor cannot.

## 7. Deploy your copy

```sh
pnpm run build:site
# Link dist/ to YOUR Vercel project, then deploy that directory.
```

The build reads the public keys from root `.env.local`; changing projects means
rebuilding the bundle. Configure `NEXT_PUBLIC_SUPABASE_URL`,
`NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` in your Vercel
project's server environment for user management. `DATABASE_URL` is for migration
tools and is not required by the hosted website.

Use your own Vercel project and Supabase URL, not the production identifiers in
[DEPLOY.md](../DEPLOY.md). Repository clones do not include the ignored Vercel
project link, secrets, Auth users, or uploaded objects from an existing Supabase
storage bucket. The checked-in photos are ordinary static website assets.
