/**
 * 2019-20 season totals, as supplied.
 *
 * Skaters carry GP / G / A / PIM; points stay computed so PTS cannot drift
 * from G + A.
 *
 * Goals against was not supplied for the goaltenders, so it is derived - and
 * two independent routes agree exactly, which is why it is safe to store:
 *
 *   Wiseman   GAA 2.03 x 118:00 / 60 =  4.0    saves  65 / .942 -  65 =  4
 *   Morse     GAA 2.40 x 600:00 / 60 = 24.0    saves 231 / .906 - 231 = 24
 *   Crick     GAA 2.68 x 603:46 / 60 = 27.0    saves 228 / .894 - 228 = 27
 *   Taherian  GAA 3.50 x 120:00 / 60 =  7.0    saves  49 / .875 -  49 =  7
 *
 * Won-lost records were not supplied and are not guessed at.
 */
window.__addStats1920 = function addStats1920(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2019-20"];
  if (!season || !(season.roster || []).length) {
    return { site: out, report: { error: "no 2019-20 roster to attach stats to" } };
  }

  /* [GP, G, A, PIM] */
  const SKATERS = {
    "Delfino Varela": [18, 8, 14, 30],
    "Gabriel Giammarco": [16, 10, 10, 6],
    "Brian Faun": [24, 7, 13, 36],
    "Ron Paulos": [21, 10, 8, 10],
    "Noah Spieser": [16, 4, 12, 18],
    "Nolan McMahon": [22, 9, 4, 6],
    "Jeffrey Chen": [24, 6, 6, 9],
    "Andrew Wong": [22, 9, 2, 6],
    "Darien Oliver": [22, 6, 5, 30],
    "David Adams": [8, 6, 3, 12],
    "Jake Sitak": [19, 5, 4, 14],
    "Matt Chorlian": [22, 2, 7, 12],
    "Alexander Carbone": [19, 3, 5, 17],
    "Chase Swerdlick": [24, 5, 2, 4],
    "Jordan Thompson": [23, 1, 6, 12],
    "Sasha Soloviev": [20, 1, 3, 2],
    "Devin Cox": [22, 1, 3, 0],
    "Pravin Chandra": [23, 2, 0, 8],
    "Sean Butler": [11, 1, 1, 2],
    "Kevin Wang": [7, 0, 2, 0],
    "Anthony Lair": [7, 1, 0, 0],
    "Ruslan Gabidoulline": [1, 0, 0, 0],
    "Max Brownlee": [3, 0, 0, 2],
  };

  /* [GP, saves, GA, SO, minutes] */
  const GOALIES = {
    "Max Wiseman": [2, 65, 4, 0, 118],
    "Sami Morse": [10, 231, 24, 1, 600],
    "Ethan Crick": [10, 228, 27, 2, 603 + 46 / 60],
    "Conner Taherian": [2, 49, 7, 1, 120],
  };

  const missing = [];
  let matched = 0;
  season.roster = season.roster.map((p) => {
    const sk = SKATERS[p.name];
    if (sk) {
      matched++;
      return { ...p, stats: { gp: sk[0], g: sk[1], a: sk[2], pim: sk[3] } };
    }
    const gk = GOALIES[p.name];
    if (gk) {
      matched++;
      return {
        ...p,
        stats: { gp: gk[0], saves: gk[1], ga: gk[2], so: gk[3], minutes: gk[4], g: 0, a: 0, pim: 0 },
      };
    }
    missing.push(p.name);
    return p;
  });

  const rosterNames = new Set(season.roster.map((p) => p.name));
  const unmatched = [...Object.keys(SKATERS), ...Object.keys(GOALIES)]
    .filter((n) => !rosterNames.has(n));

  return {
    site: out,
    report: { matched, rosterWithoutStats: missing, statsWithoutRosterEntry: unmatched },
  };
};
