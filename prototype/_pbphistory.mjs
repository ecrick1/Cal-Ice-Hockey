/**
 * Play-by-play for every earlier Cal season the ACHA publishes.
 *
 * REAL DATA. Same source and same parser as the 2025-26 import: each game on
 * the schedule links to a HockeyTech text report carrying every goal with its
 * scorer, assists, time and strength, every penalty, shots by period, the
 * goaltenders and the shootout. `_achahistory.json` already holds the game
 * ids, so this walks them.
 *
 * Two things differ from the 2025-26 run and both matter:
 *
 *   1. The team is written "M2 University of California-Berkeley" in the
 *      older seasons and "MD2 ..." from 2023-24, so which side is Cal is read
 *      from the header rather than matched against a constant.
 *   2. There is no season-totals page to reconcile against for these years,
 *      so the check is per game: the goals parsed must equal that game's
 *      final score, allowing the one-goal difference a shootout creates.
 *      A game that fails is reported and left out rather than half-imported.
 *
 * Run: node _pbphistory.mjs   ->  _pbphistory.json
 */
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const url = (id) =>
  `https://lscluster.hockeytech.com/game_reports/text-game-report.php?client_code=acha&game_id=${id}&lang_id=1`;

const flatten = (html) => html
  .replace(/<[^>]*>/g, ' ')
  .replace(/&nbsp;/g, ' ')
  .replace(/&amp;/g, '&')
  .replace(/&#39;|&apos;/g, "'")
  .replace(/\s+/g, ' ')
  .trim();

const MONTHS = { January: 1, February: 2, March: 3, April: 4, May: 5, June: 6,
  July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };

function parse(id, raw) {
  const t = raw.replace(/^Official statistics powered by LeagueStat\.com\s*/, '');
  /* Older reports write the header more loosely than 2025-26's did: a score
     can carry "(OT)" after it, and the status runs to "Final OT1" or a
     forfeit rather than a fixed set of words. The weekday that opens the date
     is the reliable end of it. */
  const head = t.match(
    /^(.+?)\s+(\d+)(?:\s*\([A-Z]+\d*\))?\s+at\s+(.+?)\s+(\d+)(?:\s*\([A-Z]+\d*\))?\s*-\s*Status:\s*(.+?)\s+(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday),/);
  if (!head) return { id, error: 'no header' };
  const [, vName, vG, hName, hG, status] = head;
  const calHome = /California-Berkeley/i.test(hName);
  const calName = calHome ? hName.trim() : vName.trim();

  const dm = t.match(/(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})/);
  const date = dm
    ? `${dm[3]}-${String(MONTHS[dm[1]]).padStart(2, '0')}-${String(+dm[2]).padStart(2, '0')}`
    : null;

  const marks = [...t.matchAll(/(\d)(?:st|nd|rd|th) (OT )?Period-/g)];
  const goals = [];
  const pens = [];
  marks.forEach((m, i) => {
    const period = m[2] ? 'OT' : m[1];
    const body = t.slice(m.index + m[0].length, i + 1 < marks.length ? marks[i + 1].index : t.length);
    const [scoring, penalties = ''] = body.split(/Penalties-/);

    const gre = /(\d+),\s*([^,]+?),\s*([A-Za-z'\-. ]+?)\s+\d+\s*(?:\(([^)]*)\)\s*,)?\s*(\d+:\d\d)(?:\s*\(([A-Z]{2})\))?/g;
    let g;
    while ((g = gre.exec(scoring)) !== null) {
      goals.push({
        period, team: g[2].trim() === calName ? 'us' : 'them',
        scorer: g[3].trim(),
        assists: (g[4] || '').split(',').map((x) => x.trim()).filter(Boolean),
        at: g[5], strength: g[6] || 'EV',
      });
    }

    if (!/No Penalties/.test(penalties)) {
      const pre = /([A-Za-z'\-. ]+?)\s+(M\d?[a-z]+)\s*\(([^)]*)\),\s*(\d+:\d\d)/g;
      let p;
      while ((p = pre.exec(penalties)) !== null) {
        const who = p[1].trim();
        pens.push({
          period, code: p[2],
          player: who.replace(/^served by\s+/i, ''),
          bench: /^served by/i.test(who),
          infractions: p[3].split(',').map((x) => x.trim()).filter(Boolean),
          at: p[4],
        });
      }
    }
  });

  let shootout = null;
  const som = t.match(/Shootout\s*-\s*(.+?)\.\s*(?:Shots on Goal|Power Play|Goalies)/);
  if (som) {
    shootout = { us: [], them: [] };
    for (const sd of [...som[1].matchAll(/([A-Za-z][^,(]*?)\s+(\d+)\s*\(([^)]*)\)/g)]) {
      const side = sd[1].trim() === calName ? 'us' : 'them';
      for (const a of sd[3].split(',')) {
        const hit = a.trim().match(/^(.+?)\s+(G|NG)$/);
        if (hit) shootout[side].push({ name: hit[1].trim(), scored: hit[2] === 'G' });
      }
    }
  }

  const shots = {};
  const sm = t.match(/Shots on Goal-(.+?)(?:Power Play|Goalies)/);
  if (sm) for (const seg of sm[1].split(/\.\s*/)) {
    const x = seg.match(/^(.+?)\s+(\d+(?:-\d+)+)$/);
    if (x) shots[x[1].trim() === calName ? 'us' : 'them'] = x[2].split('-').map(Number);
  }

  const keepers = [];
  const km = t.match(/Goalies-(.+?)(?:A-\d|Referees)/);
  if (km) {
    const seg = km[1];
    /* Split by team first: a second goaltender carries no team prefix, so
       scanning the whole section at once files them under the wrong side. */
    const teams = [...seg.matchAll(/(M[D]?\d [^,]+?),\s*/g)];
    teams.forEach((tm, i) => {
      const body = seg.slice(tm.index + tm[0].length, i + 1 < teams.length ? teams[i + 1].index : seg.length);
      const team = tm[1].trim() === calName ? 'us' : 'them';
      const gre = /([A-Za-z'\-. ]+?)\s+\d+-\d+-\d+-\d+\s*\((\d+) shots-(\d+) saves\)/g;
      let k;
      while ((k = gre.exec(body)) !== null) {
        keepers.push({ team, name: k[1].trim(), shots: +k[2], saves: +k[3] });
      }
    });
  }

  return {
    id, date, status, calHome, calName,
    opponent: (calHome ? vName : hName).replace(/^M[D]?\d\s+/, ''),
    final: { us: calHome ? +hG : +vG, them: calHome ? +vG : +hG },
    goals, pens, shots, keepers, shootout,
  };
}

const history = JSON.parse(await readFile(path.join(dir, '_achahistory.json'), 'utf8'));
const out = [];
const failed = [];

for (const season of history) {
  /* 2025-26 already has a verified play-by-play; 2026-27 has not been played. */
  if (/2025-2026|2026-27/.test(season.seasonName)) continue;
  const played = season.games.filter((g) => /final|forfeit/i.test(g.game_status || ''));
  if (!played.length) continue;

  let ok = 0;
  for (const g of played) {
    let parsed;
    try {
      const res = await fetch(url(g.game_id));
      if (!res.ok) { failed.push(`${season.seasonName} ${g.game_id}: HTTP ${res.status}`); continue; }
      parsed = parse(g.game_id, flatten(await res.text()));
    } catch (e) {
      failed.push(`${season.seasonName} ${g.game_id}: ${e.message}`);
      continue;
    }
    if (parsed.error) { failed.push(`${season.seasonName} ${g.game_id}: ${parsed.error}`); continue; }

    /* The one check available without season totals: the goals in the report
       must add up to the score on the report. A shootout puts a goal on the
       board that appears in no period, so it is short by exactly one. */
    const cu = parsed.goals.filter((x) => x.team === 'us').length;
    const ct = parsed.goals.filter((x) => x.team === 'them').length;
    const so = /SO/.test(parsed.status) || !!parsed.shootout;
    const diff = Math.abs(cu - parsed.final.us) + Math.abs(ct - parsed.final.them);
    const good = /forfeit/i.test(parsed.status) ? true : so ? diff === 1 : diff === 0;
    if (!good) {
      failed.push(`${season.seasonName} ${g.game_id} ${parsed.date}: parsed ${cu}-${ct} vs final ${parsed.final.us}-${parsed.final.them}`);
      continue;
    }

    out.push({ season: season.seasonName, seasonId: season.seasonId, ...parsed });
    ok++;
  }
  console.log(`${season.seasonName}: ${ok}/${played.length} reports parsed and reconciled`);
}

if (failed.length) {
  console.log('\nnot imported:');
  for (const f of failed) console.log('  ' + f);
}

await writeFile(path.join(dir, '_pbphistory.json'), JSON.stringify(out), 'utf8');
console.log(`\nwrote _pbphistory.json (${out.length} games, ${failed.length} left out)`);
