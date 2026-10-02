# Cal Ice Hockey

The current website and admin console are built from
`reference/cal-ice-hockey-app.jsx` through `prototype/entry.jsx`.
The Next.js projects under `apps/` are separate scaffolding, not the deployed site.

## Developer setup

Start with **[Supabase and local setup](supabase/README.md)**. It covers a new
database, migrations, your first admin, password login, email delivery, and
local preview. Each developer should use their own Supabase project.

- [Deployment instructions](DEPLOY.md)
- [Database migrations](supabase/migrations)
- [Environment variable template](.env.example)

Use Node.js 22+ and the pnpm version declared in `package.json`.

```sh
pnpm install
cp .env.example .env.local
# Fill in your own project settings and complete supabase/README.md.
pnpm run build:site
```

The production build is `dist/`. Do not deploy the repository root or use the
monorepo `build` script for this website. Never commit `.env.local`, database
passwords, private API keys, auth exports, or private recruit/alumni records.

Source code and a sanitized public-content snapshot are included. Hosted user
accounts, passwords, live database updates, and dashboard configuration are not
copied by cloning the repository.
