/**
 * Assign LW / C / RW to the forwards.
 *
 * ASSIGNED, NOT SOURCED. The roster we hold records F / D / G and nothing
 * finer - no source on file says which wing any of these players takes. These
 * are plausible assignments made so the box score's Pos column has something
 * in it, at the user's direction. Treat them as placeholders and correct them
 * from the coaching staff's line chart; the Spot dropdown in the roster editor
 * is where that happens.
 *
 * The logic is the usual convention rather than a coin toss: a right shot
 * takes the right wing, the left wing leans left-shot, and centres come from
 * both hands the way a real depth chart does. Where the hand is unrecorded the
 * player goes to centre, which needs no side.
 *
 * Only forwards are touched. Defence and goaltenders have no spot and keep an
 * empty field.
 */
window.__assignSpots = function assignSpots(site) {
  const out = JSON.parse(JSON.stringify(site));

  const SPOTS = {
    C: [
      "Kayden Roloff", "Tyson Storr", "Kodai Mizuno",
      "Dominik Sedlak-Braude", "Lucas Fung", "Connor Kanas",
    ],
    LW: [
      "Colten Fazio", "Arya Nahavandi", "Mark Rejna",
      "Tianshu Liu", "Roy Chebaclo",
    ],
    RW: [
      "Brendan Baker", "Bryan Bartolo", "Liam Collins",
      "Henry Conlin", "Ryan Lee", "Kristian Seppanen",
    ],
  };

  const byName = new Map();
  for (const [spot, names] of Object.entries(SPOTS)) {
    for (const n of names) byName.set(n.toLowerCase(), spot);
  }

  const season = out.seasons[out.currentSeason];
  const roster = season.roster || [];
  const done = [];
  const missed = [];

  for (const p of roster) {
    if (p.position !== "F") { p.spot = ""; continue; }
    const spot = byName.get((p.name || "").toLowerCase());
    if (spot) { p.spot = spot; done.push(p.name + " " + spot); }
    else { missed.push(p.name); }
  }

  /* Anyone on the list who is no longer on the roster - a name that changed,
     or a player who left - so the list can be corrected rather than silently
     doing nothing. */
  const rosterNames = new Set(roster.filter((p) => p.position === "F")
    .map((p) => (p.name || "").toLowerCase()));
  const stale = [...byName.keys()].filter((n) => !rosterNames.has(n));

  return {
    site: out,
    report: {
      assigned: done.length,
      bySpot: {
        LW: roster.filter((p) => p.spot === "LW").length,
        C: roster.filter((p) => p.spot === "C").length,
        RW: roster.filter((p) => p.spot === "RW").length,
      },
      forwardsWithoutSpot: missed,
      namesNotOnRoster: stale,
    },
  };
};
