/**
 * The 2025-26 schedule, from the ACHA.
 *
 * REAL DATA. Source: achahockey.org schedule for MD2 University of
 * California-Berkeley, 2025-2026, all months. Thirty games, every one final.
 *
 * Cross-checks against the stats already imported from the same source:
 *   30 games, 20-10-0, 180 goals for, 99 against
 * Those three totals are recomputed here from the game log and reported, so a
 * mistyped score shows up as a disagreement rather than sitting on the site.
 *
 * Home and away follow the ACHA's own columns, not the venue: four games are
 * at neutral rinks (Weber County, Promenade, and two at the EWU rec centre)
 * where Cal is listed as the home team. The venue is recorded as played.
 *
 * The source gives no start times - every game is already final - so time is
 * left blank rather than invented.
 *
 * Idempotent: replaces the 2025-26 schedule outright, and reuses any opponent
 * record that already exists by name so ids and logos survive a rerun.
 */
window.__addSchedule2526 = function addSchedule2526(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  /* name, short, logo slug (null when we hold no mark), colour */
  const OPPONENTS = [
    ["San Jose State", "SJSU", "sjsu", "#0055A2"],
    ["Grand Canyon", "GCU", "grand-canyon", "#522398"],
    ["Washington State", "WSU", "washington-state", "#981E32"],
    ["UC San Diego", "UCSD", "ucsd", "#182B49"],
    ["Eastern Washington", "EWU", "eastern-washington", "#A10022"],
    ["Washington", "UW", "washington", "#4B2E83"],
    ["Western Washington", "WWU", "western-washington", "#003F87"],
    ["Loyola Marymount", "LMU", "lmu", "#8A1538"],
    ["Utah State", "USU", "utah-state", "#00263A"],
    ["Utah", "UTAH", "utah", "#CC0000"],
    ["Weber State", "WEB", "weber-state", "#4F2D7F"],
    ["Montana State", "MSU", "montana-state", "#00205B"],
    ["Metropolitan State-Denver", "MSUD", "metro-state-denver", "#B01E24"],
    ["Dakota College-Bottineau", "DCB", "dakota-college-bottineau", "#1B5633"],
    ["Northeastern", "NU", "northeastern", "#C8102E"],
    ["Colorado", "COLO", "colorado", "#CFB87C"],
    ["USC", "USC", "usc", "#990000"],
  ];

  /* date, opponent, H/A (as the ACHA lists it), venue, Cal goals, their goals,
     and a flag for the one decided in a shootout. */
  const GAMES = [
    ["2025-09-26", "San Jose State", "A", "Sharks Ice at San Jose", 7, 3],
    ["2025-09-27", "San Jose State", "A", "Sharks Ice at San Jose", 15, 3],
    ["2025-10-03", "Grand Canyon", "H", "Oakland Ice Center", 4, 1],
    ["2025-10-04", "Grand Canyon", "H", "Oakland Ice Center", 2, 4],
    ["2025-10-10", "Washington State", "H", "Oakland Ice Center", 6, 0],
    ["2025-10-11", "Washington State", "H", "Oakland Ice Center", 6, 2],
    ["2025-10-25", "UC San Diego", "H", "Oakland Ice Center", 8, 1],
    ["2025-10-26", "UC San Diego", "H", "Oakland Ice Center", 13, 0],
    ["2025-10-31", "Eastern Washington", "H", "Oakland Ice Center", 10, 0],
    ["2025-11-01", "Eastern Washington", "H", "Oakland Ice Center", 14, 3],
    ["2025-11-07", "Washington", "A", "Kraken Community Iceplex", 6, 2],
    ["2025-11-08", "Washington", "A", "Kraken Community Iceplex", 3, 1],
    ["2025-11-09", "Western Washington", "A", "Bellingham Sportsplex", 9, 4],
    ["2025-11-10", "Western Washington", "A", "Bellingham Sportsplex", 11, 5],
    ["2025-11-15", "Loyola Marymount", "H", "Oakland Ice Center", 2, 6],
    ["2025-11-16", "Loyola Marymount", "H", "Oakland Ice Center", 5, 0],
    ["2025-11-20", "Utah State", "A", "Eccles Ice Center", 1, 8],
    ["2025-11-21", "Utah", "A", "Salt Lake City Sports Complex", 3, 6],
    ["2025-11-22", "Weber State", "A", "Weber County Ice Sheet", 3, 2, "SO"],
    ["2025-11-23", "Montana State", "H", "Weber County Ice Sheet", 4, 8],
    ["2026-01-16", "Metropolitan State-Denver", "A", "Promenade Ice Centre", 2, 5],
    ["2026-01-17", "Dakota College-Bottineau", "H", "Promenade Ice Centre", 8, 4],
    ["2026-01-18", "Northeastern", "A", "Greeley Ice Haus", 3, 6],
    ["2026-01-19", "Colorado", "A", "CU Boulder Rec Center Ice Rink", 1, 2],
    ["2026-01-23", "USC", "H", "Oakland Ice Center", 3, 7],
    ["2026-01-24", "USC", "H", "Oakland Ice Center", 4, 1],
    ["2026-01-30", "San Jose State", "A", "Sharks Ice at San Jose", 4, 3],
    ["2026-02-06", "Eastern Washington", "A", "University Recreation Center-EWU", 14, 1],
    ["2026-02-07", "USC", "H", "University Recreation Center-EWU", 6, 5],
    ["2026-02-08", "Washington", "H", "University Recreation Center-EWU", 3, 6],
  ];

  const rid = () => Math.random().toString(36).slice(2, 9);

  /* Reuse an opponent already on file so its id, colour and any logo the
     staff uploaded are kept. */
  const byName = new Map((out.opponents || []).map((o) => [o.name, o]));
  for (const [name, short, slug, color] of OPPONENTS) {
    const logo = slug ? "/logos/" + slug + (slug === "western-washington" ? ".svg" : ".webp") : null;
    const prev = byName.get(name);
    byName.set(name, prev
      ? { ...prev, short: prev.short || short, color: prev.color || color,
          logoLight: prev.logoLight || logo }
      : { id: rid(), name, short, color, logoLight: logo, logoDark: null });
  }
  out.opponents = [...byName.values()];

  const idOf = (name) => (byName.get(name) || {}).id || "";
  const missing = [];

  season.schedule = GAMES.map(([date, opp, ha, venue, us, them, so]) => {
    if (!idOf(opp)) missing.push(opp);
    return {
      id: "g2526-" + date + "-" + (byName.get(opp) || {}).short,
      date, opponentId: idOf(opp), homeAway: ha,
      venue, location: "", time: "",
      gameType: "regular", roundLabel: "",
      streamUrl: "", replayUrl: "",
      /* A shootout is an overtime that went further, so it carries both:
         `ot` keeps every existing check working, `so` lets the surfaces that
         care say "SO" instead. */
      result: { us, them, ot: so === "SO", so: so === "SO" },
    };
  });

  /* Recompute what the stats page already claims, from the games themselves. */
  const w = GAMES.filter(([, , , , u, t]) => u > t).length;
  const l = GAMES.filter(([, , , , u, t]) => u < t).length;
  const tie = GAMES.filter(([, , , , u, t]) => u === t).length;
  const gf = GAMES.reduce((n, g) => n + g[4], 0);
  const ga = GAMES.reduce((n, g) => n + g[5], 0);
  season.record = { ...(season.record || {}), w, l, t: tie, gf, ga };

  return {
    site: out,
    report: {
      games: season.schedule.length,
      record: w + "-" + l + "-" + tie, gf, ga,
      agreesWithStatsPage: w === 20 && l === 10 && tie === 0 && gf === 180 && ga === 99,
      opponents: out.opponents.length,
      withoutLogo: OPPONENTS.filter(([, , slug]) => !slug).map(([n]) => n),
      opponentIdMissing: missing,
    },
  };
};
