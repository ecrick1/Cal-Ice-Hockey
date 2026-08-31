/**
 * Write the historical box scores onto their games.
 *
 * Players are matched on the ACHA id both sides carry, not on a name. The
 * 2025-26 import had to match by name because its roster came from
 * EliteProspects, and that is how it found a player wearing someone else's
 * number for seven games; these rosters came from the ACHA's own feed, so the
 * ids line up exactly and the two Lees are not a problem.
 *
 * What gets written:
 *   - gameStats[gameId]: a line per player who dressed, and everyone else on
 *     the roster marked a scratch, so the sheet is complete rather than
 *     silent about who sat out.
 *   - opponentStats[gameId]: their side, in the shape the game centre reads.
 *
 * Power-play and short-handed goals, and the game-winner, are not in this
 * feed; they are read off the play-by-play already imported, which carries
 * each goal's strength. A zero would quietly look like a real figure, so
 * anything the data cannot support is left absent instead.
 */
window.__applyBoxHistory = function applyBoxHistory(site, box) {
  const out = JSON.parse(JSON.stringify(site));
  out.gameStats = { ...(out.gameStats || {}) };
  out.opponentStats = { ...(out.opponentStats || {}) };

  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
  const byGameId = new Map();
  for (const [key, season] of Object.entries(out.seasons || {})) {
    for (const g of season.schedule || []) {
      if (g.achaGameId) byGameId.set(String(g.achaGameId), { key, game: g, season });
    }
  }

  const report = { seasons: {}, written: 0, skipped: [], byName: [], unmatched: [], added: [] };

  for (const src of box) {
    const hit = byGameId.get(String(src.id));
    if (!hit) { report.skipped.push(src.id + " - not on any schedule"); continue; }
    const { key, game, season } = hit;
    if (out.gameStats[game.id]) { report.skipped.push(src.id + " - already has a box score"); continue; }

    const roster = season.roster || [];
    const byAcha = new Map(roster.filter((p) => p.achaId).map((p) => [String(p.achaId), p]));
    const byName = new Map(roster.map((p) => [norm(p.name), p]));

    const match = (p) => {
      const byId = byAcha.get(String(p.id));
      if (byId) return byId;
      /* Falling back to a full name, not a surname - a surname is what makes
         two Lees indistinguishable. Any use of it is reported. */
      const nm = byName.get(norm(p.first + p.last));
      if (nm) { report.byName.push(key + ": " + p.first + " " + p.last); return nm; }

      /* Dressed, with a line in the box score, but not on the roster the
         league published for that season. The roster page is a snapshot and
         misses late additions; the box score is a record of someone actually
         playing. Discarding the line would lose real games, so the player is
         added to the season instead. */
      const added = {
        id: "x" + Math.random().toString(36).slice(2, 9),
        name: p.first + " " + p.last,
        number: p.number || "",
        position: p.saves !== undefined ? "G" : (p.pos === "D" ? "D" : "F"),
        shoots: "", height: "", weight: "", hometown: "", year: "",
        achaId: p.id || null,
        addedFromBoxScore: true,
        stats: {},
      };
      season.roster = [...(season.roster || []), added];
      byAcha.set(String(p.id), added);
      byName.set(norm(added.name), added);
      report.added.push(key + ": " + added.name + " #" + added.number);
      return added;
    };

    /* Strength and the winner come from the plays, which this game already
       has, rather than being assumed. */
    const plays = game.plays || [];
    const ourGoals = plays.filter((p) => p.kind === "goal" && p.team === "us" && p.period !== "SO");
    const strengthCount = (last, strength) => ourGoals.filter((x) =>
      x.strength === strength && norm(String(x.scorer).split(/\s+/).slice(-1)[0]) === norm(last)).length;

    const res = game.result || {};
    const winnerIsUs = res.us > res.them;
    const gwIndex = winnerIsUs ? Number(res.them) : -1;
    const gwGoal = winnerIsUs ? ourGoals[gwIndex] : null;

    const lines = {};
    const dressed = new Set();
    for (const p of [...src.us.skaters, ...src.us.goalies]) {
      const player = match(p);
      if (!player) continue;
      dressed.add(player.id);
      const isGw = !!(gwGoal && norm(String(gwGoal.scorer).split(/\s+/).slice(-1)[0]) === norm(p.last));
      lines[player.id] = {
        dressed: true,
        g: p.g, a: p.a, pim: p.pim, shots: p.shots,
        ppg: strengthCount(p.last, "PP"),
        shg: strengthCount(p.last, "SH"),
        gwg: isGw ? 1 : 0,
        ...(p.saves !== undefined
          ? { saves: p.saves, ga: p.ga, minutes: Math.round(toMinutes(p.toi)) }
          : {}),
      };
    }
    /* Read after the loop, because a player can have just been added to it. */
    for (const p of season.roster || []) if (!dressed.has(p.id)) lines[p.id] = { dressed: false };
    out.gameStats[game.id] = lines;

    out.opponentStats[game.id] = [...src.them.skaters, ...src.them.goalies].map((p) => ({
      id: "acha-" + p.id,
      name: p.first + " " + p.last,
      number: p.number,
      position: p.pos,
      isGoalie: p.saves !== undefined,
      g: p.g, a: p.a, pim: p.pim, shots: p.shots,
      ...(p.saves !== undefined ? { saves: p.saves, ga: p.ga } : {}),
    }));

    report.seasons[key] = (report.seasons[key] || 0) + 1;
    report.written++;
  }

  report.byName = [...new Set(report.byName)];
  report.unmatched = [...new Set(report.unmatched)];
  report.added = [...new Set(report.added)];
  return { site: out, report };

  function toMinutes(toi) {
    if (!toi) return 0;
    const [m, s] = String(toi).split(":").map(Number);
    return (m || 0) + (s || 0) / 60;
  }
};
