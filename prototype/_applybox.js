/**
 * Apply the per-game box scores to the 2025-26 season.
 *
 * Writes site.gameStats (our players) and site.opponentStats (theirs) so the
 * Box Score tab has rosters, and scratches can be told from the dressed.
 *
 * This changes where season totals come from. boxScoreTotals() prefers a game
 * log over the roster row, so once these exist every season figure on the site
 * is a sum of thirty games rather than a number typed from the season page.
 * That is only safe because the two agree - _box2526.mjs refuses to write its
 * file unless they do - and it is better, because a total that is derived
 * cannot drift from the games underneath it.
 *
 * Three things the feed does not carry, all derived from the play data rather
 * than left at zero, since a zero would quietly replace a correct figure:
 *   - power-play and short-handed goals, from each goal's strength
 *   - the game-winning goal, which is the winner's (loser's total + 1)th
 *   - shootout goals, which belong to no player's line at all
 */
window.__applyBox = function applyBox(site, box, pbp) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  const roster = season.roster || [];
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
  const byNumber = new Map(roster.filter((p) => p.number).map((p) => [String(p.number), p]));
  const byName = new Map(roster.map((p) => [norm(p.name), p]));

  /* Name first, not number. Jersey numbers move during a season - Simon
     Mantoani appears in seven games wearing 96, which is Eric Khodorenko's
     number on our roster - so matching on the number silently files one
     player's game under another. Stripping punctuation already reconciles
     "Odowd" with "O'Dowd"; only a genuinely different first name needs an
     alias. Number stays as a last resort, and any use of it is reported. */
  const ALIAS = { johnburbank: "jackburbank" };
  const usedNumber = new Set();
  const match = (p) => {
    const k = norm(p.first + p.last);
    const byAlias = byName.get(ALIAS[k] || k);
    if (byAlias) return byAlias;
    const n = byNumber.get(String(p.number));
    if (n) usedNumber.add(p.first + " " + p.last + " #" + p.number + " -> " + n.name);
    return n || null;
  };

  const pbpByDate = new Map((pbp || []).map((g) => [g.date, g]));
  const unmatched = new Set();
  const report = { games: 0, lines: 0, scratches: 0, unmatched: [] };

  out.gameStats = { ...(out.gameStats || {}) };
  out.opponentStats = { ...(out.opponentStats || {}) };

  const byDate = new Map((season.schedule || []).map((g) => [g.date, g]));

  for (const src of box) {
    const game = byDate.get(src.date);
    if (!game) continue;
    const plays = (pbpByDate.get(src.date) || {}).goals || [];

    /* Which of our goals were on the power play, short-handed, or the winner. */
    const ourGoals = plays.filter((x) => x.team === "us");
    const theirTotal = (pbpByDate.get(src.date) || {}).final;
    const winnerIsUs = theirTotal && theirTotal.us > theirTotal.them;
    const winnerIsThem = theirTotal && theirTotal.them > theirTotal.us;
    const gwIndex = winnerIsUs ? theirTotal.them : winnerIsThem ? theirTotal.us : -1;
    const gwGoal = winnerIsUs ? ourGoals[gwIndex] : null;

    const countFor = (surname, strength) => ourGoals
      .filter((x) => x.strength === strength && norm(x.scorer) === norm(surname)).length;

    const lines = {};
    const dressed = new Set();
    for (const p of [...src.us.skaters, ...src.us.goalies]) {
      const player = match(p);
      if (!player) { unmatched.add(p.first + " " + p.last + " #" + p.number); continue; }
      dressed.add(player.id);
      const isGw = !!(gwGoal && norm(gwGoal.scorer) === norm(p.last));
      lines[player.id] = {
        dressed: true,
        g: p.g, a: p.a, pim: p.pim, shots: p.shots,
        ppg: countFor(p.last, "PP"),
        shg: countFor(p.last, "SH"),
        gwg: isGw ? 1 : 0,
        ...(p.saves !== undefined
          ? { saves: p.saves, ga: p.ga, minutes: Math.round(toMinutes(p.toi)) }
          : {}),
      };
      report.lines++;
    }
    /* Everyone else on the roster was a scratch for this game. */
    for (const p of roster) {
      if (!dressed.has(p.id)) { lines[p.id] = { dressed: false }; report.scratches++; }
    }
    out.gameStats[game.id] = lines;

    out.opponentStats[game.id] = [...src.them.skaters, ...src.them.goalies].map((p) => ({
      id: "acha-" + p.id,
      name: p.first + " " + p.last,
      number: p.number,
      position: p.pos,
      g: p.g, a: p.a, pim: p.pim, shots: p.shots,
      ...(p.saves !== undefined ? { saves: p.saves, ga: p.ga } : {}),
    }));

    report.games++;
  }

  report.unmatched = [...unmatched];
  report.matchedByNumberNotName = [...usedNumber];
  return { site: out, report };

  function toMinutes(toi) {
    if (!toi) return 0;
    const [m, s] = String(toi).split(":").map(Number);
    return (m || 0) + (s || 0) / 60;
  }
};
