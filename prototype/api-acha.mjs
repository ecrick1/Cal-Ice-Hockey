/**
 * The ACHA's own feed, proxied — the deployed half.
 *
 * serve.mjs does this for the dev server; nothing did it for the published
 * site. The feed sends no CORS headers, so a browser cannot read it directly,
 * and a static folder has nowhere to put a proxy. The requests went to /acha,
 * matched the catch-all rewrite that makes client-side routing work, and came
 * back as the site's own HTML with a 200 on it. So every call succeeded and
 * every parse failed, quietly, only in production.
 *
 * Same shape as the dev version on purpose: same path, same allowed views,
 * same unwrapping, so the page code cannot tell which one it is talking to.
 */
const ACHA = 'https://lscluster.hockeytech.com/feed/index.php';
const ACHA_KEY = 'e6867b36742a0c9d';

/* Only the views this site asks for. An open relay to any upstream URL is not
   what a proxy on a public origin should be. */
const VIEWS = new Set(['seasonsForLeague', 'teamsForSeason', 'schedule', 'roster', 'gameSummary']);

export default async function handler(req, res) {
  const q = new URL(req.url, 'http://localhost').searchParams;
  const view = q.get('view') ?? '';
  if (!VIEWS.has(view)) {
    res.status(400).json({ error: 'unknown view' });
    return;
  }

  const params = new URLSearchParams({
    feed: 'statviewfeed', view, key: ACHA_KEY,
    site_id: '2', client_code: 'acha', lang: 'en', league_id: '1',
  });
  /* Numeric ids only — nothing typed by a visitor reaches the upstream. */
  for (const k of ['season_id', 'team_id', 'team', 'game_id']) {
    const v = q.get(k);
    if (v && /^\d+$/.test(v)) params.set(k, v);
  }

  try {
    const text = await fetch(ACHA + '?' + params).then((r) => r.text());
    /* The feed sometimes wraps its JSON in parentheses. Unwrapped here so no
       caller has to know that. */
    const t = text.trim();
    const body = t.startsWith('(') ? t.slice(1, -1) : t;
    JSON.parse(body);                       // refuse to pass on what will not parse
    /* A team's record does not change faster than five minutes, and this keeps
       a page refresh from hammering somebody else's server. */
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
    res.setHeader('Content-Type', 'application/json');
    res.status(200).send(body);
  } catch (e) {
    res.status(502).json({ error: String((e && e.message) || e) });
  }
}
