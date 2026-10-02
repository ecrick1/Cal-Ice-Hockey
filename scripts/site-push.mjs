/**
 * Put the repo's copy of the site into the database, and name who may edit it.
 *
 * Ordinarily the console writes to site_state itself and this is not needed.
 * It exists for the two moments the console cannot cover: the first upload,
 * before there is anything to read, and a recovery, when what is in the
 * database is worse than what is in the repo.
 *
 *   node scripts/site-push.mjs --if-empty          # initialize a NEW project only
 *   node scripts/site-push.mjs                     # upload the newest backup
 *   node scripts/site-push.mjs --admin a@b.edu     # ...and allow that address
 *   node scripts/site-push.mjs --admin a@b.edu --only-admin
 *
 * Uses the service role key, which bypasses row-level security. That is the
 * point - there is no signed-in person here - and it is also why this is a
 * script run by hand from a machine holding .env.local, and never anything
 * the site imports.
 */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { config } from 'dotenv';

config({ path: '.env.local' });

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const secret = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !secret) {
  console.error('Need NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local');
  process.exit(1);
}

const args = process.argv.slice(2);
const adminAt = args.indexOf('--admin');
const admin = adminAt === -1 ? null : args[adminAt + 1];
const ifEmpty = args.includes('--if-empty');
if (ifEmpty && admin) {
  console.error('--if-empty seeds content only; create the first admin separately.');
  process.exit(1);
}
const onlyAdmin = args.includes('--only-admin');

const api = (path, init = {}) =>
  fetch(url.replace(/\/$/, '') + path, {
    ...init,
    headers: {
      apikey: secret,
      Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });

const die = async (what, res) => {
  console.error(what + ' failed: ' + res.status + ' ' + (await res.text()).slice(0, 300));
  process.exit(1);
};

if (admin) {
  const res = await api('/rest/v1/site_admins?on_conflict=email', {
    method: 'POST',
    headers: { Prefer: 'resolution=merge-duplicates' },
    body: JSON.stringify([{ email: admin.toLowerCase(), note: 'added by site-push' }]),
  });
  if (!res.ok) await die('adding admin', res);
  console.log('admin allowed: ' + admin.toLowerCase());
}

if (!onlyAdmin) {
  /* The newest backup, the same one dist ships, so the database and a fresh
     build never disagree about what the site is. */
  const backups = path.join(root, 'data');
  const dirs = (await readdir(backups, { withFileTypes: true }))
    .filter((d) => d.isDirectory() && /^backup-\d{4}-\d{2}-\d{2}$/.test(d.name))
    .map((d) => d.name)
    .sort();
  if (!dirs.length) { console.error('no data/backup-* to push'); process.exit(1); }
  const file = path.join(backups, dirs[dirs.length - 1], 'site.json');
  const text = await readFile(file, 'utf8');
  const site = JSON.parse(text);
  if (!site.seasons) { console.error('that file has no seasons — wrong one?'); process.exit(1); }

  /* Never push backwards. Overwriting a newer row with an older file is the
     one thing this script could do that nobody could undo. */
  const cur = await api('/rest/v1/site_state?key=eq.cal-hockey-site&select=rev');
  if (!cur.ok) await die('reading current rev', cur);
  const rows = await cur.json();
  const there = rows.length ? Number(rows[0].rev || 0) : null;
  const here = Number(site.rev || 0);
  if (ifEmpty && rows.length) {
    console.error('Site already exists; --if-empty will not overwrite it.');
    process.exit(1);
  }
  if (there !== null && there > here) {
    console.error(
      'the database is at rev ' + there + ' and this file is rev ' + here + '. '
      + 'Pushing would undo ' + (there - here) + ' revisions. Export the newer '
      + 'copy first, or pass the file you actually mean.');
    process.exit(1);
  }

  const res = await api(ifEmpty ? '/rest/v1/site_state' : '/rest/v1/site_state?on_conflict=key', {
    method: 'POST',
    headers: ifEmpty ? {} : { Prefer: 'resolution=merge-duplicates' },
    body: JSON.stringify([{
      key: 'cal-hockey-site', value: text, rev: here, updated_at: new Date().toISOString(),
    }]),
  });
  if (!res.ok) await die('uploading site', res);
  console.log(
    'pushed ' + path.relative(root, file) + ' — rev ' + here
    + (there === null ? ' (first upload)' : ' (was ' + there + ')')
    + ', ' + (text.length / 1024 / 1024).toFixed(1) + ' MB, '
    + Object.keys(site.seasons).length + ' seasons');
}
