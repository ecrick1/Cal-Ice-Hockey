/**
 * Write the historical play-by-play onto the seasons it belongs to.
 *
 * Same shape the 2025-26 plays use, so every screen that reads them - the
 * game centre, the scoresheet, the reconciler - works on these without
 * knowing they came from a different run.
 *
 * Two things this deliberately does not do:
 *
 *   - It does not touch a game that already has plays. 2025-26 was built and
 *     verified separately and is not going to be rewritten here.
 *   - It writes plays and shots, not box-score lines. The text report names
 *     players by surname only, and these rosters have their own duplicate
 *     surnames; guessing which "Lee" scored in order to build a season total
 *     would be inventing data. Where a surname matches exactly one player the
 *     goal is linked to them, and where it does not the name stands as text.
 */
window.__applyPbpHistory = function applyPbpHistory(site, games) {
  const out = JSON.parse(JSON.stringify(site));
  const uid = () => "h" + Math.random().toString(36).slice(2, 9);
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
  const surname = (n) => String(n || "").trim().split(/\s+/).slice(-1)[0];

  /* Report clocks count up from the start of a period; the site counts down. */
  const PERIOD_SECONDS = { "1": 1200, "2": 1200, "3": 1200, OT: 300, SO: 0 };
  const remaining = (period, at) => {
    const [m, s] = String(at || "0:00").split(":").map(Number);
    const left = Math.max(0, (PERIOD_SECONDS[period] ?? 1200) - ((m || 0) * 60 + (s || 0)));
    return String(Math.floor(left / 60)).padStart(2, "0") + ":" + String(left % 60).padStart(2, "0");
  };

  /* Not printed on a report, so read from the wording - the one inference. */
  const minutesFor = (txt) => {
    const t = String(txt || "").toLowerCase();
    if (/game misconduct|misconduct/.test(t)) return 10;
    if (/major|fighting|checking from behind|contact to the head/.test(t)) return 5;
    return 2;
  };

  const byGameId = new Map();
  for (const [key, season] of Object.entries(out.seasons || {})) {
    for (const g of season.schedule || []) {
      if (g.achaGameId) byGameId.set(String(g.achaGameId), { key, game: g, season });
    }
  }

  const report = { seasons: {}, written: 0, skipped: [], ambiguous: new Set(), unmatched: new Set() };

  for (const src of games) {
    const hit = byGameId.get(String(src.id));
    if (!hit) { report.skipped.push(src.id + " - no game on the schedule"); continue; }
    const { key, game, season } = hit;
    if ((game.plays || []).length) { report.skipped.push(src.id + " - already has plays"); continue; }

    const roster = season.roster || [];
    const resolve = (last) => {
      const hits = roster.filter((p) => norm(surname(p.name)) === norm(last));
      if (hits.length === 1) return { id: hits[0].id, name: hits[0].name };
      if (hits.length > 1) { report.ambiguous.add(key + ": " + last); return { id: null, name: last }; }
      report.unmatched.add(key + ": " + last);
      return { id: null, name: last };
    };

    const plays = [];
    const periods = [];
    for (const g of src.goals) if (!periods.includes(g.period)) periods.push(g.period);
    for (const p of src.pens) if (!periods.includes(p.period)) periods.push(p.period);
    const order = ["1", "2", "3", "OT"].filter((p) => periods.includes(p));

    /* Which penalty code is ours is read from the goals, which do carry full
       team names: whichever code appears on a penalty in a game we can tie to
       a Cal goal. Falling back to the more common code when a game has none. */
    const ourCode = (() => {
      const counts = {};
      for (const p of src.pens) counts[p.code] = (counts[p.code] || 0) + 1;
      const codes = Object.keys(counts);
      if (codes.length < 2) return codes[0] || null;
      /* "M2ucb" / "MD2ucb" - the tail is the school. */
      return codes.find((c) => /ucb|cal|berk/i.test(c)) || null;
    })();

    for (const per of order) {
      plays.push({ id: uid(), kind: "period", phase: "start", period: per, clock: per === "OT" ? "05:00" : "20:00" });

      const inPeriod = [
        ...src.goals.filter((g) => g.period === per).map((x) => ({ t: "g", x })),
        ...src.pens.filter((p) => p.period === per).map((x) => ({ t: "p", x })),
      ].sort((a, b) => {
        const s = (v) => { const [m, sec] = v.at.split(":").map(Number); return m * 60 + sec; };
        return s(a.x) - s(b.x);
      });

      for (const row of inPeriod) {
        if (row.t === "g") {
          const g = row.x;
          const mine = g.team === "us";
          const sc = mine ? resolve(g.scorer) : { id: null, name: g.scorer };
          const as = g.assists.map((a) => (mine ? resolve(a) : { id: null, name: a }));
          plays.push({
            id: uid(), kind: "goal", team: g.team, period: per, clock: remaining(per, g.at),
            strength: g.strength || "EV",
            scorer: sc.name, scorerId: sc.id,
            assists: as.map((a) => a.name), assistIds: as.map((a) => a.id),
          });
        } else {
          const p = row.x;
          const mine = ourCode ? p.code === ourCode : false;
          const who = mine && !p.bench ? resolve(p.player) : { id: null, name: p.player };
          const infraction = p.infractions.join(", ");
          plays.push({
            id: uid(), kind: "penalty", team: mine ? "us" : "them", period: per,
            clock: remaining(per, p.at),
            player: who.name, playerId: who.id,
            minutes: minutesFor(infraction), infraction,
          });
        }
      }

      plays.push({ id: uid(), kind: "period", phase: "end", period: per, clock: "00:00" });
    }

    /* The shootout, and the goal it puts on the board. */
    let shootout = null;
    if (src.shootout && (src.shootout.us.length || src.shootout.them.length)) {
      const attempts = [];
      const n = Math.max(src.shootout.us.length, src.shootout.them.length);
      for (let i = 0; i < n; i++) {
        for (const side of ["us", "them"]) {
          const a = src.shootout[side][i];
          if (!a) continue;
          const who = side === "us" ? resolve(a.name) : { id: null, name: a.name };
          attempts.push({
            id: uid(), team: side, player: who.name, playerId: who.id,
            shot: "", result: a.scored ? "goal" : "nogoal", scored: a.scored,
          });
        }
      }
      /* The sheet lists each side's attempts in order but not how the two
         interleaved, so they are alternated and that is recorded. */
      shootout = { attempts, orderAssumed: true };

      const usG = src.shootout.us.filter((a) => a.scored).length;
      const themG = src.shootout.them.filter((a) => a.scored).length;
      const side = usG > themG ? "us" : "them";
      const last = [...src.shootout[side]].reverse().find((a) => a.scored);
      const who = side === "us" && last ? resolve(last.name) : { id: null, name: last ? last.name : "Shootout Winner" };
      plays.push({
        id: uid(), kind: "goal", team: side, period: "SO", clock: "", strength: "SO",
        scorer: who.name, scorerId: who.id, assistIds: [], assists: [],
      });
    }

    plays.push({
      id: uid(), kind: "game", phase: "end",
      period: shootout ? "SO" : (order[order.length - 1] || "3"),
      clock: shootout ? "" : "00:00",
      us: src.final.us, them: src.final.them,
    });

    game.plays = plays;
    if (shootout) game.shootout = shootout;

    /* Shots by period, and the totals, in the shape the game page reads. */
    const us = src.shots.us || null;
    const them = src.shots.them || null;
    if (us && them) {
      const periodShots = {};
      const cols = ["1", "2", "3", "OT", "SO"];
      for (let i = 0; i < Math.min(us.length, them.length) - 1; i++) {
        periodShots[cols[i] || String(i + 1)] = { us: us[i], them: them[i] };
      }
      game.live = {
        periodShots,
        shotsUs: us[us.length - 1],
        shotsThem: them[them.length - 1],
      };
    }

    report.seasons[key] = (report.seasons[key] || 0) + 1;
    report.written++;
  }

  report.ambiguous = [...report.ambiguous];
  report.unmatched = [...report.unmatched];
  return { site: out, report };
};
