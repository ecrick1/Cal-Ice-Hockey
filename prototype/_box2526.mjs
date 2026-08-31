/**
 * Pull the 2025-26 per-game box scores from the ACHA's game-summary feed.
 *
 * REAL DATA. The game centre on achahockey.org is a HockeyTech StatView
 * widget backed by a JSON feed, and that feed carries what the text reports
 * do not: every dressed player, by first and last name and jersey number,
 * with goals, assists, penalty minutes and shots for that game, plus the
 * goaltenders' shots against and saves.
 *
 * Run: node _box2526.mjs   (after _pbp2526.mjs, which supplies the game ids)
 *
 * It writes _box2526.json only if the season rebuilt from thirty box scores
 * agrees with the ACHA's own season stats page. That is the whole point of
 * the check: if it agrees, these per-game numbers can safely replace the
 * season totals on the roster row, because they add up to the same thing.
 */
import { writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const CAL = 'MD2 University of California-Berkeley';
const KEY = 'e6867b36742a0c9d';

const url = (id) =>
  'https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=gameSummary'
  + `&game_id=${id}&key=${KEY}&site_id=2&client_code=acha&lang=en&league_id=`;

/* The feed answers as JSONP when a callback is asked for and as bare JSON
   when it is not, but it still wraps in parentheses often enough to strip. */
const unwrap = (t) => {
  const s = t.trim();
  const open = s.indexOf('(');
  const body = s.startsWith('{') || s.startsWith('[') ? s : s.slice(open + 1).replace(/\)\s*;?\s*$/, '');
  return JSON.parse(body);
};

const pbp = JSON.parse(await readFile(path.join(dir, '_pbp2526.json'), 'utf8'));

const line = (p) => ({
  id: p.info.id,
  first: p.info.firstName,
  last: p.info.lastName,
  number: p.info.jerseyNumber,
  pos: p.info.position,
  g: p.stats.goals || 0,
  a: p.stats.assists || 0,
  pim: p.stats.penaltyMinutes || 0,
  shots: p.stats.shots || 0,
  starting: !!p.starting,
  ...(p.stats.saves !== undefined
    ? { saves: p.stats.saves || 0, ga: p.stats.goalsAgainst || 0,
        shotsAgainst: p.stats.shotsAgainst || 0, toi: p.stats.timeOnIce || '' }
    : {}),
});

const games = [];
for (const src of pbp) {
  const j = unwrap(await fetch(url(src.id)).then((r) => r.text()));
  const calHome = j.homeTeam.info.name === CAL;
  const us = calHome ? j.homeTeam : j.visitingTeam;
  const them = calHome ? j.visitingTeam : j.homeTeam;
  games.push({
    id: src.id, date: src.date, opponent: src.opponent,
    us: { skaters: us.skaters.map(line), goalies: us.goalies.map(line) },
    them: { skaters: them.skaters.map(line), goalies: them.goalies.map(line) },
  });
}

/* ---- Does thirty box scores add up to the season page? ---- */
const season = new Map();
for (const g of games) {
  for (const p of [...g.us.skaters, ...g.us.goalies]) {
    const k = p.first + ' ' + p.last;
    const t = season.get(k) || { gp: 0, g: 0, a: 0, pim: 0, saves: 0, ga: 0 };
    t.gp++; t.g += p.g; t.a += p.a; t.pim += p.pim;
    t.saves += p.saves || 0; t.ga += p.ga || 0;
    season.set(k, t);
  }
}
const totals = [...season.values()].reduce((t, x) => ({
  g: t.g + x.g, a: t.a + x.a, pim: t.pim + x.pim, saves: t.saves + x.saves, ga: t.ga + x.ga,
}), { g: 0, a: 0, pim: 0, saves: 0, ga: 0 });

/* The ACHA season pages say the team scored 180 and conceded 99. Neither is
   the number a box score sums to, and both differences are the point:
     - a shootout winner counts in the team's goals for but goes on no
       player's line, so the skaters add up to 180 minus the shootouts;
     - an empty-net goal is charged to no goaltender, so the keepers add up
       to 99 minus the empty-netters.
   Both are counted from the play data rather than assumed. */
const shootoutGoals = pbp.filter((g) => g.shootout).length;
const emptyNet = pbp.reduce((n, g) =>
  n + g.goals.filter((x) => x.team === 'them' && x.strength === 'EN').length, 0);

const EXPECT = { g: 180 - shootoutGoals, saves: 839, ga: 99 - emptyNet, pim: 560 };
const problems = [];
if (totals.g !== EXPECT.g) problems.push(`skater goals ${totals.g}, expected ${EXPECT.g} (180 less ${shootoutGoals} shootout)`);
if (totals.saves !== EXPECT.saves) problems.push(`saves ${totals.saves}, season page says ${EXPECT.saves}`);
if (totals.ga !== EXPECT.ga) problems.push(`goals against ${totals.ga}, expected ${EXPECT.ga} (99 less ${emptyNet} empty-net)`);
if (totals.pim !== EXPECT.pim) problems.push(`penalty minutes ${totals.pim}, season page says ${EXPECT.pim}`);

console.log(`${games.length} box scores`);
console.log('rebuilt season:', JSON.stringify(totals));
const lees = [...season.entries()].filter(([k]) => /\bLee$/.test(k));
console.log('the two Lees:', lees.map(([k, v]) => `${k} ${v.gp}GP ${v.g}G ${v.a}A ${v.pim}PIM`).join('  |  '));

if (problems.length) {
  console.error('\nNOT WRITTEN:');
  for (const p of problems) console.error('  ' + p);
  process.exit(1);
}

await writeFile(path.join(dir, '_box2526.json'), JSON.stringify(games), 'utf8');
console.log('\nagrees with the season page - wrote _box2526.json');
