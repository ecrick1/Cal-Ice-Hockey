/**
 * Schedules and results for 2012-13, 2013-14 and 2014-15.
 *
 * REAL DATA from MYHockey Rankings, which is the only source still online
 * that carries Cal through those three years. EliteProspects has a genuine
 * hole there - a player who appears either side of it, Sandon Griffin, shows
 * 2011-12 and then 2015-16 on his own page - the ACHA's system begins at
 * 2020-21, and Pointstreak, which ran ACHA stats at the time, is gone.
 *
 * What this source is worth was measured rather than assumed. Against
 * 2025-26, whose game log is already on the site and was verified against the
 * ACHA's own feed, MYHockey had 27 of the 30 games and every one of the 27
 * matched exactly; the three it was missing account precisely for the gap in
 * its totals, 156+24=180 for and 87+12=99 against. So each game it lists can
 * be trusted, and its season totals cannot - it drops games silently. These
 * three seasons are therefore a floor, not a certified record.
 *
 * It publishes no venue, so `homeAway` is left unset rather than guessed, and
 * vsAt() prints neither "vs" nor "at" for a game nobody recorded one for.
 *
 * Nothing here touches a season that already has a game log or a verified
 * record.
 */
window.__applyMhr = function applyMhr(site, data, opts) {
  const dry = !(opts && opts.write);
  const out = JSON.parse(JSON.stringify(site));
  out.opponents = [...(out.opponents || [])];
  const uid = (p) => p + Math.random().toString(36).slice(2, 9);
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  const MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6,
                   jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 };

  /* MYHockey prints "Oct 4" with no year. A season runs August to June, so
     the month says which side of New Year the game falls on. */
  const isoDate = (season, when) => {
    const m = String(when).match(/^([A-Za-z]{3})\s+(\d{1,2})/);
    if (!m) return null;
    const mon = MONTHS[m[1].toLowerCase()];
    if (!mon) return null;
    const start = Number(season.slice(0, 4));
    const year = mon >= 8 ? start : start + 1;
    return year + "-" + String(mon).padStart(2, "0") + "-" + String(m[2]).padStart(2, "0");
  };

  /* MYHockey's long-form names against the ones the site already uses. Only
     the exact strings this data contains, so a name it has never seen shows
     up as a new opponent rather than being matched to something near it. */
  const ALIAS = {
    "san jose state university (d2)": "San Jose State",
    "san jose state university": "San Jose State",
    "santa clara university": "Santa Clara",
    "stanford university": "Stanford",
    "oregon, university of": "Oregon",
    "washington, university of": "Washington",
    "utah, university of": "Utah",
    "california - davis, university of": "UC Davis",
    "california - los angeles, university of": "UCLA",
    "california - santa barbara, university of": "UCSB",
    "southern california, university of": "USC",
  };
  /* Not on the site, because Cal has not played them in any season it holds. */
  const NEW_OPPONENTS = {
    "santa rosa junior college": { name: "Santa Rosa Junior College", short: "SRJC" },
    "fresno state university": { name: "Fresno State", short: "FRES" },
    "california state university - long beach": { name: "Cal State Long Beach", short: "CSULB" },
    "brigham young university": { name: "BYU", short: "BYU" },
    "gonzaga university": { name: "Gonzaga", short: "GONZ" },
  };

  const byName = new Map(out.opponents.map((o) => [norm(o.name), o]));
  const report = { seasons: [], opponentsAdded: [], skipped: [], unmatched: [], checks: [] };

  const opponentFor = (raw) => {
    const key = String(raw).trim().toLowerCase();
    const mapped = ALIAS[key];
    if (mapped) {
      const hit = byName.get(norm(mapped));
      if (hit) return hit;
      report.unmatched.push(raw + " -> " + mapped + " (alias points at no opponent)");
      return null;
    }
    const direct = byName.get(norm(raw));
    if (direct) return direct;
    const made = NEW_OPPONENTS[key];
    if (!made) { report.unmatched.push(raw); return null; }
    const hit = byName.get(norm(made.name));
    if (hit) return hit;
    const o = { id: uid("o"), name: made.name, short: made.short,
                logoLight: "", logoDark: "", homeRink: "", source: "myhockeyrankings" };
    out.opponents.push(o);
    byName.set(norm(o.name), o);
    report.opponentsAdded.push(o.name + " (" + o.short + ")");
    return o;
  };

  for (const s of data.seasons || []) {
    const key = s.season;
    const existing = out.seasons[key];
    if (existing && (existing.schedule || []).length) {
      report.skipped.push(key + " — already has a game log");
      continue;
    }
    if (existing && existing.record) {
      report.skipped.push(key + " — already has a published record");
      continue;
    }

    const schedule = [];
    let w = 0, l = 0, t = 0, gf = 0, ga = 0;
    for (const row of s.games || []) {
      const [when, opp, outcome, score] = row.split("~");
      const date = isoDate(key, when);
      const o = opponentFor(opp);
      if (!date || !o) continue;
      const m = String(score).match(/^(\d+)\s*-\s*(\d+)(\s*OT)?/);
      if (!m) continue;
      const us = Number(m[1]), them = Number(m[2]);
      gf += us; ga += them;
      if (us > them) w++; else if (us < them) l++; else t++;

      schedule.push({
        id: "g" + key.replace("-", "") + "-" + date + "-" + (o.short || "OPP"),
        date,
        opponentId: o.id,
        /* Not published. Left unset, not guessed. */
        homeAway: "",
        venue: "", location: "", time: "",
        gameType: "regular", roundLabel: "", streamUrl: "", replayUrl: "",
        result: { us, them, ot: /OT/i.test(score) },
        source: "myhockeyrankings",
      });
    }
    schedule.sort((a, b) => a.date.localeCompare(b.date));

    /* The site computes a record from the log, so this only checks that what
       was read back matches the totals MYHockey prints on the same page. */
    const mine = w + "-" + l + "-" + t + "  " + gf + ":" + ga;
    const theirs = String(s.totals).replace(/\s+/g, " ").trim();
    const same = mine.replace(/\s+/g, " ") === theirs;
    report.checks.push(key + ": read " + mine.replace(/\s+/g, " ")
      + " vs page " + theirs + (same ? "  ✓" : "  DIFFERS"));

    if (!dry) {
      out.seasons[key] = {
        ...(existing || {}),
        label: (existing && existing.label) || key,
        roster: (existing && existing.roster) || [],
        coaches: (existing && existing.coaches) || [],
        record: (existing && existing.record) || null,
        schedule,
      };
    }

    report.seasons.push({
      season: key, created: !existing, games: schedule.length,
      of: (s.games || []).length,
      record: w + "-" + l + "-" + t, goals: gf + ":" + ga,
    });
  }

  report.unmatched = [...new Set(report.unmatched)];
  return { site: out, report };
};
