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

/* Set when a write reached this browser and not the database, cleared when one
   gets through. It is the only honest reason for a local copy to be newer than
   the shared one, and reading it is how a load tells "work waiting here" apart
   from "this browser has drifted ahead and should be corrected". Without it,
   the two look identical and the safe-looking choice - keep what is local -
   pins the browser to a copy nobody else can see. */
const UNSENT = 'cal-hockey-unsent';
const unsent = () => {
  try { return localStorage.getItem(UNSENT) === '1'; } catch { return false; }
};
const markUnsent = (yes) => {
  try {
    if (yes) localStorage.setItem(UNSENT, '1');
    else localStorage.removeItem(UNSENT);
  } catch { /* private mode; the flag is an optimisation, not a guarantee */ }
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

      /* Equal revisions mean equal documents, so there is nothing to fetch.
         Anything else and the database wins - including a local copy that
         claims to be NEWER, which for somebody who is not signed in should be
         impossible and is the one case that used to be treated as current.
         A write from a visitor stops at the local mirror by design, and the
         app stamps a rev when it publishes a parked draft on load, so a
         browser could end up one ahead of a database it had never written to.
         From then on it answered every check with "already current" and never
         fetched again: pinned, silently and permanently, to a copy nobody else
         could see.

         An editor is the exception. Their local copy outranking the database
         means a write was refused and is waiting on this device - the "saved
         here only" case - and fetching over it would throw the work away. */
      const theirs = Number(data.rev || 0);
      if (theirs === hereRev) return here;
      if (theirs < hereRev && unsent()) return here;

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

  /**
   * The revision, without the document.
   *
   * A save checks whether anybody else has written since this screen was
   * loaded, and it was answering that by fetching the whole site - a megabyte
   * and a half, on every goal and every clock stop. The rev is a column of its
   * own precisely so the question can be asked for a few bytes.
   */
  async rev(key) {
    if (sb && SHARED.has(key)) {
      try {
        const { data, error } = await sb.from(TABLE).select('rev').eq('key', key).maybeSingle();
        if (error) throw error;
        return data ? Number(data.rev || 0) : null;
      } catch { return null; }   // unreachable database; the caller treats it as "unknown"
    }
    const here = local.get(key);
    if (!here) return null;
    try { return Number(JSON.parse(here.value).rev || 0); } catch { return null; }
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
    if (!error) markUnsent(false);
    if (error) {
      markUnsent(true);
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

  /**
   * The current session's own token, for the one screen that has to prove
   * who is asking rather than just who is signed in.
   *
   * Everything else here writes through `window.storage`, which the RLS
   * policies gate by row - anyone signed in can reach it, and "signed in"
   * has always been the whole bar. Deciding who else gets to sign in is a
   * question the browser cannot be trusted to answer honestly on its own,
   * so it is asked of a server instead, and the server needs this token to
   * know who is actually asking - a user who was never on the editors list
   * calling the console's own code cannot claim to be one by skipping this.
   */
  async token() {
    if (!sb) return null;
    const { data } = await sb.auth.getSession();
    return (data.session && data.session.access_token) || null;
  },
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
  const revHere = () => {
    try { return Number(JSON.parse(localStorage.getItem('cal-hockey-site') || '{}').rev || 0); }
    catch { return 0; }
  };

  /**
   * Fetch the site and hand it to the page.
   *
   * One request at a time, but a change that arrives during one is remembered
   * and fetched after it rather than dropped. That distinction is the whole
   * of live scoring: goals, penalties and clock stops arrive in bursts, and
   * dropping the ones that land mid-request means the burst ends with the
   * page holding whatever happened to arrive first - stale until something
   * else changes, which during a quiet period could be the rest of the game.
   */
  let fetching = false;
  let again = false;
  const pull = async () => {
    if (fetching) { again = true; return; }
    fetching = true;
    try {
      do {
        again = false;
        const { data, error } = await sb.from(TABLE).select('value,rev')
          .eq('key', 'cal-hockey-site').maybeSingle();
        if (error || !data || !data.value) return;
        if (Number(data.rev || 0) <= revHere()) continue;
        local.set('cal-hockey-site', data.value);
        window.dispatchEvent(new CustomEvent('cal-site-updated', {
          detail: { rev: Number(data.rev || 0), value: data.value },
        }));
      } while (again);
    } finally {
      fetching = false;
    }
  };

  const channel = sb.channel('site_state')
    .on('postgres_changes',
      { event: '*', schema: 'public', table: TABLE, filter: 'key=eq.cal-hockey-site' },
      (payload) => {
        const rev = Number((payload.new || {}).rev || 0);
        if (mine.has(rev)) return;                       // our own write, echoed back
        if (rev <= revHere()) return;
        pull();
      });
  channel.subscribe();

  /**
   * And a heartbeat, because a socket is not a promise.
   *
   * A realtime connection drops - a phone sleeping in a pocket at a rink, a
   * network changing, a proxy giving up on an idle socket - and a page that
   * was relying on it alone goes quiet without saying so. Asking for the rev
   * is a few bytes and settles it: the document is only fetched when the
   * number has actually moved.
   *
   * Faster while a game is being scored, because that is when a minute of
   * silence is a minute of the wrong score.
   */
  const beat = async () => {
    if (document.visibilityState === 'hidden') return;
    try {
      const { data } = await sb.from(TABLE).select('rev').eq('key', 'cal-hockey-site').maybeSingle();
      if (data && Number(data.rev || 0) > revHere()) pull();
    } catch { /* offline; the next beat will do */ }
  };
  const liveNow = () => {
    try {
      const doc = JSON.parse(localStorage.getItem('cal-hockey-site') || '{}');
      return Object.values(doc.seasons || {}).some((s) =>
        (s.schedule || []).some((g) => g.live && g.live.running));
    } catch { return false; }
  };
  let timer = null;
  const schedule = () => {
    clearTimeout(timer);
    timer = setTimeout(async () => { await beat(); schedule(); }, liveNow() ? 15000 : 60000);
  };
  schedule();
  /* Coming back to a tab that has been away is the moment a stale page is
     most obvious, so it checks then rather than waiting for the next beat. */
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') { beat(); schedule(); }
  });
}

(async () => {
  if (sb) {
    const { data } = await sb.auth.getSession();
    window.auth.user = (data.session && data.session.user) || null;
    signedIn = !!window.auth.user;
  }
  createRoot(document.getElementById('root')).render(<CalIceHockey />);
})();
