/**
 * Who edits the site, and who decides that — the one screen that needed a
 * server behind it rather than a write through the usual channel.
 *
 * Everything else the console saves goes through window.storage, which RLS
 * gates by row: anyone signed in can reach it, because "signed in" was the
 * whole bar. This is different. site_admins is the list that bar is checked
 * against, and scripts/users.mjs has always required the service-role key
 * for exactly that reason - a mistake here hands somebody the whole site,
 * so changing it was kept off anything a signed-in browser could reach on
 * its own.
 *
 * A console screen for it still needs a door, just not an unguarded one.
 * This function holds the service-role key (set in Vercel's own server
 * environment, never in the client bundle) and asks one question before
 * doing anything: does the token this request carries belong to somebody
 * who is themselves an admin, right now. Not "was, when they signed in" -
 * an admin demoted five minutes ago loses this the moment they try it
 * again, the same way scripts/users.mjs has always said a removed editor
 * loses write access "at once... the check runs on every write, not when
 * they signed in."
 */
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const secret = process.env.SUPABASE_SERVICE_ROLE_KEY;

const admin = (path, init = {}) =>
  fetch(url.replace(/\/$/, '') + path, {
    ...init,
    headers: {
      apikey: secret, Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/json', ...(init.headers || {}),
    },
  });

/* Whose token this is, and whether that address is an admin - looked up
   fresh, every call. Two questions, because a valid session (anyone signed
   in) and an admin session (this one narrower group) are not the same
   thing, and the first is cheap to fake by simply being signed in at all. */
async function callerRole(req) {
  const auth = req.headers.authorization || '';
  const token = auth.replace(/^Bearer\s+/i, '');
  if (!token) return null;

  const who = await fetch(url.replace(/\/$/, '') + '/auth/v1/user', {
    headers: { apikey: anon, Authorization: 'Bearer ' + token },
  });
  if (!who.ok) return null;
  const email = (await who.json()).email;
  if (!email) return null;

  const row = await admin('/rest/v1/site_admins?select=role&email=eq.'
    + encodeURIComponent(email.toLowerCase()));
  if (!row.ok) return null;
  const rows = await row.json();
  return { email: email.toLowerCase(), role: (rows[0] || {}).role || null };
}

const bad = (res, code, msg) => res.status(code).json({ error: msg });

export default async function handler(req, res) {
  if (!url || !anon || !secret) return bad(res, 500, 'server is missing its Supabase configuration');

  const me = await callerRole(req);
  if (!me || me.role !== 'admin') return bad(res, 403, 'admins only');

  if (req.method === 'GET') {
    const [usersRes, editorsRes] = await Promise.all([
      admin('/auth/v1/admin/users?per_page=200'),
      admin('/rest/v1/site_admins?select=email,role,note,added_at&order=added_at'),
    ]);
    if (!usersRes.ok || !editorsRes.ok) return bad(res, 502, 'could not read the editors list');
    const usersBody = await usersRes.json();
    const users = usersBody.users || usersBody || [];
    const byEmail = new Map(users.map((u) => [(u.email || '').toLowerCase(), u]));
    const editors = await editorsRes.json();
    res.status(200).json({
      you: me.email,
      editors: editors.map((e) => {
        const u = byEmail.get(e.email.toLowerCase());
        return {
          email: e.email, role: e.role, note: e.note, addedAt: e.added_at,
          hasAccount: !!u, lastSignIn: (u && u.last_sign_in_at) || null,
        };
      }),
    });
    return;
  }

  if (req.method !== 'POST') return bad(res, 405, 'method not allowed');

  let body;
  try { body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {}); }
  catch { return bad(res, 400, 'bad request body'); }

  const email = String(body.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, 400, 'that does not look like an email address');

  /* Nobody demotes or removes themselves through this screen. Not a
     permissions question - they are an admin either way - but the one
     admin left standing locking themselves out is a mistake this can
     refuse to make possible. */
  if (email === me.email && body.action !== 'add') {
    return bad(res, 400, 'use a second account to change your own access');
  }

  if (body.action === 'add') {
    const role = body.role === 'admin' ? 'admin' : 'editor';
    const usersRes = await admin('/auth/v1/admin/users?per_page=200');
    if (!usersRes.ok) return bad(res, 502, 'could not check existing accounts');
    const users = (await usersRes.json()).users || [];
    const already = users.find((u) => (u.email || '').toLowerCase() === email);
    if (!already) {
      const create = await admin('/auth/v1/admin/users', {
        method: 'POST',
        body: JSON.stringify({ email, email_confirm: true }),
      });
      if (!create.ok) return bad(res, 502, 'creating the account failed');
    }
    const put = await admin('/rest/v1/site_admins?on_conflict=email', {
      method: 'POST',
      headers: { Prefer: 'resolution=merge-duplicates' },
      body: JSON.stringify([{ email, role, note: 'invited ' + new Date().toISOString().slice(0, 10) }]),
    });
    if (!put.ok) return bad(res, 502, 'adding to the editors list failed');
    res.status(200).json({ ok: true });
    return;
  }

  if (body.action === 'setRole') {
    const role = body.role === 'admin' ? 'admin' : 'editor';
    const patch = await admin('/rest/v1/site_admins?email=eq.' + encodeURIComponent(email), {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
    if (!patch.ok) return bad(res, 502, 'changing the role failed');
    res.status(200).json({ ok: true });
    return;
  }

  if (body.action === 'remove') {
    const del = await admin('/rest/v1/site_admins?email=eq.' + encodeURIComponent(email), {
      method: 'DELETE',
    });
    if (!del.ok) return bad(res, 502, 'removing them failed');
    res.status(200).json({ ok: true });
    return;
  }

  return bad(res, 400, 'unknown action');
}
