/**
 * Apply the parsed ACHA game reports to the 2025-26 schedule.
 *
 * Reads _pbp2526.json (written by _pbp2526.mjs) and turns each game's goals
 * and penalties into plays on the matching game. Run __addPeriodMarks
 * afterwards to add the period start/end marks and sort each period.
 *
 * What it writes: plays only. It deliberately does NOT write per-game box
 * score lines, because boxScoreTotals() prefers those over the roster row -
 * and the roster row holds the ACHA's own season totals, which are exact.
 * Deriving season stats from thirty parsed sheets instead would replace known
 * figures with inferred ones for no gain.
 *
 * Two honest gaps, both reported rather than papered over:
 *
 *  - The reports name players by surname. Every Cal surname resolves to one
 *    roster player except "Lee", who is either Jason or Ryan. Those plays keep
 *    the surname and carry no player id, so nothing links to the wrong person.
 *
 *  - Penalty minutes are not printed, only the infraction. They are inferred
 *    from the wording (major 5, misconduct 10, everything else 2) and the
 *    season total that implies is compared against the ACHA's own PIM. The
 *    difference is reported; the box score is left alone either way.
 */
window.__applyPbp = function applyPbp(site, data) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  const roster = season.roster || [];
  /* Surname -> the players who share it. */
  const bySurname = new Map();
  for (const p of roster) {
    const s = (p.name || "").trim().split(/\s+/).slice(1).join(" ").toLowerCase();
    if (!s) continue;
    if (!bySurname.has(s)) bySurname.set(s, []);
    bySurname.get(s).push(p);
  }
  /* The reports drop the apostrophe. */
  const ALIAS = { odowd: "o'dowd" };
  const look = (surname) => {
    const k = String(surname || "").trim().toLowerCase();
    return bySurname.get(ALIAS[k] || k) || [];
  };
  const ambiguous = new Set();
  const unknown = new Set();
  /* One name, one player - or nothing. A surname two players share resolves
     to neither, because guessing would credit the wrong one. */
  const resolve = (surname) => {
    const hits = look(surname);
    if (hits.length === 1) return hits[0];
    if (hits.length > 1) ambiguous.add(surname);
    else unknown.add(surname);
    return null;
  };

  /* The reports count up from the start of a period; the site counts down. */
  const LEN = { OT: 5 * 60 };
  const clockOf = (period, at) => {
    const [m, s] = String(at).split(":").map(Number);
    const len = LEN[period] || 20 * 60;
    const left = Math.max(0, len - (m * 60 + s));
    return String(Math.floor(left / 60)).padStart(2, "0") + ":" +
      String(left % 60).padStart(2, "0");
  };

  /* No minutes on the sheet, so they come from the wording. */
  const minutesFor = (infraction) => {
    const t = infraction.toLowerCase();
    if (/\bmajor\b|fighting/.test(t)) return 5;
    if (/misconduct|disqualification|\bdq\b/.test(t)) return 10;
    return 2;
  };

  const byDate = new Map((season.schedule || []).map((g) => [g.date, g]));
  const report = { games: 0, goals: 0, penalties: 0, unmatchedGames: [],
    ambiguousNames: [], unknownNames: [] };

  for (const src of data) {
    const game = byDate.get(src.date);
    if (!game) { report.unmatchedGames.push(src.date + " " + src.opponent); continue; }

    const plays = [];
    let n = 0;
    for (const g of src.goals) {
      const mine = g.team === "us";
      const scorer = mine ? resolve(g.scorer) : null;
      const assists = g.assists.map((a) => (mine ? resolve(a) : null));
      plays.push({
        id: "pb-" + src.id + "-g" + (n++),
        kind: "goal", team: g.team, period: g.period, clock: clockOf(g.period, g.at),
        scorer: scorer ? scorer.name : g.scorer,
        scorerId: scorer ? scorer.id : null,
        assists: g.assists.map((a, i) => (assists[i] ? assists[i].name : a)),
        assistIds: assists.map((p) => (p ? p.id : null)),
        strength: g.strength,
      });
    }
    for (const p of src.pens) {
      const mine = p.team === "us";
      const who = mine && !p.bench ? resolve(p.player) : null;
      const infraction = p.infractions.join(" + ");
      plays.push({
        id: "pb-" + src.id + "-p" + (n++),
        kind: "penalty", team: p.team, period: p.period, clock: clockOf(p.period, p.at),
        player: who ? who.name : p.player,
        playerId: who ? who.id : null,
        minutes: p.infractions.reduce((t, x) => t + minutesFor(x), 0),
        infraction,
      });
    }

    /* The shootout winner. It is a goal on the scoresheet - it decides the
       game and counts in the final - but it belongs to no period of play, so
       it sits in its own SO column rather than inflating the third. */
    if (src.shootout) {
      for (const sc of src.shootout.scorers) {
        const mine = sc.team === "us";
        const who = mine ? resolve(sc.name) : null;
        plays.push({
          id: "pb-" + src.id + "-so" + (n++),
          kind: "goal", team: sc.team, period: "SO", clock: "00:00",
          scorer: who ? who.name : sc.name,
          scorerId: who ? who.id : null,
          assists: [], assistIds: [], strength: "SO",
        });
      }
      /* The round-by-round list. The report gives each team's attempts in
         order but not how the two interleaved, and the rules alternate, so
         they are zipped one for one. The home side is put second, which is
         the usual order but is an assumption rather than something the sheet
         states. */
      const home = src.calHome ? "us" : "them";
      const away = src.calHome ? "them" : "us";
      const rows = [];
      const A = src.shootout.attempts || { us: [], them: [] };
      for (let i = 0; i < Math.max(A.us.length, A.them.length); i++) {
        for (const side of [away, home]) {
          const a = A[side][i];
          if (!a) continue;
          const who = side === "us" ? resolve(a.name) : null;
          rows.push({
            id: "so-" + src.id + "-" + rows.length,
            team: side,
            player: who ? who.name : a.name,
            playerId: who ? who.id : null,
            shot: "",
            /* The scoresheet marks an attempt G or NG and nothing more, so a
               miss is recorded as "no goal" rather than guessed to be a save.
               Games scored live in the console can say which. */
            result: a.scored ? "goal" : "nogoal",
            scored: !!a.scored,
          });
        }
      }
      game.shootout = { attempts: rows, orderAssumed: true };
      game.result = { ...(game.result || {}), so: true, ot: true };
    }

    game.plays = plays;
    report.games++;
    report.goals += src.goals.length;
    report.penalties += src.pens.length;
  }

  report.ambiguousNames = [...ambiguous];
  report.unknownNames = [...unknown];

  /* What our inferred minutes add up to, against what the ACHA says. */
  const fromPlays = (season.schedule || []).reduce((t, g) =>
    t + (g.plays || []).filter((x) => x.kind === "penalty" && x.team === "us")
      .reduce((n, x) => n + x.minutes, 0), 0);
  const fromStats = roster.reduce((t, p) => t + (Number((p.stats || {}).pim) || 0), 0);
  report.pimFromPlays = fromPlays;
  report.pimFromAchaStats = fromStats;
  report.pimDifference = fromPlays - fromStats;

  return { site: out, report };
};
