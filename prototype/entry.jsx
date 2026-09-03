import { createRoot } from 'react-dom/client';
import { createClient } from '@supabase/supabase-js';
import CalIceHockey from '../reference/cal-ice-hockey-app.jsx';

/**
 * The prototype was written for an artifact host that provides an async
 * `window.storage`. Everything it knows goes through that one pair of
 * functions, which is why the whole site can be moved somewhere shared
 * without the app being rewritten: point get and set at a database and
 * "Publish" starts meaning what it says.
 *
 * Backed by localStorage, the site was private to a browser. Every visitor
 * held their own copy, so an edit could not reach anybody - the console's
 * own dialog said "will change for everyone" and was wrong.
 *
 * Two stores now, and which one a key uses is a decision about who should
 * see it rather than a detail:
 *
 *   shared  - the site itself. Public to read, an allow-list to write.
 *   local   - everything private to one person or one browser: view
 *             preferences, a parked draft, and recruit submissions.
 *
 * Recruit submissions stay local deliberately. They are somebody's name,
 * email and phone number, and the shared row is readable by anyone with the
 * address of the site. They need a table of their own with public insert and
 * nothing else, which is what the migrations already describe; until they
 * have it, publishing them would be worse than not sharing them.
 */

const URL_ = process.env.SUPABASE_URL || '';
const KEY_ = process.env.SUPABASE_ANON_KEY || '';
const TABLE = 'site_state';

/* Public content, kept in the database. Everything not named here stays in
   this browser. */
const SHARED = new Set(['cal-hockey-site', 'cal-hockey-alumni']);

const local = {
  get(key) {
    const value = localStorage.getItem(key);
    return value === null ? null : { value };
  },
  set(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { console.warn('local mirror failed', e); }
  },
};

const sb = URL_ && KEY_
  ? createClient(URL_, KEY_, { auth: { persistSession: true, autoRefreshToken: true } })
  : null;

/* Revisions this tab wrote, so the realtime feed does not report our own
   work back to us as somebody else's news. */
const mine = new Set();
let signedIn = false;

window.storage = {
  /* True when the site is coming from the database. The app uses it to leave
     the shipped file alone: a static build is a fallback for when there is no
     database, not an authority over one. */
  remote: !!sb,

  /**
   * Ask what the revision is before asking for four megabytes.
   *
   * The document is large and mostly unchanged between visits, so fetching it
   * every load put the whole site behind a spinner for no reason. The rev sits
   * in a column of its own precisely so this question is cheap: a few bytes
   * decide whether the rest is worth asking for.
   */
  async get(key) {
    if (!sb || !SHARED.has(key)) return local.get(key);
    const here = local.get(key);
    let hereRev = -1;
    try { hereRev = Number(JSON.parse(here.value).rev || 0); } catch { /* none or unreadable */ }
    try {
      const { data, error } = await sb.from(TABLE).select('rev').eq('key', key).maybeSingle();
      if (error) throw error;
      if (!data) return here;                    // nothing shared yet; this copy is the best one
      if (Number(data.rev || 0) <= hereRev) return here;   // already current

      const full = await sb.from(TABLE).select('value').eq('key', key).maybeSingle();
      if (full.error) throw full.error;
      if (full.data && full.data.value) {
        local.set(key, full.data.value);         // so a later load, or an offline one, is instant
        return { value: full.data.value };
      }
      return here;
    } catch (e) {
      console.warn('reading ' + key + ' from the database failed; using this browser\'s copy', e);
      return here;
    }
  },

  async set(key, value) {
    local.set(key, value);                   // always, so nothing is lost to a failed write
    if (!sb || !SHARED.has(key)) return;

    /* A visitor is not publishing. The app saves its own housekeeping back on
       every load - a document it has just normalised, an update it has just
       taken - and those writes are not edits anybody made. Sending them was
       a request certain to be refused, on every page view, for everyone who
       was only reading. The local mirror is the whole destination here. */
    if (!signedIn) return;

    let rev = 0;
    try { rev = Number(JSON.parse(value).rev || 0); } catch { /* not a document with a rev */ }
    mine.add(rev);

    const { error } = await sb.from(TABLE)
      .upsert({ key, value, rev, updated_at: new Date().toISOString() }, { onConflict: 'key' });
    if (error) {
      /* Saved here but not there, and only reachable by someone who really was
         editing. Said plainly rather than swallowed: the difference between
         "saved" and "everyone can see it" is the whole reason for this. */
      throw new Error('Saved on this device only — the database refused the write. ('
        + error.message + ')');
    }
  },
};

/**
 * Sign-in, for the console.
 *
 * A magic link rather than a password: the console's passcode was compared in
 * the browser against a constant in the bundle, which was fine while the data
 * was your own and is not fine now that a write reaches everybody.
 */
window.auth = {
  available: !!sb,
  user: null,
  async signIn(email) {
    if (!sb) throw new Error('No database configured.');
    const { error } = await sb.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: window.location.origin,
        /* No account, no email. Without this, typing any address at all makes
           the site create an account and send to it - so anybody could have
           the club's site email a stranger, and the only thing standing
           between them and editing was a second check further in. Access
           starts with an invitation now, and an invitation is an account. */
        shouldCreateUser: false,
      },
    });
    if (error) {
      /* Supabase says "signups not allowed", which is true and reads like a
         fault in the site rather than the intended answer. */
      if (/signups? not allowed|not allowed for otp/i.test(error.message)) {
        throw new Error('That address has not been given access. Ask someone who edits '
          + 'the site to add it.');
      }
      throw new Error(error.message);
    }
  },

  /**
   * The same sign-in, typed rather than clicked.
   *
   * A link is a one-time token in a URL, and plenty of things follow a URL
   * before a person does - mail scanners, link previews, a second click after
   * a first that went nowhere. Any of them spends the token, and what the
   * person then sees is that it has expired, which is true and useless.
   *
   * The code in the same email cannot be spent by anything that merely reads
   * the message, and it does not care which device it is typed on.
   */
  async verifyCode(email, token) {
    if (!sb) throw new Error('No database configured.');
    const { error } = await sb.auth.verifyOtp({
      email, token: String(token).replace(/\s+/g, ''), type: 'email',
    });
    if (error) throw new Error(error.message);
  },
  async signOut() { if (sb) await sb.auth.signOut(); },
  onChange(fn) {
    if (!sb) return () => {};
    const { data } = sb.auth.onAuthStateChange((_e, session) => {
      window.auth.user = (session && session.user) || null;
      signedIn = !!window.auth.user;
      fn(window.auth.user);
    });
    return () => data.subscription.unsubscribe();
  },
};

/**
 * Somebody else published.
 *
 * A viewer is reading a page that is now out of date, so it is reloaded. An
 * editor is not: they may be halfway through something of their own, and
 * taking that away to show them a change they did not make would be the
 * worse of the two. They get told instead.
 */
if (sb) {
  let fetching = false;
  sb.channel('site_state')
    .on('postgres_changes',
      { event: '*', schema: 'public', table: TABLE, filter: 'key=eq.cal-hockey-site' },
      async (payload) => {
        const rev = Number((payload.new || {}).rev || 0);
        if (mine.has(rev)) return;                       // our own write, echoed back
        const here = Number(JSON.parse(localStorage.getItem('cal-hockey-site') || '{}').rev || 0);
        if (rev <= here) return;
        /* Goals arrive in bursts and each one is a row change. One fetch at a
           time, and the last rev wins - a second request racing the first
           would only be a slower way to the same answer. */
        if (fetching) return;
        fetching = true;
        try {
          const { data, error } = await sb.from(TABLE).select('value')
            .eq('key', 'cal-hockey-site').maybeSingle();
          if (error || !data || !data.value) return;
          local.set('cal-hockey-site', data.value);
          window.dispatchEvent(new CustomEvent('cal-site-updated', {
            detail: { rev, value: data.value },
          }));
        } finally {
          fetching = false;
        }
      })
    .subscribe();
}

(async () => {
  if (sb) {
    const { data } = await sb.auth.getSession();
    window.auth.user = (data.session && data.session.user) || null;
    signedIn = !!window.auth.user;
  }
  createRoot(document.getElementById('root')).render(<CalIceHockey />);
})();
