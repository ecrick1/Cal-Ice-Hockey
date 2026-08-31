/**
 * Pull the 2025-26 play-by-play from the ACHA's text game reports.
 *
 * REAL DATA. Each game on the ACHA schedule links to a HockeyTech text report
 * that carries every goal (scorer, assists, time, strength), every penalty,
 * shots by period, power-play opportunities and the goaltenders' lines. This
 * fetches all thirty, parses them, and writes _pbp2526.json for the browser
 * importer to apply.
 *
 * Run: node _pbp2526.mjs
 *
 * It verifies as it goes and refuses to write a file that does not reconcile:
 *   - goals parsed per game == that game's final score
 *   - shots by period == the total on the same line
 *   - goals against per goaltender + empty-net goals == goals conceded
 *   - power-play goals flagged in the plays == the Power Play Opportunities line
 *   - season totals rebuilt from all thirty == the ACHA stats pages (180-99, 20-10-0)
 *
 * Two things the reports cannot give us, both reported rather than guessed:
 *   - Players are surnames only, so "Lee" is either Jason or Ryan. Those are
 *     left unresolved for the importer to handle.
 *   - Penalty minutes are not printed, only the infraction.
 */
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const CAL = 'MD2 University of California-Berkeley';

const IDS = ['30001','30028','28120','28121','28122','28123','28124','28125','28126','28127',
  '27800','27801','29948','29949','28128','28129','29508','25097','29490','30908',
  '27728','29706','29711','28093','28130','28131','30016','31233','31280','31305'];

const url = (id) =>
  `https://lscluster.hockeytech.com/game_reports/text-game-report.php?client_code=acha&game_id=${id}&lang_id=1`;

/* The report is HTML wrapping plain text; strip tags and collapse space. */
const flatten = (html) => html
  .replace(/<[^>]*>/g, ' ')
  .replace(/&nbsp;/g, ' ')
  .replace(/&amp;/g, '&')
  .replace(/&#39;|&apos;/g, "'")
  .replace(/\s+/g, ' ')
  .trim();

function parse(id, raw) {
  const t = raw.replace(/^Official statistics powered by LeagueStat\.com\s*/, '');
  const head = t.match(/^(.+?) (\d+)(?: \(SO\))? at (.+?) (\d+) - Status: (Final(?: SO| OT)?)/);
  if (!head) throw new Error(`${id}: no header`);
  const [, vName, vG, hName, hG, status] = head;
  const calHome = hName === CAL;

  /* "Friday, September 26, 2025 - Sharks Ice at San Jose" - matching on the
     date is safer than trusting two lists to stay in the same order. */
  const dm = t.match(/(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})/);
  const MONTHS = { January:1, February:2, March:3, April:4, May:5, June:6, July:7,
    August:8, September:9, October:10, November:11, December:12 };
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

    /* "7, TEAM, Fung 11 (Collins, Lee), 8:22 (PP)." - and the unassisted
       form, which carries no brackets at all: "7, TEAM, Mizuno 2 10:13 (SH)." */
    const gre = /(\d+),\s*([^,]+?),\s*([A-Za-z'\-. ]+?)\s+\d+\s*(?:\(([^)]*)\)\s*,)?\s*(\d+:\d\d)(?:\s*\(([A-Z]{2})\))?/g;
    let g;
    while ((g = gre.exec(scoring)) !== null) {
      goals.push({
        period, team: g[2].trim() === CAL ? 'us' : 'them',
        scorer: g[3].trim(),
        assists: (g[4] || '').split(',').map((x) => x.trim()).filter(Boolean),
        at: g[5], strength: g[6] || 'EV',
      });
    }

    if (!/No Penalties/.test(penalties)) {
      const pre = /([A-Za-z'\-. ]+?)\s+(M2[a-z]+)\s*\(([^)]*)\),\s*(\d+:\d\d)/g;
      let p;
      while ((p = pre.exec(penalties)) !== null) {
        const who = p[1].trim();
        pens.push({
          period, team: p[2] === 'M2ucb' ? 'us' : 'them',
          player: who.replace(/^served by\s+/i, ''),
          bench: /^served by/i.test(who),
          infractions: p[3].split(',').map((x) => x.trim()).filter(Boolean),
          at: p[4],
        });
      }
    }
  });

  /* "Shootout - CAL 1 (Sedlak-Braude NG, Mizuno NG, Chebaclo G), WEB 0 (...)"
     Only the attempt marked G decided it; the rest are misses. */
  let shootout = null;
  const som = t.match(/Shootout\s*-\s*(.+?)\.\s*(?:Shots on Goal|Power Play|Goalies)/);
  if (som) {
    const sides = [...som[1].matchAll(/(MD2 [^,(]+?)\s+(\d+)\s*\(([^)]*)\)/g)];
    shootout = { us: 0, them: 0, scorers: [], attempts: { us: [], them: [] } };
    for (const sd of sides) {
      const side = sd[1].trim() === CAL ? 'us' : 'them';
      shootout[side] = +sd[2];
      for (const a of sd[3].split(',')) {
        const hit = a.trim().match(/^(.+?)\s+(G|NG)$/);
        if (!hit) continue;
        const scored = hit[2] === 'G';
        /* Every attempt, in the order the sheet lists them. The two teams are
           listed separately, so the sheet says who shot for each side and in
           what order but not how the two rounds interleaved. */
        shootout.attempts[side].push({ name: hit[1].trim(), scored });
        if (scored) shootout.scorers.push({ team: side, name: hit[1].trim() });
      }
    }
  }

  const shots = {};
  const sm = t.match(/Shots on Goal-(.+?)(?:Power Play|Goalies)/);
  if (sm) for (const seg of sm[1].split(/\.\s*/)) {
    const s = seg.match(/^(.+?)\s+(\d+(?:-\d+)+)$/);
    if (s) shots[s[1].trim() === CAL ? 'us' : 'them'] = s[2].split('-').map(Number);
  }

  const pp = {};
  const pm = t.match(/Power Play Opportunities-(.+?)(?:Goalies|A-\d)/);
  if (pm) for (const seg of pm[1].split(';')) {
    const p = seg.match(/^\s*(.+?)\s+(\d+)\s*\/\s*(\d+)/);
    if (p) pp[p[1].trim() === CAL ? 'us' : 'them'] = { goals: +p[2], chances: +p[3] };
  }

  /* A second goaltender carries no team prefix, so the section is split by
     team first and every keeper inside a segment belongs to that team. */
  const keepers = [];
  const km = t.match(/Goalies-(.+?)(?:A-\d|Referees)/);
  if (km) {
    const seg = km[1];
    const teams = [...seg.matchAll(/(MD2 [^,]+?),\s*/g)];
    teams.forEach((tm, i) => {
      const body = seg.slice(tm.index + tm[0].length, i + 1 < teams.length ? teams[i + 1].index : seg.length);
      const team = tm[1].trim() === CAL ? 'us' : 'them';
      const gre = /([A-Za-z'\-. ]+?)\s+\d+-\d+-\d+-\d+\s*\((\d+) shots-(\d+) saves\)/g;
      let k;
      while ((k = gre.exec(body)) !== null) {
        keepers.push({ team, name: k[1].trim(), shots: +k[2], saves: +k[3] });
      }
    });
  }

  return {
    id, date, status, calHome, opponent: (calHome ? vName : hName).replace(/^MD2 /, ''),
    final: { us: calHome ? +hG : +vG, them: calHome ? +vG : +hG },
    goals, pens, shots, pp, keepers, shootout,
  };
}

const games = [];
for (const id of IDS) {
  const res = await fetch(url(id));
  if (!res.ok) throw new Error(`${id}: HTTP ${res.status}`);
  games.push(parse(id, flatten(await res.text())));
}

/* ---- Checks. Anything that fails here stops the write. ---- */
const problems = [];
const sum = (a) => a.reduce((n, x) => n + x, 0);

const undated = games.filter((g) => !g.date).map((g) => g.id);
if (undated.length) problems.push('no date parsed for: ' + undated.join(', '));
const dupes = games.map((g) => g.date).filter((d, i, a) => a.indexOf(d) !== i);
if (dupes.length) problems.push('two games share a date: ' + dupes.join(', '));

for (const g of games) {
  const cu = g.goals.filter((x) => x.team === 'us').length;
  const ct = g.goals.filter((x) => x.team === 'them').length;
  const so = /SO/.test(g.status);
  /* The shootout winner is credited a goal on the scoresheet that never
     appears in the play list, so the two differ by exactly one. */
  const ok = so
    ? Math.abs(cu - g.final.us) + Math.abs(ct - g.final.them) === 1
    : cu === g.final.us && ct === g.final.them;
  if (!ok) problems.push(`${g.id} ${g.opponent}: goals ${cu}-${ct} vs final ${g.final.us}-${g.final.them}`);

  if (so) {
    if (!g.shootout) problems.push(`${g.id}: final SO but no shootout line`);
    else if (g.shootout.scorers.length < 1) problems.push(`${g.id}: shootout with no scorer`);
  }

  for (const side of ['us', 'them']) {
    const a = g.shots[side];
    if (!a) { problems.push(`${g.id}: no shots for ${side}`); continue; }
    if (sum(a.slice(0, -1)) !== a[a.length - 1]) problems.push(`${g.id}: shot line ${a.join('-')} does not total`);
  }

  const ours = g.keepers.filter((k) => k.team === 'us');
  const en = g.goals.filter((x) => x.team === 'them' && x.strength === 'EN').length;
  if (ours.length && sum(ours.map((k) => k.shots - k.saves)) + en !== g.final.them) {
    problems.push(`${g.id}: goaltenders concede ${sum(ours.map((k) => k.shots - k.saves))} + ${en} EN, final ${g.final.them}`);
  }

  if (g.pp.us && g.pp.us.goals !== g.goals.filter((x) => x.team === 'us' && x.strength === 'PP').length) {
    problems.push(`${g.id}: power-play goals disagree with the opportunities line`);
  }
}

const gf = sum(games.map((g) => g.final.us));
const ga = sum(games.map((g) => g.final.them));
const w = games.filter((g) => g.final.us > g.final.them).length;
const l = games.filter((g) => g.final.us < g.final.them).length;
if (gf !== 180 || ga !== 99 || w !== 20 || l !== 10) {
  problems.push(`season rebuilt as ${w}-${l}, ${gf}-${ga}; the ACHA stats pages say 20-10, 180-99`);
}

console.log(`${games.length} games, ${sum(games.map((g) => g.goals.length))} goals, ${sum(games.map((g) => g.pens.length))} penalties`);
console.log(`season from the sheets: ${w}-${l}-0, ${gf} for, ${ga} against`);

if (problems.length) {
  console.error('\nNOT WRITTEN - ' + problems.length + ' problem(s):');
  for (const p of problems) console.error('  ' + p);
  process.exit(1);
}

await writeFile(path.join(dir, '_pbp2526.json'), JSON.stringify(games), 'utf8');
console.log('\nevery check passed - wrote _pbp2526.json');
