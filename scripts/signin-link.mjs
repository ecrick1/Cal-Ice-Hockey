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
/* The live site by default. NEXT_PUBLIC_SITE_URL is the Next apps' dev
   address - localhost:3000 - and using it here sent the link somewhere with
   nothing running on it, which is not a sign-in, it is a dead end. */
const siteAt = args.indexOf('--site');
const site = siteAt === -1 ? 'https://cal-ice-hockey.vercel.app' : args[siteAt + 1];

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
const props = body.properties || body;
const link = props.action_link;
const otp = props.email_otp;
if (!link) { console.error('no link came back: ' + JSON.stringify(body).slice(0, 300)); process.exit(1); }
/* Supabase rate-limits how often one email can be issued a new code - request
   a second one too soon after the first and the reply still carries a link,
   just no `email_otp`. The file below already handles this (the code section
   only appears when there is one), but silently was how "the code isn't in
   the file" turned into "sign-in is broken" - it looked identical to success
   until somebody went looking for a code that was never going to be there. */
if (!otp) {
  console.error('note: no code came back this time (probably asked again too soon after');
  console.error('the last one for this address) - the file below will only have the link.');
  console.error('Wait a minute and rerun if you want the code as a fallback too.');
}

/* Two ways in, because they fail differently. The link depends on the redirect
   being configured and on nothing having followed the URL first; the code
   depends on neither, and is typed straight into the console. */
const out = path.resolve('signin-link.html');
await writeFile(out,
  '<!doctype html><meta charset="utf-8"><title>Sign in</title>'
  + '<body style="font:16px system-ui;padding:40px;max-width:34em">'
  + '<h1 style="font-size:20px">Sign in as ' + email + '</h1>'
  + (otp
    ? '<p>On the site, open <strong>Admin</strong>, choose <strong>I already have a code</strong>, '
      + 'enter this address and this code:</p>'
      + '<p style="font:600 30px/1.2 ui-monospace,monospace;letter-spacing:.12em;'
      + 'background:#f4f7f9;padding:14px 18px;border-radius:8px;display:inline-block">'
      + otp + '</p>'
      + '<p style="color:#666;font-size:14px">The code needs no email and no redirect, '
      + 'so it works when the link does not.</p><hr style="margin:26px 0;border:0;'
      + 'border-top:1px solid #ddd">'
    : '')
  + '<p><a href="' + link + '">Or open the site signed in</a></p>'
  + '<p style="color:#666;font-size:14px">One use only, and both stop working once either is '
  + 'used. Delete this file afterwards.</p>');

console.log('link written to ' + out);
console.log('  open it, click through, then delete the file:');
console.log('  node scripts/signin-link.mjs --clean');

if (args.includes('--clean')) {
  await unlink(out).catch(() => {});
  console.log('  (removed)');
}
