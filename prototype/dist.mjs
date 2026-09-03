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
import { readdirSync, existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/* fileURLToPath, not the URL's pathname: this folder has a space in its
   name and a pathname keeps it percent-encoded. */
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const out = path.join(root, "dist");

const ASSET_DIRS = ["logos", "photos", "covers", "staff", "articles"];
/* The newest backup, not a named one. The date was written in here, which
   meant that taking a fresh export and shipping it were two jobs rather than
   one - and forgetting the second silently deploys the older season. The
   folders are ISO-dated, so newest is last in sort order. */
const BACKUPS = path.join(root, "data");
const SITE_DATA = (() => {
  const dirs = readdirSync(BACKUPS)
    .filter((d) => /^backup-\d{4}-\d{2}-\d{2}$/.test(d))
    .filter((d) => existsSync(path.join(BACKUPS, d, "site.json")))
    .sort();
  if (!dirs.length) throw new Error("no data/backup-*/site.json to ship");

  /* Newest by date, but the date is a claim about when the export happened
     and the rev is what the data actually is. Exporting a browser that is
     behind the repo writes today's folder with older data in it - which
     sorts newest and would ship, quietly undoing everything done since that
     browser last loaded. The two orderings agreeing is the normal case; when
     they disagree something is wrong that a person has to look at, because
     either the export was stale or a folder is misdated. */
  const revOf = (d) => {
    try { return Number(JSON.parse(readFileSync(path.join(BACKUPS, d, "site.json"), "utf8")).rev || 0); }
    catch { return 0; }
  };
  const pick = dirs[dirs.length - 1];
  const best = dirs.reduce((a, b) => (revOf(b) > revOf(a) ? b : a));
  if (revOf(pick) < revOf(best)) {
    throw new Error(
      "newest backup " + pick + " is rev " + revOf(pick) + ", but " + best
      + " is rev " + revOf(best) + ". Publishing the newer folder would undo "
      + (revOf(best) - revOf(pick)) + " revisions. Either the export was taken "
      + "from a browser that had not loaded the latest, or a folder is misdated.");
  }
  return path.join(BACKUPS, pick, "site.json");
})();

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

/* The club's own data, so a visitor sees the real site rather than the seed. */
const site = JSON.parse(await readFile(SITE_DATA, "utf8"));
if (!site.seasons) throw new Error("site.json has no seasons — wrong file?");

/**
 * The migration guard, checked here rather than discovered by visitors.
 *
 * The page runs a one-time migration when the stored data's `v` is behind the
 * source's SEED_VERSION, and that migration replaces every season with the
 * built-in sample data. It exists so an old copy in somebody's browser gets
 * rebuilt, and it is correct for that. Shipping data whose `v` is behind
 * would aim it at the club's own seasons instead: each returning visitor
 * would load the site, be handed fictional players, and save them over the
 * real ones.
 *
 * The source is the authority on the number, so it is read from there rather
 * than written down twice.
 */
const src = await readFile(path.join(root, "reference", "cal-ice-hockey-app.jsx"), "utf8");
const seedVersion = Number((src.match(/const SEED_VERSION = (\d+)/) || [])[1]);
if (!Number.isFinite(seedVersion)) {
  throw new Error("cannot find SEED_VERSION in the source — refusing to build blind");
}
if (Number(site.v) !== seedVersion) {
  throw new Error(
    "data v=" + site.v + " but SEED_VERSION=" + seedVersion + ". Publishing this "
    + "would replace every visitor's seasons with the seed. Bump `v` in "
    + path.relative(root, SITE_DATA) + " to " + seedVersion + " once the data "
    + "is known to suit the new version.");
}

/* A rev of zero means every returning visitor is already ahead and no update
   ever reaches them; the site would look frozen and nobody would see why. */
if (!Number(site.rev)) throw new Error("data has no rev — nothing would ever update");

/* Vercel writes its project link into .vercel inside the folder it deploys,
   and this build empties that folder. Left alone, every rebuild would unlink
   the project and the next deploy would ask the setup questions again - and
   answering them again makes a second project, so the domain everybody has
   would stop being the one receiving updates. Carried across instead. */
const link = path.join(out, ".vercel");
const keptLink = existsSync(link)
  ? await cp(link, path.join(root, ".vercel-link-tmp"), { recursive: true }).then(() => true)
  : false;

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

await writeFile(path.join(out, "index.html"), page);
await cp(path.join(here, "app.js"), path.join(out, "app.js"));

await writeFile(path.join(out, "site.json"), JSON.stringify(site));

for (const d of ASSET_DIRS) {
  await cp(path.join(here, d), path.join(out, d), { recursive: true });
}

/* The rev on its own, so a returning visitor can find out whether the four
   megabytes are worth fetching without fetching them. */
await writeFile(path.join(out, "version.json"),
  JSON.stringify({ rev: Number(site.rev || 0), built: new Date().toISOString() }) + "\n");

await writeFile(path.join(out, "_redirects"), redirects);
await writeFile(path.join(out, "vercel.json"), vercel);

/* The project link back where Vercel expects it. */
if (keptLink) {
  await cp(path.join(root, ".vercel-link-tmp"), link, { recursive: true });
  await rm(path.join(root, ".vercel-link-tmp"), { recursive: true, force: true });
}

const seasons = Object.keys(site.seasons).length;
const games = Object.values(site.seasons)
  .reduce((n, s) => n + ((s.schedule || []).length), 0);
console.log("dist/ built");
console.log("  app.js     " + mb(await size(path.join(out, "app.js"))));
console.log("  site.json  " + mb(await size(path.join(out, "site.json")))
  + "  (" + seasons + " seasons, " + games + " games, "
  + (site.news || []).length + " articles)");
console.log("  version    rev " + Number(site.rev || 0)
  + "  (a returning visitor updates when this goes up)");
console.log("  assets     " + ASSET_DIRS.join(", "));
console.log("\nServe the folder at a domain root — assets are referenced from /.");
