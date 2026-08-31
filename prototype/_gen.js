/**
 * Fill in scoring detail and recaps for every played game.
 *
 * DEMO CONTENT. The dataset this runs against is already flagged `demo: true`;
 * this adds goal-by-goal detail and recap articles in the same spirit. Nothing
 * here is a record of a real game.
 *
 * Why it also rewrites goals and assists: the demo generator produced box
 * scores that cannot happen — one game had two goals and thirteen assists, and
 * another listed five goals against a 4-goal final. Scoring plays built from
 * those would contradict the score on the same page. So each played game gets
 * a coherent set of goals matching the final score, 0-2 assists on each, and
 * the box score is rewritten to agree with the plays exactly. Penalty minutes,
 * shots and goaltender saves are left as they were.
 *
 * Deterministic: seeded from the game id, so re-running produces the same
 * result rather than a different fiction each time.
 */
window.__genScoring = function genScoring(site, opts) {
  const out = JSON.parse(JSON.stringify(site));
  const seasonKey = out.currentSeason;
  const season = out.seasons[seasonKey];
  const roster = season.roster || [];
  const schedule = season.schedule || [];
  const opponents = out.opponents || [];
  /* The opponent name is derived for the public site, not stored on the game -
     the schedule keys off opponentId. */
  const oppNameOf = (g) => (opponents.find((o) => o.id === g.opponentId) || {}).name || "Opponent";
  const report = [];

  /* ---- deterministic RNG, seeded per game ---- */
  const seedOf = (str) => {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  };
  const rngFrom = (seed) => {
    let s = seed || 1;
    return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  };

  const uid = (r) => Math.floor(r() * 1e9).toString(36) + Math.floor(r() * 1e9).toString(36);
  const pick = (r, list) => list[Math.floor(r() * list.length)];

  /* Weighted draw without replacement. Forwards score more than defence, and
     whoever the old box score liked stays prominent, so the season's leaders
     do not change identity just because the detail got rebuilt. */
  const draw = (r, pool, weights) => {
    let total = weights.reduce((a, b) => a + b, 0);
    if (total <= 0) return Math.floor(r() * pool.length);
    let t = r() * total;
    for (let i = 0; i < pool.length; i++) { t -= weights[i]; if (t <= 0) return i; }
    return pool.length - 1;
  };

  const PERIODS = ["1", "2", "3"];
  const mmss = (secs) => String(Math.floor(secs / 60)).padStart(2, "0") + ":" + String(secs % 60).padStart(2, "0");

  for (const game of schedule) {
    if (!game.result) continue;
    const r = rngFrom(seedOf(game.id));
    const usGoals = Number(game.result.us) || 0;
    const themGoals = Number(game.result.them) || 0;
    const ot = !!game.result.ot;

    const oldLines = (out.gameStats || {})[game.id] || {};
    const dressed = roster.filter((p) => (oldLines[p.id] || {}).dressed !== false);
    const skaters = dressed.filter((p) => p.position !== "G");
    const goalies = dressed.filter((p) => p.position === "G");
    if (!skaters.length) { report.push({ game: game.id, skipped: "no dressed skaters" }); continue; }

    const scoreWeight = (p) => {
      const l = oldLines[p.id] || {};
      const base = p.position === "D" ? 1 : 3;
      return base + (Number(l.g) || 0) * 4 + (Number(l.a) || 0);
    };
    const helpWeight = (p) => {
      const l = oldLines[p.id] || {};
      const base = p.position === "D" ? 2.5 : 2.5;
      return base + (Number(l.a) || 0) * 3 + (Number(l.g) || 0);
    };

    /* ---- our goals ---- */
    const goalRecords = [];
    for (let i = 0; i < usGoals; i++) {
      const w = skaters.map(scoreWeight);
      const scorer = skaters[draw(r, skaters, w)];
      const helpers = [];
      const nAssists = r() < 0.16 ? 0 : r() < 0.55 ? 1 : 2;
      const availableFor = skaters.filter((p) => p.id !== scorer.id);
      for (let k = 0; k < nAssists && availableFor.length; k++) {
        const pool = availableFor.filter((p) => !helpers.some((h) => h.id === p.id));
        if (!pool.length) break;
        helpers.push(pool[draw(r, pool, pool.map(helpWeight))]);
      }
      const roll = r();
      goalRecords.push({
        team: "us", scorer, assists: helpers,
        strength: roll < 0.18 ? "PP" : roll < 0.23 ? "SH" : "EV",
      });
    }

    /* ---- their goals, from the opponent lines already on file ---- */
    const oppList = ((out.opponentStats || {})[game.id] || []).filter((p) => !p.isGoalie);
    const themRecords = [];
    for (let i = 0; i < themGoals; i++) {
      const who = oppList.length ? oppList[Math.floor(r() * oppList.length)] : null;
      let helper = null;
      if (oppList.length > 1 && r() < 0.6) {
        const pool = oppList.filter((p) => !who || p.id !== who.id);
        helper = pool[Math.floor(r() * pool.length)];
      }
      const roll = r();
      themRecords.push({
        team: "them",
        scorerName: who ? who.name : oppNameOf(game),
        scorerId: who ? who.id : null,
        assistNames: helper ? [helper.name] : [],
        assistIds: helper ? [helper.id] : [],
        strength: roll < 0.16 ? "PP" : "EV",
      });
    }

    /* ---- put them in time order ---- */
    const all = [...goalRecords, ...themRecords];
    const times = [];
    for (let i = 0; i < all.length; i++) {
      const otGoal = ot && i === all.length - 1;
      const period = otGoal ? "OT" : PERIODS[Math.min(2, Math.floor(r() * 3))];
      /* Clock counts down from 20:00 (5:00 in overtime). */
      const len = otGoal ? 5 * 60 : 20 * 60;
      times.push({ period, secs: Math.floor(r() * (len - 20)) + 10, otGoal });
    }
    const order = { "1": 0, "2": 1, "3": 2, OT: 3 };
    const idx = all.map((_, i) => i).sort((a, b) => {
      const ta = times[a], tb = times[b];
      return order[ta.period] - order[tb.period] || (tb.secs - ta.secs);
    });
    /* An overtime winner is the last goal of the game by definition. */
    if (ot) {
      const otPos = idx.findIndex((i) => times[i].otGoal);
      if (otPos >= 0) idx.push(...idx.splice(otPos, 1));
    }

    const plays = idx.map((i) => {
      const rec = all[i];
      const t = times[i];
      const base = {
        id: uid(r), kind: "goal", team: rec.team,
        period: t.period, clock: mmss(t.secs), strength: rec.strength,
      };
      if (rec.team === "us") {
        return {
          ...base,
          scorer: rec.scorer.name, scorerId: rec.scorer.id,
          assists: rec.assists.map((p) => p.name),
          assistIds: rec.assists.map((p) => p.id),
        };
      }
      return {
        ...base,
        scorer: rec.scorerName, scorerId: rec.scorerId,
        assists: rec.assistNames, assistIds: rec.assistIds,
      };
    });

    /* ---- box score rewritten to agree with the plays ---- */
    const nextLines = {};
    for (const p of roster) {
      const old = oldLines[p.id] || {};
      nextLines[p.id] = { ...old, g: 0, a: 0 };
      if (old.dressed === false) nextLines[p.id].dressed = false;
    }
    for (const rec of goalRecords) {
      nextLines[rec.scorer.id].g = (nextLines[rec.scorer.id].g || 0) + 1;
      for (const h of rec.assists) nextLines[h.id].a = (nextLines[h.id].a || 0) + 1;
    }
    /* Power-play and short-handed goals are counted off the same plays, so the
       game-stats bars and the scoring summary cannot disagree. */
    for (const p of roster) { nextLines[p.id].ppg = 0; nextLines[p.id].shg = 0; }
    for (const rec of goalRecords) {
      if (rec.strength === "PP") nextLines[rec.scorer.id].ppg += 1;
      if (rec.strength === "SH") nextLines[rec.scorer.id].shg += 1;
    }
    /* The goaltender conceded what the other team scored. */
    const starter = goalies.find((p) => (oldLines[p.id] || {}).ga != null) || goalies[0];
    if (starter) {
      const l = nextLines[starter.id];
      const saves = Number((oldLines[starter.id] || {}).saves) || 0;
      nextLines[starter.id] = { ...l, ga: themGoals, saves, minutes: (oldLines[starter.id] || {}).minutes || 60 };
      for (const gk of goalies) if (gk.id !== starter.id) { nextLines[gk.id].ga = 0; nextLines[gk.id].saves = 0; }
    }

    out.gameStats = out.gameStats || {};
    out.gameStats[game.id] = nextLines;

    /* ---- opponent lines follow their plays too ---- */
    if (oppList.length) {
      const byId = new Map(((out.opponentStats || {})[game.id] || []).map((p) => [p.id, { ...p, g: 0, a: 0 }]));
      for (const rec of themRecords) {
        if (rec.scorerId && byId.has(rec.scorerId)) byId.get(rec.scorerId).g += 1;
        for (const aid of rec.assistIds) if (byId.has(aid)) byId.get(aid).a += 1;
      }
      out.opponentStats[game.id] = ((out.opponentStats || {})[game.id] || []).map((p) => byId.get(p.id) || p);
    }

    game.plays = plays;
    report.push({
      date: game.date, opponent: oppNameOf(game),
      score: usGoals + "-" + themGoals, plays: plays.length,
    });
  }

  return { site: out, report };
};
