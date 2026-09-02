/**
 * What the prototype holds that the database cannot store.
 *
 * The schema was written when a game was a date, a score and a list of goals.
 * The prototype has since grown live scoring, a play-by-play with eight kinds
 * of play, opponent rosters, sponsors and an alumni list - and an importer
 * written against a schema that cannot hold its input drops the difference
 * silently, which is the worst way to find out.
 *
 * So the mapping is declared rather than assumed: every field the prototype
 * writes is either named here with the column it belongs in, or listed as
 * deliberately not stored. Anything else is a gap, and the gaps are the
 * migration that has to be written before any data moves.
 *
 *   node scripts/audit-schema.mjs
 */
import { readFile } from 'node:fs/promises';
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });

const SITE = process.argv[2] || 'data/backup-2026-08-31/site.json';
const site = JSON.parse(await readFile(SITE, 'utf8'));

/* Fields the prototype keeps for itself. Local bookkeeping, caches of things
   the database derives, and the two counters that only mean something to a
   browser holding one copy. */
const NOT_STORED = {
  game: ['id', 'plays', 'live', 'result', 'lineup', 'awayLineup', 'source'],
  play: ['id'],
  person: ['id', 'stats', 'source', 'addedFromBoxScore'],
  line: ['fow', 'fol'],
  oppLine: ['fow', 'fol'],
  opponent: ['id', 'roster', 'source'],
  news: ['id', 'source', 'generated'],
  staff: ['id'],
  top: ['rev', 'v', 'demo', 'account', 'currentSeason', 'seasons',
    'gameStats', 'opponentStats'],
};

/* prototype field -> column it lands in. */
const MAP = {
  game: {
    date: 'date', homeAway: 'home_away', venue: 'venue', time: 'time',
    location: 'location', opponentId: 'opponent_id', gameType: 'game_type',
    roundLabel: 'round_label', streamUrl: 'stream_url', replayUrl: 'replay_url',
    achaGameId: 'acha_game_id', forfeit: 'forfeit', officials: 'officials',
    pp: 'power_play', previewId: 'preview_id', recapId: 'recap_id',
    shootout: 'shootout', stars: 'stars', ticketsUrl: 'tickets_url',
  },
  play: {
    kind: 'kind', team: 'team', period: 'period', clock: 'clock',
    scorerId: 'player_id', scorer: 'player_name', assistIds: 'assist_ids',
    assists: 'assist_names', strength: 'strength', minutes: 'minutes',
    infraction: 'infraction',
    /* One person per play, whatever the play is. */
    playerId: 'player_id', player: 'player_name',
    shooterId: 'player_id', shooter: 'player_name',
    winnerId: 'player_id', winner: 'player_name',
    /* Sparse and kind-specific: null on seven kinds out of eight. */
    a1: 'detail', a2: 'detail', by: 'detail', byId: 'detail', byTeam: 'detail',
    goalie: 'detail', phase: 'detail', reason: 'detail',
    us: 'detail', them: 'detail',
  },
  person: {
    name: 'name', hometown: 'hometown', highSchool: 'high_school',
    priorTeam: 'prior_team', shoots: 'shoots', height: 'height', bio: 'bio',
    photo: 'photo_url', weight: 'weight',
    number: 'players.number', position: 'players.position', year: 'players.year',
    captain: 'players.captain',
    achaId: 'acha_id', spot: 'spot',
  },
  line: {
    dressed: 'dressed', g: 'g', a: 'a', pim: 'pim', saves: 'saves',
    ga: 'goals_against', ppg: 'ppg', shg: 'shg', gwg: 'gwg', shots: 'shots',
    minutes: 'minutes',
  },
  oppLine: {
    name: 'name', number: 'number', isGoalie: 'is_goalie', g: 'g', a: 'a',
    pim: 'pim', saves: 'saves', ga: 'goals_against', minutes: 'minutes',
    id: 'opponent_player_id', position: 'position', shots: 'shots',
  },
  opponent: {
    name: 'name', short: 'short_name', logoLight: 'logo_light_url',
    logoDark: 'logo_dark_url', homeVenue: 'home_venue', homeCity: 'home_city',
    achaTeamId: 'acha_team_id', color: 'color', mascot: 'mascot',
  },
  news: {
    date: 'date', tag: 'tag', title: 'title', blurb: 'blurb', body: 'body',
    image: 'image_url', published: 'published', author: 'author',
    publishAt: 'publish_at',
    gameId: 'game_id',
  },
  staff: {
    name: 'name', title: 'title', email: 'email', bio: 'bio', photo: 'photo_url',
    roleGroup: 'role_group', since: 'since', phone: 'phone', featured: 'featured',
  },
  top: {
    news: 'news', opponents: 'opponents', staff: 'staff',
    settings: 'settings', recruiting: 'settings', volunteerRoles: 'volunteer_roles',
    sponsors: 'sponsors', pages: 'site_pages', nav: 'settings',
  },
};

const keysOf = (objs) => {
  const s = new Set();
  for (const o of objs) if (o && typeof o === 'object') for (const k of Object.keys(o)) s.add(k);
  return [...s].sort();
};

const seasons = Object.values(site.seasons || {});
const sets = {
  game: keysOf(seasons.flatMap((s) => s.schedule || [])),
  play: keysOf(seasons.flatMap((s) => (s.schedule || []).flatMap((g) => g.plays || []))),
  person: keysOf(seasons.flatMap((s) => s.roster || [])),
  line: keysOf(Object.values(site.gameStats || {}).flatMap((m) => Object.values(m))),
  oppLine: keysOf(Object.values(site.opponentStats || {}).flat()),
  opponent: keysOf(site.opponents || []),
  news: keysOf(site.news || []),
  staff: keysOf(site.staff || []),
  top: Object.keys(site).sort(),
};

/* Columns that exist, so a mapping naming one that does not is caught here
   rather than by the importer at three in the morning. */
const c = new pg.Client({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });
await c.connect();
const cols = new Set((await c.query(
  `select table_name || '.' || column_name c from information_schema.columns
   where table_schema='public'`)).rows.map((r) => r.c));
const tables = new Set((await c.query(
  `select table_name t from information_schema.tables where table_schema='public'`)).rows.map((r) => r.t));
await c.end();

const TABLE_FOR = {
  game: 'games', play: 'game_plays', person: 'people', line: 'game_stats',
  oppLine: 'opponent_game_stats', opponent: 'opponents', news: 'news', staff: 'staff',
};

let gaps = 0, wrong = 0;
for (const [group, keys] of Object.entries(sets)) {
  const map = MAP[group] || {};
  const skip = new Set(NOT_STORED[group] || []);
  const missing = [], bad = [];
  for (const k of keys) {
    if (skip.has(k)) continue;
    if (!(k in map)) { missing.push(k + ' (unmapped)'); continue; }
    const col = map[k];
    if (col === null) { missing.push(k); continue; }
    if (group === 'top') { if (!tables.has(col)) bad.push(`${k} -> ${col}`); continue; }
    const full = col.includes('.') ? col : TABLE_FOR[group] + '.' + col;
    if (!cols.has(full)) bad.push(`${k} -> ${full}`);
  }
  gaps += missing.length; wrong += bad.length;
  const label = (TABLE_FOR[group] || group).padEnd(20);
  if (!missing.length && !bad.length) console.log('  ok    ' + label + keys.length + ' fields');
  else {
    console.log('  GAP   ' + label + missing.length + ' with nowhere to go');
    if (missing.length) console.log('          ' + missing.join(', '));
    if (bad.length) console.log('        MAPPED TO A COLUMN THAT DOES NOT EXIST: ' + bad.join(', '));
  }
}
console.log('\n' + gaps + ' fields need schema, ' + wrong + ' mappings point at nothing.');
