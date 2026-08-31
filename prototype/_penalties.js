/**
 * Penalty and face-off plays for every played game.
 *
 * DEMO CONTENT. The dataset is already flagged `demo: true`; this is the same
 * fiction told in more detail. Nothing here is a record of a real game.
 *
 * The penalties are DERIVED from the penalty minutes already on the box score
 * rather than invented alongside them. The box score is the record of what a
 * player did; a play only says when. So each player's PIM is split into
 * infractions that add back up to exactly that number - two-minute minors,
 * with a five-minute major where the remainder calls for one - and no total
 * anywhere else on the page moves.
 *
 * Face-offs are here because Face-off % has nothing to read without them, and
 * a stat that always shows a dash cannot be judged. They are deliberately
 * sparse: an operator records the draw after a stoppage, not all sixty-odd in
 * a game, so a dozen or so per game is what the console would really collect.
 * The percentage is therefore of recorded draws, which is the honest thing for
 * it to be.
 *
 * Order does not matter here - run __addPeriodMarks afterwards and it sorts
 * every period by the clock and puts the period marks back.
 *
 * Deterministic: seeded from the game id, so a rerun reproduces this exactly.
 * Idempotent: existing penalty and face-off plays are stripped and rebuilt.
 */
window.__addPenalties = function addPenalties(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons[out.currentSeason];
  const schedule = season.schedule || [];
  const roster = season.roster || [];

  const MINOR = [
    "tripping", "hooking", "slashing", "holding", "cross-checking",
    "interference", "roughing", "high-sticking", "delay of game", "boarding",
    "too many men", "unsportsmanlike conduct",
  ];
  const MAJOR = ["fighting", "checking from behind", "charging"];

  const seedOf = (str) => {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  };
  const rngFrom = (seed) => {
    let s = seed || 1;
    return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  };

  /* Minutes broken into penalties that add back up to them. An odd minute
     left over is dropped rather than rounded up: better a total one short
     than an infraction nobody called. */
  const split = (pim) => {
    const list = [];
    let left = Number(pim) || 0;
    while (left >= 2) {
      if (left === 5 || left === 7 || left === 9) { list.push(5); left -= 5; }
      else { list.push(2); left -= 2; }
    }
    return list;
  };

  const report = [];

  for (const game of schedule) {
    if (!game.result) continue;
    const rnd = rngFrom(seedOf("pen-" + game.id));
    const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
    const kept = (game.plays || []).filter((p) => p.kind !== "penalty" && p.kind !== "faceoff");

    const periods = ["1", "2", "3"].concat(game.result.ot ? ["OT"] : []);
    const clockIn = (period) => {
      const secs = Math.floor(rnd() * (period === "OT" ? 5 : 20) * 60);
      return String(Math.floor(secs / 60)).padStart(2, "0") + ":"
        + String(secs % 60).padStart(2, "0");
    };

    const made = [];
    const addFor = (team, name, playerId, pim) => {
      for (const mins of split(pim)) {
        const period = pick(periods);
        made.push({
          id: "pen-" + game.id + "-" + made.length,
          kind: "penalty", team, period, clock: clockIn(period),
          player: name, playerId: playerId || null,
          minutes: mins,
          infraction: mins === 5 ? pick(MAJOR) : pick(MINOR),
        });
      }
    };

    /* gameStats[gameId] is the line map itself, keyed by player id. */
    const lines = (out.gameStats || {})[game.id] || {};
    for (const p of roster) {
      const pim = (lines[p.id] || {}).pim;
      if (pim) addFor("us", p.name, p.id, pim);
    }
    for (const row of ((out.opponentStats || {})[game.id] || [])) {
      if (row.pim) addFor("them", row.name, row.id || null, row.pim);
    }

    const draws = 11 + Math.floor(rnd() * 8);
    const usShare = 0.42 + rnd() * 0.16;
    const faceoffs = [];
    for (let i = 0; i < draws; i++) {
      const period = pick(periods);
      faceoffs.push({
        id: "fo-" + game.id + "-" + i,
        kind: "faceoff", team: rnd() < usShare ? "us" : "them",
        period, clock: clockIn(period), winner: "", winnerId: null,
      });
    }

    game.plays = [...kept, ...made, ...faceoffs];
    report.push({
      date: game.date,
      penalties: made.length,
      pimUs: made.filter((p) => p.team === "us").reduce((n, p) => n + p.minutes, 0),
      pimThem: made.filter((p) => p.team === "them").reduce((n, p) => n + p.minutes, 0),
      faceoffs: faceoffs.length,
    });
  }

  return { site: out, report };
};
