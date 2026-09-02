# Publishing the site

The prototype is a static folder. `dist/` is built from the source plus the
newest `data/backup-*/site.json`, and hosted at a domain root.

## Why your data is safe

`localStorage` is per-origin. Your editing happens at `localhost:3002`; the
live site is a different origin with a completely separate store. **A deploy
cannot reach the browser you work in.** Nothing below can overwrite your data.

The risks are the other direction — shipping the wrong data, or losing work
done in the wrong place. See [What actually loses data](#what-actually-loses-data).

## Deploying

**1. Export the browser's copy.** The repo is only as fresh as the last export,
and the browser is the only place edits exist until you do this. Skip it only
if you have made no admin edits since the last one.

    node prototype/_recv.mjs data/backup-$(date +%F)/site.json

Then in the console at `localhost:3002`:

    fetch('http://localhost:3999/', { method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: localStorage.getItem('cal-hockey-site') })

**2. Build.** Takes the newest `data/backup-*` by folder name, so a fresh
export is picked up with no further ceremony.

    node prototype/build.mjs && node prototype/dist.mjs

It refuses to build rather than ship something harmful — see
[The guards](#the-guards). Check the printed rev matches your browser's.

**3. Deploy a preview.** First run asks setup questions; accept the defaults.

    npx vercel login
    npx vercel deploy dist

**4. Check the preview before promoting.** If `site.json` fails to load, a
visitor falls through to the built-in seed and sees fictional players.

    curl -s https://YOUR-PREVIEW.vercel.app/version.json

Must print the rev from step 2. Open the URL and confirm the season list is
the real one. If either is wrong, stop.

**5. Promote.**

    npx vercel deploy dist --prod

## The guards

`dist.mjs` refuses to package a folder that would damage a visitor's data.
Both run before `dist/` is cleared, so a refused build leaves the last good
one in place.

- **`v` vs `SEED_VERSION`.** The page runs a one-time migration when stored
  data is behind the source, and that migration *replaces every season with
  the sample data*. It is meant for a stale copy in someone's browser. Ship
  data whose `v` is behind and it aims at the club's real seasons instead:
  every returning visitor is handed fictional players and saves them over the
  real ones. The number is read from the source, so the two cannot drift.

- **A missing rev.** Zero means every returning visitor is already ahead, no
  update ever reaches anyone, and the site looks frozen with no clue why.

## What actually loses data

- **Editing on the live site.** Those edits live only in that browser, for
  that domain. The next deploy ships a higher rev and the load path replaces
  them wholesale. Do all admin work at `localhost:3002`. The admin screens are
  in the deployed bundle and reachable — they just edit a throwaway copy.

- **Shipping a stale backup.** Step 1 is the guard. `dist.mjs` takes the
  newest folder by name, so an ISO date that sorts wrong ships an old season
  silently.

- **Not exporting before the tab closes.** The browser copy is the only one
  until step 1 runs. This has cost work before.

## Rollback

There is no git remote, so Vercel has no deploy history to roll back through.
To undo a bad publish, rebuild from a known-good `data/backup-*` and deploy
again. Pushing this repo to GitHub and connecting it to Vercel would give
one-click rollback and a deploy on every commit — worth doing before the
domain is public.
