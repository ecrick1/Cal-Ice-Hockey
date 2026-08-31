/**
 * Box scores for every earlier Cal season.
 *
 * REAL DATA, from the same game-summary feed the 2025-26 box scores came
 * from: every dressed player by name and jersey number with goals, assists,
 * penalty minutes and shots, plus the goaltenders' shots against and saves.
 *
 * The 2025-26 run had to match players by name, which is how it discovered
 * Simon Mantoani wearing someone else's number for seven games. These seasons
 * do not need that guesswork: the roster came from the ACHA's own roster feed
 * and carries each player's ACHA id, and so does this one. Matching on the id
 * is exact, and the two Lees stop being a problem.
 *
 * Each game is checked against the play-by-play already imported for it: the
 * skater goals in the box score must equal the goals in the report, less any
 * shootout winner, which belongs to no player's line.
 *
 * Run: node _boxhistory.mjs   ->  _boxhistory.json
 */
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const KEY = 'e6867b36742a0c9d';
const url = (id) =>
  'https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=gameSummary'
  + `&game_id=${id}&key=${KEY}&site_id=2&client_code=acha&lang=en&league_id=`;

const unwrap = (t) => {
  const s = t.trim();
  const open = s.indexOf('(');
  const body = s.startsWith('{') || s.startsWith('[') ? s : s.slice(open + 1).replace(/\)\s*;?\s*$/, '');
  return JSON.parse(body);
};

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

const pbp = JSON.parse(await readFile(path.join(dir, '_pbphistory.json'), 'utf8'));
const out = [];
const failed = [];

for (const src of pbp) {
  let j;
  try {
    j = unwrap(await fetch(url(src.id)).then((r) => r.text()));
  } catch (e) {
    failed.push(`${src.season} ${src.id}: ${e.message}`);
    continue;
  }
  const home = j.homeTeam, away = j.visitingTeam;
  if (!home || !away) { failed.push(`${src.season} ${src.id}: no teams in summary`); continue; }

  const calHome = /California-Berkeley/i.test((home.info && home.info.name) || '');
  const us = calHome ? home : away;
  const them = calHome ? away : home;

  const game = {
    id: src.id, season: src.season, seasonId: src.seasonId, date: src.date,
    us: { skaters: (us.skaters || []).map(line), goalies: (us.goalies || []).map(line) },
    them: { skaters: (them.skaters || []).map(line), goalies: (them.goalies || []).map(line) },
  };

  /* The box score against the play-by-play already imported for this game. A
     shootout winner is on the scoreboard but on nobody's line. */
  const boxGoals = game.us.skaters.reduce((n, p) => n + p.g, 0)
    + game.us.goalies.reduce((n, p) => n + p.g, 0);
  const playGoals = src.goals.filter((x) => x.team === 'us').length;
  if (boxGoals !== playGoals) {
    failed.push(`${src.season} ${src.id} ${src.date}: box ${boxGoals} goals vs play-by-play ${playGoals}`);
    continue;
  }

  out.push(game);
}

const bySeason = {};
for (const g of out) bySeason[g.season] = (bySeason[g.season] || 0) + 1;
for (const [k, v] of Object.entries(bySeason)) console.log(`${k}: ${v} box scores`);

if (failed.length) {
  console.log('\nnot imported:');
  for (const f of failed) console.log('  ' + f);
}

await writeFile(path.join(dir, '_boxhistory.json'), JSON.stringify(out), 'utf8');
console.log(`\nwrote _boxhistory.json (${out.length} games, ${failed.length} left out)`);
