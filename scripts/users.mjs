/**
 * Who may edit the site.
 *
 *   node scripts/users.mjs                        # who has access
 *   node scripts/users.mjs --add name@place.edu   # invite
 *   node scripts/users.mjs --remove name@place.edu
 *
 * Adding someone does two things, and both are needed: it creates their
 * account, so the site will send them a sign-in code at all, and it puts them
 * on the editors list, which is what the database checks before allowing a
 * write. Either alone leaves a person who can sign in but change nothing, or
 * a name on a list that can never get through the door.
 *
 * Removing does the reverse of the second. The account stays - deleting
 * accounts is not something a script should do quietly - but it can no longer
 * write anything, immediately, without waiting for a session to expire.
 *
 * Run from a machine holding .env.local. It uses the service key, which is
 * exactly why granting access is a deliberate step taken here rather than a
 * button in a browser: a mistake in this file hands somebody the site.
 */
import { config } from 'dotenv';

config({ path: '.env.local' });

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const secret = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !secret) {
  console.error('Need NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local');
  process.exit(1);
}

const api = (p, init = {}) =>
  fetch(url.replace(/\/$/, '') + p, {
    ...init,
    headers: {
      apikey: secret, Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/json', ...(init.headers || {}),
    },
  });

const args = process.argv.slice(2);
const at = (f) => { const i = args.indexOf(f); return i === -1 ? null : args[i + 1]; };
const add = at('--add');
const remove = at('--remove');

const listUsers = async () => {
  const res = await api('/auth/v1/admin/users?per_page=200');
  if (!res.ok) { console.error(await res.text()); process.exit(1); }
  const body = await res.json();
  return body.users || body || [];
};
const listEditors = async () => {
  const res = await api('/rest/v1/site_admins?select=email,note,added_at&order=added_at');
  if (!res.ok) { console.error(await res.text()); process.exit(1); }
  return res.json();
};

if (add) {
  const email = add.trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    console.error('that does not look like an email address: ' + add);
    process.exit(1);
  }

  /* The account. Already existing is success, not a problem - somebody may
     have signed in while editing was open. */
  const users = await listUsers();
  const already = users.find((u) => (u.email || '').toLowerCase() === email);
  if (already) {
    console.log('account already exists (' + email + ')');
  } else {
    const res = await api('/auth/v1/admin/users', {
      method: 'POST',
      /* Confirmed on creation: the code they are sent when they sign in is
         itself the proof they hold the address, so a separate confirmation
         email is a second hoop for the same fact. */
      body: JSON.stringify({ email, email_confirm: true }),
    });
    if (!res.ok) { console.error('creating the account failed: ' + await res.text()); process.exit(1); }
    console.log('account created (' + email + ')');
  }

  const res = await api('/rest/v1/site_admins?on_conflict=email', {
    method: 'POST',
    headers: { Prefer: 'resolution=merge-duplicates' },
    body: JSON.stringify([{ email, note: 'invited ' + new Date().toISOString().slice(0, 10) }]),
  });
  if (!res.ok) { console.error('adding to the editors list failed: ' + await res.text()); process.exit(1); }
  console.log('added to editors — ' + email + ' can now sign in and save.');
} else if (remove) {
  const email = remove.trim().toLowerCase();
  const res = await api('/rest/v1/site_admins?email=eq.' + encodeURIComponent(email), {
    method: 'DELETE', headers: { Prefer: 'return=representation' },
  });
  if (!res.ok) { console.error(await res.text()); process.exit(1); }
  const gone = await res.json();
  if (!gone.length) { console.log(email + ' was not on the editors list; nothing changed.'); }
  else {
    console.log('removed from editors — ' + email + ' can no longer save. Effective at once:');
    console.log('  the check runs on every write, not when they signed in.');
    console.log('  their account still exists; delete it in the dashboard if you want it gone.');
  }
} else {
  const [editors, users] = await Promise.all([listEditors(), listUsers()]);
  const byEmail = new Map(users.map((u) => [(u.email || '').toLowerCase(), u]));
  console.log('editors — these addresses can sign in and save:\n');
  if (!editors.length) console.log('  (nobody, which means nobody can change the site)');
  for (const e of editors) {
    const u = byEmail.get(e.email.toLowerCase());
    console.log('  ' + e.email.padEnd(30)
      + (u ? 'account ok' : 'NO ACCOUNT — cannot sign in, run --add')
      + (u && u.last_sign_in_at ? '   last in ' + u.last_sign_in_at.slice(0, 10) : ''));
  }
  const strays = users.filter((u) => !editors.some((e) => e.email.toLowerCase() === (u.email || '').toLowerCase()));
  if (strays.length) {
    console.log('\naccounts that are not editors — they can sign in but cannot change anything:');
    for (const u of strays) console.log('  ' + u.email);
  }
  console.log('\n  node scripts/users.mjs --add name@place.edu');
  console.log('  node scripts/users.mjs --remove name@place.edu');
}
