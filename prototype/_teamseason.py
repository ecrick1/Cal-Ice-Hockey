# -*- coding: utf-8 -*-
"""An opponent's whole season, aggregated from the league's own game summaries.

The schedule view gives a record and nothing else; the players view is a
qualified-leaders board the smaller teams never reach. But every game has a
summary with both benches on it, so walking a team's finished games and adding
up the lines gives their season exactly - from the league, automatically, with
nobody pasting anything.

It is ~25 requests, so it runs a few at a time and the answer is held for an
hour. In the real app this is a route handler with ISR, or a nightly job.
"""
import io

p = 'serve.mjs'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90])
    s = s.replace(old, new)


sub("""createServer(async (req, res) => {
  const url = (req.url ?? '/').split('?')[0];
  if (url === '/acha') return achaProxy(req, res);""",
    """/* A season's worth of summaries is expensive to build and changes slowly. */
const seasonCache = new Map();
const SEASON_TTL = 60 * 60 * 1000;

const achaJson = async (params) => {
  const q = new URLSearchParams({
    feed: 'statviewfeed', key: ACHA_KEY, site_id: '2',
    client_code: 'acha', lang: 'en', league_id: '1', ...params,
  });
  const text = await fetch(ACHA + '?' + q).then((r) => r.text());
  const t = text.trim();
  return JSON.parse(t.startsWith('(') ? t.slice(1, -1) : t);
};

async function teamSeason(req, res) {
  const q = new URL(req.url, 'http://localhost');
  const season = q.searchParams.get('season_id') ?? '';
  const team = q.searchParams.get('team') ?? '';
  if (!/^\\d+$/.test(season) || !/^\\d+$/.test(team)) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'season_id and team must be numeric' }));
    return;
  }

  const key = season + ':' + team;
  const hit = seasonCache.get(key);
  if (hit && Date.now() - hit.at < SEASON_TTL) {
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'hit' });
    res.end(hit.body);
    return;
  }

  try {
    const sched = await achaJson({ view: 'schedule', season_id: season, team });
    const holder = Array.isArray(sched) ? sched[0] : sched;
    const rows = ((holder && holder.sections) || [])
      .flatMap((sec) => (sec.data || []).map((d) => d.row));
    const ids = rows.filter((r) => /final/i.test(r.game_status || '')).map((r) => r.game_id);

    const skaters = new Map();
    const goalies = new Map();
    let i = 0;
    /* Six at a time: quick enough to serve a page, gentle enough on a feed
       that is doing this as a favour. */
    const worker = async () => {
      while (i < ids.length) {
        const id = ids[i++];
        let g;
        try { g = await achaJson({ view: 'gameSummary', game_id: id }); } catch { continue; }
        for (const side of ['homeTeam', 'visitingTeam']) {
          const T = g[side];
          if (!T || !T.info || String(T.info.id) !== String(team)) continue;
          for (const pl of T.skaters || []) {
            const k = pl.info.id;
            if (!skaters.has(k)) {
              skaters.set(k, { name: pl.info.firstName + ' ' + pl.info.lastName,
                number: pl.info.jerseyNumber, pos: pl.info.position, gp: 0, g: 0, a: 0, pim: 0 });
            }
            const r = skaters.get(k);
            r.gp++; r.g += pl.stats.goals || 0; r.a += pl.stats.assists || 0;
            r.pim += pl.stats.penaltyMinutes || 0;
          }
          for (const pl of T.goalies || []) {
            /* A backup who dressed and never faced a shot did not play. */
            const faced = (pl.stats.saves || 0) + (pl.stats.goalsAgainst || 0);
            if (!faced) continue;
            const k = pl.info.id;
            if (!goalies.has(k)) {
              goalies.set(k, { name: pl.info.firstName + ' ' + pl.info.lastName,
                number: pl.info.jerseyNumber, gp: 0, saves: 0, ga: 0, so: 0 });
            }
            const r = goalies.get(k);
            r.gp++; r.saves += pl.stats.saves || 0; r.ga += pl.stats.goalsAgainst || 0;
            if ((pl.stats.goalsAgainst || 0) === 0) r.so++;
          }
        }
      }
    };
    await Promise.all(Array.from({ length: 6 }, worker));

    const body = JSON.stringify({
      games: ids.length,
      source: 'ACHA game summaries',
      skaters: [...skaters.values()].sort((a, b) => (b.g + b.a) - (a.g + a.a)),
      goalies: [...goalies.values()].sort((a, b) => b.gp - a.gp),
    });
    seasonCache.set(key, { at: Date.now(), body });
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'miss' });
    res.end(body);
  } catch (e) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: String((e && e.message) || e) }));
  }
}

createServer(async (req, res) => {
  const url = (req.url ?? '/').split('?')[0];
  if (url === '/acha') return achaProxy(req, res);
  if (url === '/acha/team-season') return teamSeason(req, res);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('endpoint added')
