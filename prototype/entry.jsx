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

  async get(key) {
    if (!sb || !SHARED.has(key)) return local.get(key);
    try {
      const { data, error } = await sb.from(TABLE).select('value').eq('key', key).maybeSingle();
      if (error) throw error;
      if (data && data.value) {
        local.set(key, data.value);          // so a later offline load still works
        return { value: data.value };
      }
      /* Nothing shared yet. Whatever this browser has is the best answer, and
         the first save will put it where everyone can see it. */
      return local.get(key);
    } catch (e) {
      console.warn('reading ' + key + ' from the database failed; using this browser\'s copy', e);
      return local.get(key);
    }
  },

  async set(key, value) {
    local.set(key, value);                   // always, so nothing is lost to a failed write
    if (!sb || !SHARED.has(key)) return;

    let rev = 0;
    try { rev = Number(JSON.parse(value).rev || 0); } catch { /* not a document with a rev */ }
    mine.add(rev);

    const { error } = await sb.from(TABLE)
      .upsert({ key, value, rev, updated_at: new Date().toISOString() }, { onConflict: 'key' });
    if (error) {
      /* Saved here but not there. Said plainly rather than swallowed: the
         difference between "saved" and "everyone can see it" is the whole
         reason for this. */
      const why = signedIn
        ? 'your account is not on the editors list'
        : 'you are not signed in';
      throw new Error('Saved on this device only — ' + why + '. (' + error.message + ')');
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
      email, options: { emailRedirectTo: window.location.origin },
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
  sb.channel('site_state')
    .on('postgres_changes',
      { event: '*', schema: 'public', table: TABLE, filter: 'key=eq.cal-hockey-site' },
      (payload) => {
        const rev = Number((payload.new || {}).rev || 0);
        if (mine.has(rev)) return;                       // our own write, echoed back
        const here = Number(JSON.parse(localStorage.getItem('cal-hockey-site') || '{}').rev || 0);
        if (rev <= here) return;
        window.dispatchEvent(new CustomEvent('cal-site-updated', { detail: { rev } }));
        if (!signedIn) window.location.reload();
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
