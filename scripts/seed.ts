/**
 * Seeds Supabase from the prototype's SEED_SITE.
 *
 * Roster and season records are the EliteProspects import for team 10366
 * (Univ. of California-Berkeley, ACHA II), captured 2026-08-28. OT wins are
 * folded into W and OT losses into L to fit the W-L-T display.
 *
 * No per-player stats, coaches, or game logs are published upstream yet, so
 * those stay empty and are entered through the admin app. Historical seasons
 * carry a record_override because they have no game log.
 *
 * Idempotent: re-running updates seasons/news in place rather than duplicating.
 *
 *   pnpm seed              # normal run
 *   pnpm seed -- --reset   # wipe seasons + news first
 */
import { config } from 'dotenv';
import { createClient } from '@supabase/supabase-js';

config({ path: '.env.local' });
config({ path: '.env' });

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!url || !key) {
  console.error(
    'Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.\n' +
      'Copy .env.example to .env.local and fill it in.',
  );
  process.exit(1);
}

const db = createClient(url, key, { auth: { persistSession: false } });
const reset = process.argv.includes('--reset');

/** [number, name, position, shoots, height, hometown] */
type P = [string, string, 'F' | 'D' | 'G', string, string, string];

const ROSTER_2025_26: P[] = [
  // Goaltenders
  ['1', 'Yusuf Akbas', 'G', 'L', '6′0″', 'Irvine, CA'],
  ['', 'Allan Anaka', 'G', 'L', '6′0″', 'Granite Bay, CA'],
  ['80', 'Aidan Comeau', 'G', 'L', '5′10″', 'Newport Beach, CA'],
  ['39', 'Nikola Tomic', 'G', 'L', '6′0″', 'Tulln, Austria'],
  // Defensemen
  ['16', 'Jack Burbank', 'D', 'L', '6′0″', 'Brier, WA'],
  ['88', 'Sean Dolim', 'D', 'L', '6′2″', 'Manhattan Beach, CA'],
  ['95', 'Enzo Goebel', 'D', 'R', '5′8″', 'Arcadia, CA'],
  ['6', 'William Hagan', 'D', 'L', '5′6″', 'Palo Alto, CA'],
  ['96', 'Eric Khodorenko', 'D', 'L', '6′1″', 'Walnut Creek, CA'],
  ['4', 'Jason Lee', 'D', 'R', '6′1″', 'Saratoga, CA'],
  ['51', 'Simon Mantoani', 'D', 'R', '6′1″', 'San Diego, CA'],
  ['11', 'Patrick Nasta', 'D', 'R', '6′0″', 'Crystal Lake, IL'],
  ['8', 'Ellis O’Dowd', 'D', 'L', '5′8″', 'Santa Barbara, CA'],
  ['21', 'Trent Teruya', 'D', 'R', '5′9″', 'Redlands, CA'],
  // Forwards
  ['12', 'Brendan Baker', 'F', 'R', '5′8″', 'South Lake Tahoe, CA'],
  ['15', 'Bryan Bartolo', 'F', 'R', '5′10″', 'Berkeley, CA'],
  ['25', 'Roy Chebaclo', 'F', 'R', '6′0″', 'Edina, MN'],
  ['72', 'Liam Collins', 'F', 'R', '6′1″', 'Thousand Oaks, CA'],
  ['20', 'Henry Conlin', 'F', 'R', '6′2″', 'Chicago, IL'],
  ['93', 'Colten Fazio', 'F', 'L', '6′4″', 'New York, NY'],
  ['23', 'Lucas Fung', 'F', 'R', '5′10″', 'Brussels, Belgium'],
  ['97', 'Connor Kanas', 'F', '', '6′0″', 'California'],
  ['13', 'Ryan Lee', 'F', 'R', '5′11″', 'Valencia, CA'],
  ['81', 'Tianshu Liu', 'F', 'R', '5′10″', 'Orange, CA'],
  ['9', 'Kodai Mizuno', 'F', 'R', '5′9″', 'San Jose, CA'],
  ['24', 'Arya Nahavandi', 'F', 'L', '5′8″', 'San Diego, CA'],
  ['14', 'Mark Rejna', 'F', 'L', '6′0″', 'London, England'],
  ['19', 'Kayden Roloff', 'F', 'L', '5′11″', 'Redlands, CA'],
  ['3', 'Dominik Sedlak-Braude', 'F', 'R', '6′0″', 'North Potomac, MD'],
  ['29', 'Kristian Seppanen', 'F', 'R', '5′8″', 'Aliso Viejo, CA'],
  ['18', 'Tyson Storr', 'F', 'L', '5′10″', 'El Segundo, CA'],
];

interface SeedSeason {
  name: string;
  is_current: boolean;
  /** Historical seasons have no game log, so the record is carried as an override. */
  record_override: { w: number; l: number; t: number; gf: number; ga: number; note?: string } | null;
  roster: P[];
}

const SEASONS: SeedSeason[] = [
  {
    name: '2025-26',
    is_current: true,
    record_override: {
      w: 20,
      l: 10,
      t: 0,
      gf: 180,
      ga: 99,
      note: 'ACHA II · 3rd in PPG rank · via EliteProspects',
    },
    roster: ROSTER_2025_26,
  },
  {
    name: '2024-25',
    is_current: false,
    record_override: { w: 27, l: 1, t: 0, gf: 198, ga: 60, note: '1st in ACHA II PPG rank' },
    roster: [],
  },
  {
    name: '2023-24',
    is_current: false,
    record_override: { w: 15, l: 12, t: 0, gf: 173, ga: 119 },
    roster: [],
  },
  {
    name: '2022-23',
    is_current: false,
    record_override: { w: 14, l: 6, t: 0, gf: 129, ga: 69 },
    roster: [],
  },
  {
    name: '2019-20',
    is_current: false,
    record_override: { w: 14, l: 10, t: 0, gf: 98, ga: 64, note: 'Playoffs cancelled' },
    roster: [],
  },
  {
    name: '2018-19',
    is_current: false,
    record_override: { w: 18, l: 6, t: 0, gf: 128, ga: 63 },
    roster: [],
  },
  {
    name: '2017-18',
    is_current: false,
    record_override: { w: 16, l: 2, t: 0, gf: 121, ga: 60 },
    roster: [],
  },
];

const NEWS = [
  {
    date: '2026-08-28',
    tag: 'NEWS',
    title: 'New Cal Ice Hockey Site Is Live',
    blurb: 'Schedule, roster, stats, and season archives — all in one place, updated by the team.',
  },
  {
    date: '2026-08-20',
    tag: 'NEWS',
    title: 'Recruit Interest Form Open for 2026-27',
    blurb: 'Incoming Bears and current students: tell the coaching staff about your game.',
  },
  {
    date: '2026-08-10',
    tag: 'NEWS',
    title: 'Season Archives Now Online',
    blurb: 'Browse team records going back to 2017-18, imported from EliteProspects.',
  },
];

async function main() {
  if (reset) {
    console.log('--reset: clearing seasons and news');
    // players/games/coaches cascade from seasons.
    await db.from('seasons').delete().neq('name', '');
    await db.from('news').delete().neq('title', '');
    await db.from('people').delete().neq('name', '');
  }

  for (const s of SEASONS) {
    const { data: season, error } = await db
      .from('seasons')
      .upsert(
        { name: s.name, is_current: s.is_current, record_override: s.record_override },
        { onConflict: 'name' },
      )
      .select('id')
      .single();

    if (error) throw new Error(`season ${s.name}: ${error.message}`);

    if (s.roster.length > 0) {
      // Replace the roster wholesale — the seed is the source of truth on a re-run.
      const { error: delErr } = await db.from('players').delete().eq('season_id', season.id);
      if (delErr) throw new Error(`clear roster ${s.name}: ${delErr.message}`);

      for (const [number, name, position, shoots, height, hometown] of s.roster) {
        // People outlive seasons: reuse the existing person if this name is
        // already known, so a returning player keeps one career line.
        const { data: found } = await db
          .from('people')
          .select('id')
          .ilike('name', name)
          .limit(1)
          .maybeSingle();

        let personId = found?.id as string | undefined;

        if (!personId) {
          const { data: created, error: personErr } = await db
            .from('people')
            .insert({ name, shoots, height, hometown, high_school: '', prior_team: '', bio: '' })
            .select('id')
            .single();
          if (personErr) throw new Error(`person ${name}: ${personErr.message}`);
          personId = created.id;
        }

        const { error: insErr } = await db.from('players').insert({
          season_id: season.id,
          person_id: personId,
          number,
          position,
          year: '',
          captain: '',
          gp: 0,
          g: 0,
          a: 0,
          pim: 0,
        });
        if (insErr) throw new Error(`roster ${s.name} / ${name}: ${insErr.message}`);
      }
    }

    console.log(`  ${s.name.padEnd(8)} ${String(s.roster.length).padStart(2)} players`);
  }

  // News has no natural key; only insert titles that aren't there yet.
  const { data: existing } = await db.from('news').select('title');
  const have = new Set((existing ?? []).map((n) => n.title));
  const fresh = NEWS.filter((n) => !have.has(n.title));

  if (fresh.length > 0) {
    const { error } = await db
      .from('news')
      .insert(fresh.map((n) => ({ ...n, body: '', author: '', published: true })));
    if (error) throw new Error(`news: ${error.message}`);
  }
  console.log(`  news     ${fresh.length} inserted, ${NEWS.length - fresh.length} already present`);

  console.log('\nSeed complete.');
}

main().catch((e) => {
  console.error('\nSeed failed:', e instanceof Error ? e.message : e);
  process.exit(1);
});
