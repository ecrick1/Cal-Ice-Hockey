/**
 * Pull every season of Cal's ACHA history the league actually publishes.
 *
 * REAL DATA, from the same HockeyTech feed behind achahockey.org's own stats
 * pages - the one the 2025-26 import already used, so the shape is known and
 * the 2025-26 result can be checked against data that was verified against
 * three independent sources.
 *
 * How far back it goes is not a choice: the league's men's regular seasons in
 * this system begin at 2021-22. Anything earlier is not there to fetch, so
 * the older seasons already on the site keep whatever they were built from.
 *
 * Team ids are per season, so Cal is found by name in each rather than
 * assumed to be 241 throughout.
 *
 * Run: node _achahistory.mjs   ->  _achahistory.json
 */
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const KEY = 'e6867b36742a0c9d';
const BASE = 'https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed'
  + `&key=${KEY}&site_id=2&client_code=acha&lang=en&league_id=1`;
const CAL = /California-Berkeley/i;

/* The feed answers as JSON, sometimes wrapped in parentheses. */
const get = async (params) => {
  const t = await fetch(BASE + params).then((r) => r.text());
  const s = t.trim();
  return JSON.parse(s.startsWith('(') ? s.slice(1, -1) : s);
};

/* A statview table is sections of {headers, data:[{prop,row}]}. Only `row`
   carries values; `prop` carries link ids, which is where a player id lives. */
const rowsOf = (payload) => {
  const holder = Array.isArray(payload) ? payload[0] : payload;
  const secs = (holder && holder.sections) || [];
  return secs.map((s) => ({ title: s.title, rows: (s.data || []).map((d) => ({ ...d.row, _prop: d.prop })) }));
};

const seasons = (await get('&view=seasonsForLeague')).seasons
  /* "Women's Divisions" contains "men's Divisions", so a case-insensitive
     match on the men's name alone picks up both. */
  .filter((s) => !/women/i.test(s.name) && /men's (divisions|regular season)/i.test(s.name))
  .map((s) => ({ id: s.id, name: s.name }))
  .sort((a, b) => Number(a.id) - Number(b.id));

console.log('men\'s regular seasons in the feed:');
for (const s of seasons) console.log('  ' + s.id + '  ' + s.name);

const out = [];
for (const s of seasons) {
  const teams = (await get(`&view=teamsForSeason&season_id=${s.id}`)).teams || [];
  const cal = teams.find((t) => CAL.test(t.name || ''));
  if (!cal) { console.log(`\n${s.name}: Cal not in this season`); continue; }

  const roster = rowsOf((await get(`&view=roster&season_id=${s.id}&team_id=${cal.id}`)).roster);
  /* The schedule view takes `team`, not `team_id` - with team_id it quietly
     ignores the filter and hands back the whole league's five thousand
     games rather than erroring. */
  const schedule = rowsOf(await get(`&view=schedule&season_id=${s.id}&team=${cal.id}`));

  const players = roster
    .filter((sec) => !/coach/i.test(sec.title))
    .flatMap((sec) => sec.rows.map((r) => ({
      section: sec.title,
      id: r.player_id,
      name: r.name,
      number: r.tp_jersey_number,
      position: r.position,
      shoots: r.shoots,
      height: r.height_hyphenated,
      weight: r.w,
      hometown: r.hometown,
      rookie: r.rookie === '1',
    })));

  const staff = roster
    .filter((sec) => /coach/i.test(sec.title))
    .flatMap((sec) => sec.rows.map((r) => ({ name: r.name, role: r.position || r.role || '' })));

  const games = schedule.flatMap((sec) => sec.rows);

  out.push({ seasonId: s.id, seasonName: s.name, teamId: cal.id, players, staff, games });
  console.log(`\n${s.name}: ${players.length} players, ${staff.length} staff, ${games.length} games`);
  if (games[0]) console.log('  a game row: ' + JSON.stringify(games[0]).slice(0, 300));
}

await writeFile(path.join(dir, '_achahistory.json'), JSON.stringify(out, null, 1), 'utf8');
console.log(`\nwrote _achahistory.json (${out.length} seasons)`);
