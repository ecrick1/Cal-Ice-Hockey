import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.PORT ?? 3002);
const types = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  // Without these, images fall back to application/octet-stream and the
  // browser refuses to render them — an <img> that silently shows nothing.
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.ico': 'image/x-icon', '.json': 'application/json',
};

/**
 * The ACHA's own feed, proxied.
 *
 * It sends no CORS headers, so a browser cannot read it directly - the fetch
 * fails before the response is seen. The real site is Next.js and would do
 * this in a route handler with ISR; here a small proxy stands in, so the page
 * code is written the same way either side of the port.
 *
 * Answers are held for five minutes. A team's record does not change faster
 * than that, and it keeps a page refresh from hammering somebody else's
 * server.
 */
const ACHA = 'https://lscluster.hockeytech.com/feed/index.php';
const ACHA_KEY = 'e6867b36742a0c9d';
const ACHA_TTL = 5 * 60 * 1000;
const achaCache = new Map();

/* Only the views this site asks for. An open relay to any upstream URL is
   not what a proxy on a public origin should be. */
const ACHA_VIEWS = new Set(['seasonsForLeague', 'teamsForSeason', 'schedule', 'roster', 'gameSummary']);

async function achaProxy(req, res) {
  const q = new URL(req.url, 'http://localhost');
  const view = q.searchParams.get('view') ?? '';
  if (!ACHA_VIEWS.has(view)) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'unknown view' }));
    return;
  }

  const params = new URLSearchParams({
    feed: 'statviewfeed', view, key: ACHA_KEY,
    site_id: '2', client_code: 'acha', lang: 'en', league_id: '1',
  });
  /* Numeric ids only - nothing typed by a visitor reaches the upstream. */
  for (const k of ['season_id', 'team_id', 'team', 'game_id']) {
    const v = q.searchParams.get(k);
    if (v && /^\d+$/.test(v)) params.set(k, v);
  }

  const target = ACHA + '?' + params;
  const hit = achaCache.get(target);
  if (hit && Date.now() - hit.at < ACHA_TTL) {
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'hit' });
    res.end(hit.body);
    return;
  }

  try {
    const text = await fetch(target).then((r) => r.text());
    /* The feed sometimes wraps its JSON in parentheses. Unwrapped here so
       every caller does not have to know that. */
    const t = text.trim();
    const body = t.startsWith('(') ? t.slice(1, -1) : t;
    JSON.parse(body);
    achaCache.set(target, { at: Date.now(), body });
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'miss' });
    res.end(body);
  } catch (e) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: String(e && e.message || e) }));
  }
}

/* A season's worth of summaries is expensive to build and changes slowly. */
const seasonCache = new Map();
const SEASON_TTL = 60 * 60 * 1000;

const achaJson = async (params) => {
  const q = new URLSearchParams({
    feed: 'statviewfeed', key: ACHA_KEY, site_id: '2',
    client_code: 'acha', lang: 'en', league_id: '1', ...params,
  });
  const text = await fetch(ACHA + '?' + q).then((r) => r.text());
  const t = text.trim();
  return JSON.parse(t.startsWith('(') ? t.slice(1, -1) : t);
};

async function teamSeason(req, res) {
  const q = new URL(req.url, 'http://localhost');
  const season = q.searchParams.get('season_id') ?? '';
  const team = q.searchParams.get('team') ?? '';
  if (!/^\d+$/.test(season) || !/^\d+$/.test(team)) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'season_id and team must be numeric' }));
    return;
  }

  const key = season + ':' + team;
  const hit = seasonCache.get(key);
  if (hit && Date.now() - hit.at < SEASON_TTL) {
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'hit' });
    res.end(hit.body);
    return;
  }

  try {
    const sched = await achaJson({ view: 'schedule', season_id: season, team });
    const holder = Array.isArray(sched) ? sched[0] : sched;
    const rows = ((holder && holder.sections) || [])
      .flatMap((sec) => (sec.data || []).map((d) => d.row));
    const ids = rows.filter((r) => /final/i.test(r.game_status || '')).map((r) => r.game_id);

    const skaters = new Map();
    const goalies = new Map();
    let i = 0;
    /* Six at a time: quick enough to serve a page, gentle enough on a feed
       that is doing this as a favour. */
    const worker = async () => {
      while (i < ids.length) {
        const id = ids[i++];
        let g;
        try { g = await achaJson({ view: 'gameSummary', game_id: id }); } catch { continue; }
        for (const side of ['homeTeam', 'visitingTeam']) {
          const T = g[side];
          if (!T || !T.info || String(T.info.id) !== String(team)) continue;
          for (const pl of T.skaters || []) {
            const k = pl.info.id;
            /* The feed carries a placeholder line with no id and no name -
               goals the scorekeeper never attributed to anybody. It is a real
               part of the team's total but not a player, so it is left out of
               a list of players. */
            if (!k || String(k) === '0' || !pl.info.lastName) continue;
            if (!skaters.has(k)) {
              skaters.set(k, { name: pl.info.firstName + ' ' + pl.info.lastName,
                number: pl.info.jerseyNumber, pos: pl.info.position, gp: 0, g: 0, a: 0, pim: 0 });
            }
            const r = skaters.get(k);
            r.gp++; r.g += pl.stats.goals || 0; r.a += pl.stats.assists || 0;
            r.pim += pl.stats.penaltyMinutes || 0;
          }
          for (const pl of T.goalies || []) {
            /* A backup who dressed and never faced a shot did not play. */
            const faced = (pl.stats.saves || 0) + (pl.stats.goalsAgainst || 0);
            if (!faced) continue;
            const k = pl.info.id;
            if (!k || String(k) === '0' || !pl.info.lastName) continue;
            if (!goalies.has(k)) {
              goalies.set(k, { name: pl.info.firstName + ' ' + pl.info.lastName,
                number: pl.info.jerseyNumber, gp: 0, saves: 0, ga: 0, so: 0 });
            }
            const r = goalies.get(k);
            r.gp++; r.saves += pl.stats.saves || 0; r.ga += pl.stats.goalsAgainst || 0;
            if ((pl.stats.goalsAgainst || 0) === 0) r.so++;
          }
        }
      }
    };
    await Promise.all(Array.from({ length: 6 }, worker));

    const body = JSON.stringify({
      games: ids.length,
      source: 'ACHA game summaries',
      skaters: [...skaters.values()].sort((a, b) => (b.g + b.a) - (a.g + a.a)),
      goalies: [...goalies.values()].sort((a, b) => b.gp - a.gp),
    });
    seasonCache.set(key, { at: Date.now(), body });
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'miss' });
    res.end(body);
  } catch (e) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: String((e && e.message) || e) }));
  }
}

/**
 * Write a file into the working tree, so the prototype's state can be got
 * out of one browser profile and into the repository.
 *
 * Development only, and deliberately narrow: the path has to resolve inside
 * this checkout, and only the two directories the exporter writes to are
 * allowed. It is here because the alternative - a browser download - lands
 * in Downloads under whatever name the browser picks.
 */
async function saveFile(req, res) {
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'text/plain' });
    res.end('POST only');
    return;
  }
  const q = new URLSearchParams(req.url.split('?')[1] || '');
  const rel = q.get('to') || '';
  const root = path.resolve(dir, '..');
  const full = path.resolve(root, path.posix.normalize(rel).replace(/^\/+/, ''));
  const allowed = [path.join(root, 'data'), path.join(dir, 'articles')];
  if (!allowed.some((a) => full === a || full.startsWith(a + path.sep))) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Not a writable path: ' + rel);
    return;
  }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const body = Buffer.concat(chunks);
  await mkdir(path.dirname(full), { recursive: true });
  const isB64 = q.get('base64') === '1';
  await writeFile(full, isB64 ? Buffer.from(body.toString('utf8'), 'base64') : body);
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ ok: true, path: path.relative(root, full), bytes: body.length }));
}

/**
 * The site data, and the rev that guards it.
 *
 * The page asks for ./site.json and ./version.json on every load, and takes
 * an update when the shipped rev is above the one in storage. This directory
 * has neither file - they are written into dist/ at build time - so on the
 * dev server both requests 404, the rev comes back null, and no edit made in
 * the repo ever reaches the browser. Storage simply wins forever, which looks
 * exactly like the data not having been saved.
 *
 * Served straight out of the newest data/backup-*, the same file dist ships,
 * so there is one copy of the data and the dev server is never behind it.
 */
const BACKUPS = path.resolve(dir, '..', 'data');

async function newestBackup() {
  const dirs = (await readdir(BACKUPS, { withFileTypes: true }))
    .filter((d) => d.isDirectory() && d.name.startsWith('backup-'))
    .map((d) => d.name)
    .sort();
  for (let i = dirs.length - 1; i >= 0; i--) {
    const f = path.join(BACKUPS, dirs[i], 'site.json');
    try { await readFile(f); return f; } catch { /* keep looking */ }
  }
  return null;
}

async function siteData(res, revOnly) {
  const f = await newestBackup();
  if (!f) { res.writeHead(404, { 'Content-Type': 'text/plain' }); res.end('no backup'); return; }
  const body = await readFile(f);
  const out = revOnly
    ? Buffer.from(JSON.stringify({ rev: Number(JSON.parse(body).rev || 0) }))
    : body;
  res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
  res.end(out);
}

createServer(async (req, res) => {
  const url = (req.url ?? '/').split('?')[0];
  if (url === '/acha') return achaProxy(req, res);
  if (url === '/acha/team-season') return teamSeason(req, res);
  if (url === '/save') return saveFile(req, res);
  if (url === '/site.json') return siteData(res, false);
  if (url === '/version.json') return siteData(res, true);
  const file = url === '/' ? 'index.html' : decodeURIComponent(url);
  const full = path.resolve(dir, '.' + path.posix.normalize('/' + file));

  // Serve only from this directory — reject anything that escapes it.
  if (full !== dir && !full.startsWith(dir + path.sep)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  try {
    const body = await readFile(full);
    res.writeHead(200, {
      'Content-Type': types[path.extname(full)] ?? 'application/octet-stream',
      'Cache-Control': 'no-store',
    });
    res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
  }
}).listen(port, () => console.log(`prototype on http://localhost:${port}`));
