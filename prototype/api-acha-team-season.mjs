/**
 * A team's season, totalled from the ACHA's own game summaries.
 *
 * The feed has no per-season player totals, only per-game ones, so a season is
 * one request per finished game added up. serve.mjs does this for the dev
 * server; the published site had nothing, and the requests were being answered
 * with the site's own HTML.
 *
 * The work is real - thirty games is thirty upstream requests - so the answer
 * is cached hard at the edge. A team's season does not change between two
 * people opening the same preview.
 */
const ACHA = 'https://lscluster.hockeytech.com/feed/index.php';
const ACHA_KEY = 'e6867b36742a0c9d';

const achaJson = async (params) => {
  const q = new URLSearchParams({
    feed: 'statviewfeed', key: ACHA_KEY, site_id: '2',
    client_code: 'acha', lang: 'en', league_id: '1', ...params,
  });
  const text = await fetch(ACHA + '?' + q).then((r) => r.text());
  const t = text.trim();
  return JSON.parse(t.startsWith('(') ? t.slice(1, -1) : t);
};

export default async function handler(req, res) {
  const q = new URL(req.url, 'http://localhost').searchParams;
  const season = q.get('season_id') ?? '';
  const team = q.get('team') ?? '';
  if (!/^\d+$/.test(season) || !/^\d+$/.test(team)) {
    res.status(400).json({ error: 'season_id and team must be numeric' });
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
    /* Six at a time: quick enough to answer inside a function's lifetime,
       gentle enough on a feed that is doing this as a favour. */
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
            /* The feed carries a placeholder line with no id and no name -
               goals the scorekeeper never attributed to anybody. Real in the
               team's total, not a player, so not in a list of players. */
            if (!k || String(k) === '0' || !pl.info.lastName) continue;
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
            if (!k || String(k) === '0' || !pl.info.lastName) continue;
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

    /* An hour at the edge, and a day of serving the stale copy while a fresh
       one is fetched behind it - so nobody waits for thirty requests twice. */
    res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');
    res.status(200).json({
      games: ids.length,
      source: 'ACHA game summaries',
      skaters: [...skaters.values()].sort((a, b) => (b.g + b.a) - (a.g + a.a)),
      goalies: [...goalies.values()].sort((a, b) => b.gp - a.gp),
    });
  } catch (e) {
    res.status(502).json({ error: String((e && e.message) || e) });
  }
}
