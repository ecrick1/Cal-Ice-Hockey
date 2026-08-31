/**
 * Backfill the period marks every played game must have had.
 *
 * A completed game had three periods, and each of them started and ended -
 * that is not a guess, it is what "final" means. So the play-by-play of an
 * older game gets those bookends even though nobody was tapping a console at
 * the time. Overtime is added only where the result says the game went there.
 *
 * Two things it deliberately does NOT invent: an overtime that ended on a goal
 * gets no end mark, because sudden death ends when the puck goes in and not at
 * 00:00; and no stoppages are added beyond period marks, because which
 * whistles happened is genuinely unknown.
 *
 * Idempotent: existing period marks are stripped and rebuilt, so running it
 * twice leaves the same result.
 */
window.__addPeriodMarks = function addPeriodMarks(site) {
  const out = JSON.parse(JSON.stringify(site));
  const seasonKey = out.currentSeason;
  const schedule = (out.seasons[seasonKey] || {}).schedule || [];
  const report = [];

  const secs = (clock) => {
    const m = /^(\d+):(\d+)$/.exec(String(clock || ""));
    return m ? Number(m[1]) * 60 + Number(m[2]) : 0;
  };

  for (const game of schedule) {
    if (!game.result) continue;

    /* Anything already marked is dropped and rebuilt from scratch. */
    const plays = (game.plays || [])
      .filter((p) => p.kind !== "period" && p.kind !== "game");
    const ot = !!game.result.ot;
    const decidedInOt = plays.some((p) => p.kind === "goal" && p.period === "OT");
    const periods = ["1", "2", "3"].concat(ot ? ["OT"] : []);
    const known = new Set(periods);

    const mark = (phase, period, clock) => ({
      /* Stable id: the same game, period and phase always produce the same
         one, so a rerun does not churn React keys. */
      id: "pm-" + game.id + "-" + period + "-" + phase,
      kind: "period", phase, period, clock,
    });

    const next = [];
    for (const p of periods) {
      next.push(mark("start", p, p === "OT" ? "05:00" : "20:00"));
      /* The clock counts down, so earlier plays hold the higher time. */
      next.push(...plays
        .filter((x) => x.period === p)
        .sort((a, b) => secs(b.clock) - secs(a.clock)));
      if (!(p === "OT" && decidedInOt)) next.push(mark("end", p, "00:00"));
    }
    /* A shootout, or anything with a period we do not model, keeps its place
       at the end rather than being dropped. */
    next.push(...plays.filter((x) => !known.has(x.period)));

    /* The final whistle. It lands where the game actually finished: at 00:00
       of the last period normally, but on the goal itself when overtime
       decided it. */
    const last = periods[periods.length - 1];
    const decider = decidedInOt
      ? plays.filter((x) => x.period === "OT").sort((a, b) => secs(a.clock) - secs(b.clock))[0]
      : null;
    /* A shootout decided it, so the whistle belongs to the shootout and not
       to the overtime that preceded it - and a shootout has no clock. */
    const so = !!game.result.so;
    next.push({
      id: "gm-" + game.id + "-end",
      kind: "game", phase: "end",
      period: so ? "SO" : last,
      clock: so ? "" : (decider ? decider.clock : "00:00"),
      us: Number(game.result.us) || 0,
      them: Number(game.result.them) || 0,
    });

    game.plays = next;
    report.push({
      date: game.date,
      periods: periods.join("/"),
      marks: next.filter((x) => x.kind === "period").length,
      total: next.length,
    });
  }

  return { site: out, report };
};
