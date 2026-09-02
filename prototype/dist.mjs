/**
 * Package a self-contained copy of the site for a static host.
 *
 * The prototype is served out of this folder with a dev server that also
 * writes files; a published copy needs none of that, and must not carry the
 * scripts, the source data dumps or the patch history that live here. So the
 * build lists what goes in rather than what stays out - an allow-list cannot
 * leak the next thing somebody drops in this directory.
 *
 * site.json is the point of the exercise: without it a visitor's empty
 * storage falls through to the built-in seed and the club has no seasons.
 *
 * Assets are referenced from the root ("/logos/..."), so the result has to be
 * served at a domain root rather than in a subdirectory.
 */
import { cp, mkdir, rm, writeFile, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

/* fileURLToPath, not the URL's pathname: this folder has a space in its
   name and a pathname keeps it percent-encoded. */
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const out = path.join(root, "dist");

const ASSET_DIRS = ["logos", "photos", "covers", "staff", "articles"];
const SITE_DATA = path.join(root, "data", "backup-2026-08-31", "site.json");

const TITLE = "Cal Ice Hockey";
const DESCRIPTION =
  "Schedule, results, roster, statistics and news for Cal Ice Hockey — "
  + "the University of California, Berkeley club team.";

const page = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${TITLE}</title>
    <meta name="description" content="${DESCRIPTION}" />
    <meta property="og:title" content="${TITLE}" />
    <meta property="og:description" content="${DESCRIPTION}" />
    <meta property="og:type" content="website" />
    <link rel="icon" href="/logos/cal.svg" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Inter:wght@400;600;700&display=swap"
      rel="stylesheet"
    />
    <style>
      html, body { margin: 0; padding: 0; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script src="./app.js"></script>
  </body>
</html>
`;

/* Every route is the same document: the app decides what to show from its own
   view state, so a host that returns index.html for anything it cannot find
   is the whole of the routing story. Both files, because Netlify reads one
   and Vercel the other, and a folder that works on either is worth two. */
const redirects = "/*  /index.html  200\n";
const vercel = JSON.stringify(
  { rewrites: [{ source: "/(.*)", destination: "/index.html" }] }, null, 2) + "\n";

const size = async (p) => (await stat(p)).size;
const mb = (n) => (n / 1024 / 1024).toFixed(1) + " MB";

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

await writeFile(path.join(out, "index.html"), page);
await cp(path.join(here, "app.js"), path.join(out, "app.js"));

/* The club's own data, so a visitor sees the real site rather than the seed. */
const site = JSON.parse(await readFile(SITE_DATA, "utf8"));
if (!site.seasons) throw new Error("site.json has no seasons — wrong file?");
await writeFile(path.join(out, "site.json"), JSON.stringify(site));

for (const d of ASSET_DIRS) {
  await cp(path.join(here, d), path.join(out, d), { recursive: true });
}

await writeFile(path.join(out, "_redirects"), redirects);
await writeFile(path.join(out, "vercel.json"), vercel);

const seasons = Object.keys(site.seasons).length;
const games = Object.values(site.seasons)
  .reduce((n, s) => n + ((s.schedule || []).length), 0);
console.log("dist/ built");
console.log("  app.js     " + mb(await size(path.join(out, "app.js"))));
console.log("  site.json  " + mb(await size(path.join(out, "site.json")))
  + "  (" + seasons + " seasons, " + games + " games, "
  + (site.news || []).length + " articles)");
console.log("  assets     " + ASSET_DIRS.join(", "));
console.log("\nServe the folder at a domain root — assets are referenced from /.");
