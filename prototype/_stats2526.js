/**
 * 2025-26 season totals, from the ACHA.
 *
 * REAL DATA. Source: achahockey.org player stats and goalie stats for
 * MD2 University of California-Berkeley, 2025-2026, read on the date this was
 * run. Nothing here is invented; anything the source does not carry is left
 * empty rather than filled in.
 *
 * What the source gives, and what it does not:
 *   skaters  GP G A PPG SHG GWG PIM        - no shots, no tying goals
 *   goalies  GP W L GA SVS SO minutes      - SV% and GAA are derived, so they
 *                                            are recomputed rather than stored
 *
 * Names are matched case- and punctuation-insensitively, with an alias for the
 * two the ACHA spells differently from our roster. Anyone unmatched is
 * reported rather than dropped quietly.
 *
 * IMPORTANT: these totals live on the roster row, and boxScoreTotals() only
 * falls back to the roster row when the season has NO box scores. While the
 * demo schedule is loaded its per-game lines win and these numbers stay
 * invisible. Clear the demo data for them to show.
 */
window.__addStats2526 = function addStats2526(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  /* name, GP, G, A, PPG, SHG, GWG, PIM */
  const SKATERS = [
    ["Dominik Sedlak-Braude", 21, 25, 18, 4, 3, 0, 30],
    ["Roy Chebaclo", 24, 19, 19, 1, 1, 0, 6],
    ["Liam Collins", 24, 17, 17, 2, 1, 3, 18],
    ["Mark Rejna", 30, 16, 17, 2, 2, 3, 22],
    ["Kodai Mizuno", 28, 12, 21, 3, 2, 1, 6],
    ["Lucas Fung", 27, 21, 9, 0, 0, 4, 31],
    ["Colten Fazio", 28, 17, 11, 8, 0, 2, 66],
    ["John Burbank", 28, 9, 15, 2, 0, 0, 10],
    ["Ellis Odowd", 26, 4, 18, 2, 0, 0, 12],
    ["Sean Dolim", 23, 4, 14, 1, 0, 1, 21],
    ["Tianshu Liu", 14, 9, 7, 3, 0, 1, 21],
    ["Jason Lee", 29, 4, 12, 2, 0, 0, 63],
    ["Tyson Storr", 24, 3, 12, 1, 0, 1, 9],
    ["Trent Teruya", 26, 3, 12, 0, 0, 1, 73],
    ["Connor Kanas", 20, 3, 7, 0, 0, 0, 17],
    ["Simon Mantoani", 27, 2, 7, 0, 0, 0, 6],
    ["Ryan Lee", 18, 3, 5, 1, 0, 0, 8],
    ["Patrick Nasta", 18, 0, 8, 0, 0, 0, 22],
    ["Bryan Bartolo", 13, 2, 5, 1, 0, 1, 20],
    ["Arya Nahavandi", 20, 2, 5, 0, 0, 1, 29],
    ["Brendan Baker", 22, 3, 2, 0, 0, 0, 26],
    ["Henry Conlin", 13, 1, 4, 0, 0, 0, 2],
    ["Enzo Goebel", 25, 0, 2, 0, 0, 0, 42],
    ["Eric Khodorenko", 1, 0, 0, 0, 0, 0, 0],
    ["Kayden Roloff", 1, 0, 0, 0, 0, 0, 0],
    ["William Hagan", 4, 0, 0, 0, 0, 0, 0],
  ];

  /* name, GP, W, L, GA, SVS, SO, minutes */
  const GOALIES = [
    ["Aidan Comeau", 25, 16, 8, 65, 668, 3, 1327],
    ["Nikola Tomic", 5, 2, 1, 12, 94, 2, 228],
    ["Yusuf Akbas", 7, 2, 1, 19, 77, 0, 250],
    ["Allan Anaka", 0, 0, 0, 0, 0, 0, 0],
  ];

  /* The ACHA spells these two differently from the roster we hold. */
  const ALIAS = { "john burbank": "jack burbank", "ellis odowd": "ellis o'dowd" };
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
  const key = (s) => {
    const low = String(s || "").toLowerCase().trim();
    return norm(ALIAS[low] || low);
  };

  const roster = season.roster || [];
  const byKey = new Map(roster.map((p) => [norm(p.name), p]));
  const unmatched = [];
  const matched = [];

  for (const [name, gp, g, a, ppg, shg, gwg, pim] of SKATERS) {
    const p = byKey.get(key(name));
    if (!p) { unmatched.push(name); continue; }
    p.stats = { ...(p.stats || {}), gp, g, a, ppg, shg, gwg, pim };
    matched.push(p.name);
  }

  for (const [name, gp, w, l, ga, saves, so, minutes] of GOALIES) {
    const p = byKey.get(key(name));
    if (!p) { unmatched.push(name); continue; }
    p.stats = { ...(p.stats || {}), gp, w, l, tie: 0, ga, saves, so, minutes, g: 0, a: 0, pim: 0 };
    matched.push(p.name);
  }

  /* The season's own record, straight from the goalie page totals. */
  season.record = { ...(season.record || {}), w: 20, l: 10, t: 0, ga: 99 };

  const sourced = new Set([...SKATERS, ...GOALIES].map(([n]) => key(n)));
  const notInSource = roster.filter((p) => !sourced.has(norm(p.name))).map((p) => p.name);

  return {
    site: out,
    report: {
      matched: matched.length,
      unmatchedFromSource: unmatched,
      onRosterButNotInSource: notInSource,
      teamGA: 99, teamRecord: "20-10-0",
    },
  };
};
