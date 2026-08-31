/**
 * 2018-19 season totals, as supplied.
 *
 * Skaters carry GP / G / A / PIM. Points are not stored - the site adds G and
 * A wherever it shows PTS, so storing it too would just be a number that could
 * disagree with itself.
 *
 * Goaltenders were given as GP, GAA, SV%, SO, time on ice and saves. Goals
 * against was not, so it is worked out - and worth showing the arithmetic,
 * because two independent routes agree exactly:
 *
 *   Morse     GAA 2.56 x 585:48 / 60 = 25.0    saves 309 / .925 - 309 = 25
 *   Crick     GAA 2.62 x 618:35 / 60 = 27.0    saves 264 / .907 - 264 = 27
 *   Taherian  GAA 3.33 x 180:00 / 60 = 10.0    saves  61 / .859 -  61 = 10
 *
 * Won-lost records were not supplied and are not guessed at.
 */
window.__addStats1819 = function addStats1819(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2018-19"];
  if (!season || !(season.roster || []).length) {
    return { site: out, report: { error: "no 2018-19 roster to attach stats to" } };
  }

  /* [GP, G, A, PIM] */
  const SKATERS = {
    "Michael Leone": [22, 17, 28, 14],
    "Gabriel Giammarco": [22, 19, 21, 14],
    "Delfino Varela": [23, 14, 16, 40],
    "Jeffrey Chen": [22, 9, 11, 8],
    "Noah Spieser": [21, 4, 16, 24],
    "Patrick Tagari": [18, 11, 6, 11],
    "Andrew Wong": [23, 6, 10, 4],
    "William Song": [21, 5, 11, 29],
    "Jack Gibbons": [19, 7, 6, 15],
    "Kevin Wang": [21, 2, 11, 2],
    "Chase Swerdlick": [22, 8, 4, 16],
    "Max Brownlee": [22, 6, 4, 20],
    "Ron Paulos": [22, 5, 5, 6],
    "Matt Chorlian": [22, 2, 8, 22],
    "Darien Oliver": [21, 6, 3, 14],
    "Devin Cox": [20, 3, 6, 4],
    "Jordan Thompson": [21, 2, 5, 4],
    "Sasha Soloviev": [16, 2, 0, 0],
    "Alexandre Orcutt": [23, 0, 2, 19],
    "Sean Butler": [4, 0, 0, 0],
    "Duncan Cadeddu": [5, 0, 0, 0],
  };

  /* [GP, saves, GA, SO, minutes] */
  const GOALIES = {
    "Sami Morse": [10, 309, 25, 0, 585 + 48 / 60],
    "Ethan Crick": [11, 264, 27, 1, 618 + 35 / 60],
    "Conner Taherian": [3, 61, 10, 0, 180],
  };

  const missing = [];
  const matched = [];
  season.roster = season.roster.map((p) => {
    const sk = SKATERS[p.name];
    if (sk) {
      matched.push(p.name);
      return { ...p, stats: { gp: sk[0], g: sk[1], a: sk[2], pim: sk[3] } };
    }
    const gk = GOALIES[p.name];
    if (gk) {
      matched.push(p.name);
      return {
        ...p,
        stats: { gp: gk[0], saves: gk[1], ga: gk[2], so: gk[3], minutes: gk[4], g: 0, a: 0, pim: 0 },
      };
    }
    missing.push(p.name);
    return p;
  });

  /* Anything in the supplied tables that is not on the roster - a name typed
     differently, say - is worth naming rather than silently dropping. */
  const rosterNames = new Set(season.roster.map((p) => p.name));
  const unmatched = [...Object.keys(SKATERS), ...Object.keys(GOALIES)]
    .filter((n) => !rosterNames.has(n));

  return {
    site: out,
    report: {
      matched: matched.length,
      rosterWithoutStats: missing,
      statsWithoutRosterEntry: unmatched,
    },
  };
};
