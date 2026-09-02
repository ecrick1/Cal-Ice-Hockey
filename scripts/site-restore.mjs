/**
 * Look at what the site used to be, and put one of those versions back.
 *
 * Anyone signed in can edit, so the answer to a bad edit is not preventing it
 * but reversing it. Every version the site is replaced from is kept - the last
 * twenty - with the account that wrote it and when.
 *
 *   node scripts/site-restore.mjs                 # list what is kept
 *   node scripts/site-restore.mjs --show 12       # what that version contains
 *   node scripts/site-restore.mjs --restore 12    # put it back
 *   node scripts/site-restore.mjs --save 12 out.json
 *
 * Restoring writes the old document forward with a new, higher rev rather than
 * moving the number backwards. Every browser holding the bad version compares
 * revs to decide whether to update, so a restore that lowered the rev would
 * reach nobody - the ones that most need it least of all.
 *
 * Uses the service role key, which is why this is run by hand from a machine
 * holding .env.local and never from anything the site loads.
 */
import { writeFile } from 'node:fs/promises';
import { config } from 'dotenv';

config({ path: '.env.local' });

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const secret = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !secret) {
  console.error('Need NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local');
  process.exit(1);
}

const KEY = 'cal-hockey-site';
const api = (p, init = {}) =>
  fetch(url.replace(/\/$/, '') + p, {
    ...init,
    headers: {
      apikey: secret, Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/json', ...(init.headers || {}),
    },
  });

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  return i === -1 ? null : args[i + 1];
};

const summarise = (text) => {
  try {
    const d = JSON.parse(text);
    const games = Object.values(d.seasons || {})
      .reduce((n, s) => n + ((s.schedule || []).length), 0);
    const scored = Object.values(d.seasons || {})
      .reduce((n, s) => n + (s.schedule || []).filter((g) => g.result).length, 0);
    return Object.keys(d.seasons || {}).length + ' seasons, ' + games + ' games, '
      + scored + ' scored, ' + (d.news || []).length + ' articles';
  } catch { return 'unreadable'; }
};

const showId = flag('--show');
const restoreId = flag('--restore');
const saveId = flag('--save');
const saveTo = saveId ? args[args.indexOf('--save') + 2] : null;

const one = async (id) => {
  const res = await api('/rest/v1/site_state_history?id=eq.' + encodeURIComponent(id)
    + '&select=id,rev,value,replaced_at,written_at,written_by');
  if (!res.ok) { console.error(await res.text()); process.exit(1); }
  const rows = await res.json();
  if (!rows.length) { console.error('no version with id ' + id); process.exit(1); }
  return rows[0];
};

if (showId || saveId) {
  const row = await one(showId || saveId);
  console.log('version ' + row.id + ' — rev ' + row.rev);
  console.log('  written  ' + (row.written_at || '?') + ' by ' + (row.written_by || 'unknown'));
  console.log('  replaced ' + row.replaced_at);
  console.log('  contains ' + summarise(row.value));
  if (saveTo) { await writeFile(saveTo, row.value); console.log('  saved to ' + saveTo); }
} else if (restoreId) {
  const row = await one(restoreId);
  const cur = await api('/rest/v1/site_state?key=eq.' + KEY + '&select=rev');
  const now = Number(((await cur.json())[0] || {}).rev || 0);
  const next = now + 1;

  /* Forward, not backward: the document is the old one, the rev is a new one,
     so every browser sees an update rather than something older than it has. */
  const doc = JSON.parse(row.value);
  doc.rev = next;
  const res = await api('/rest/v1/site_state?key=eq.' + KEY, {
    method: 'PATCH',
    body: JSON.stringify({ value: JSON.stringify(doc), rev: next,
                           updated_at: new Date().toISOString() }),
  });
  if (!res.ok) { console.error('restore failed: ' + await res.text()); process.exit(1); }
  console.log('restored version ' + row.id + ' (was rev ' + row.rev + ') as rev ' + next);
  console.log('  ' + summarise(row.value));
  console.log('  the version it replaced is itself kept, so this is undoable too');
} else {
  const res = await api('/rest/v1/site_state_history?key=eq.' + KEY
    + '&select=id,rev,replaced_at,written_at,written_by&order=id.desc');
  if (!res.ok) { console.error(await res.text()); process.exit(1); }
  const rows = await res.json();
  const cur = await api('/rest/v1/site_state?key=eq.' + KEY + '&select=rev,updated_at,updated_by');
  const live = (await cur.json())[0] || {};
  console.log('live      rev ' + live.rev + '  ' + (live.updated_at || '')
    + '  by ' + (live.updated_by || 'unknown'));
  if (!rows.length) { console.log('\nno earlier versions kept yet'); }
  else {
    console.log('\nkept versions, newest first:');
    for (const r of rows) {
      console.log('  id ' + String(r.id).padEnd(5) + ' rev ' + String(r.rev).padEnd(6)
        + ' replaced ' + r.replaced_at + '  by ' + (r.written_by || 'unknown'));
    }
    console.log('\n  node scripts/site-restore.mjs --show <id>');
    console.log('  node scripts/site-restore.mjs --restore <id>');
  }
}
