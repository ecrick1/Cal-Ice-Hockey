/**
 * A sign-in link for an editor, made here instead of emailed.
 *
 *   node scripts/signin-link.mjs ethanjcrick@gmail.com
 *   node scripts/signin-link.mjs ethanjcrick@gmail.com --site https://cal-ice-hockey.vercel.app
 *
 * The built-in Supabase mailer allows a couple of messages an hour, which is
 * enough for the odd sign-in and not enough for an afternoon of setting one
 * up. This asks the admin API for the same link the email would have carried.
 * Nothing is sent, so nothing is rate limited.
 *
 * It is written to a file rather than printed. The link signs somebody in by
 * itself for as long as it is unused, so it does not belong in scrollback,
 * a screenshot, or anything pasted into a chat window. Open the file, use the
 * link, delete the file - and the script offers to delete it for you.
 *
 * Break-glass, not routine. The routine answer is custom SMTP, after which
 * the site sends its own codes and nobody needs this.
 */
import { writeFile, unlink } from 'node:fs/promises';
import path from 'node:path';
import { config } from 'dotenv';

config({ path: '.env.local' });

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const secret = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !secret) {
  console.error('Need NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local');
  process.exit(1);
}

const args = process.argv.slice(2);
const email = args.find((a) => a.includes('@'));
if (!email) {
  console.error('usage: node scripts/signin-link.mjs you@example.com [--site https://...]');
  process.exit(1);
}
const siteAt = args.indexOf('--site');
const site = siteAt === -1
  ? (process.env.NEXT_PUBLIC_SITE_URL || 'https://cal-ice-hockey.vercel.app')
  : args[siteAt + 1];

const api = (p, init = {}) =>
  fetch(url.replace(/\/$/, '') + p, {
    ...init,
    headers: {
      apikey: secret, Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/json', ...(init.headers || {}),
    },
  });

/* Only for somebody who is already allowed to edit. This script exists to get
   an editor past a mail limit, not to be a second way of granting access that
   sidesteps the one deliberate step. */
const chk = await api('/rest/v1/site_admins?select=email&email=eq.'
  + encodeURIComponent(email.toLowerCase()));
if (!chk.ok) { console.error(await chk.text()); process.exit(1); }
if (!(await chk.json()).length) {
  console.error(email + ' is not on the editors list.');
  console.error('  node scripts/users.mjs --add ' + email);
  process.exit(1);
}

const res = await api('/auth/v1/admin/generate_link', {
  method: 'POST',
  body: JSON.stringify({ type: 'magiclink', email, options: { redirect_to: site } }),
});
if (!res.ok) { console.error('could not make a link: ' + await res.text()); process.exit(1); }
const body = await res.json();
const link = body.action_link || (body.properties && body.properties.action_link);
if (!link) { console.error('no link came back: ' + JSON.stringify(body).slice(0, 300)); process.exit(1); }

const out = path.resolve('signin-link.html');
await writeFile(out,
  '<!doctype html><meta charset="utf-8"><title>Sign in</title>'
  + '<body style="font:16px system-ui;padding:40px;max-width:34em">'
  + '<h1 style="font-size:20px">Sign in as ' + email + '</h1>'
  + '<p><a href="' + link + '">Open the site signed in</a></p>'
  + '<p style="color:#666;font-size:14px">One use only, and it stops working once used. '
  + 'Delete this file afterwards.</p>');

console.log('link written to ' + out);
console.log('  open it, click through, then delete the file:');
console.log('  node scripts/signin-link.mjs --clean');

if (args.includes('--clean')) {
  await unlink(out).catch(() => {});
  console.log('  (removed)');
}
