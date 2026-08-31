/**
 * Fill in Cal's ACHA history: rosters and schedules for every season the
 * league publishes.
 *
 * REAL DATA from the ACHA's own stats feed - the same source the verified
 * 2025-26 import came from.
 *
 * Rules it holds to:
 *
 *   - A season that already has games or a roster is left alone. 2025-26 was
 *     built from three reconciled sources and is not going to be overwritten
 *     by a second pass at the same feed.
 *   - The feed's dates carry no year ("Fri, Oct 1"), so the year comes from
 *     the season span: August to December is the first year, January onwards
 *     the second. That is the only inference here.
 *   - `record` on a season is an override for seasons with no game log. Once
 *     a season has one it is computed instead, so the override is cleared -
 *     but only after checking the two agree, because a disagreement is worth
 *     seeing rather than silently resolving.
 */
window.__applyAcha = function applyAcha(site, data, opts) {
  const dry = !(opts && opts.write);
  const out = JSON.parse(JSON.stringify(site));
  out.opponents = [...(out.opponents || [])];
  out.seasons = { ...(out.seasons || {}) };

  const MONTHS = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6,
    Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12 };
  const uid = () => "a" + Math.random().toString(36).slice(2, 9);
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  /* "2024-2025 Men's Divisions" -> the key the site uses, and the two years
     a date in that season can belong to. */
  const spanOf = (name) => {
    const m = String(name).match(/(\d{4})-(\d{2,4})/);
    if (!m) return null;
    const y1 = Number(m[1]);
    const y2 = m[2].length === 4 ? Number(m[2]) : Number(String(y1).slice(0, 2) + m[2]);
    return { key: y1 + "-" + String(y2).slice(2), y1, y2 };
  };

  const dateOf = (span, txt) => {
    const m = String(txt || "").match(/([A-Z][a-z]{2})\s+(\d{1,2})/);
    if (!m) return "";
    const mm = MONTHS[m[1]];
    if (!mm) return "";
    const year = mm >= 8 ? span.y1 : span.y2;
    return year + "-" + String(mm).padStart(2, "0") + "-" + String(Number(m[2])).padStart(2, "0");
  };

  /* "MD2 San Jose State University" is a division tag, a name, and usually
     the word University. The library keeps the short form. */
  const cleanTeam = (s) => String(s || "")
    .replace(/^M(D)?\d+\s+/, "")
    .replace(/\s+University$/, "")
    .replace(/^University of\s+/, "")
    .trim();

  const findOpp = (rawName) => {
    const clean = cleanTeam(rawName);
    const hit = (out.opponents || []).find((o) =>
      norm(o.name) === norm(clean) || norm(o.name) === norm(rawName)
      || norm(clean).includes(norm(o.name)) || norm(o.name).includes(norm(clean)));
    if (hit) return { id: hit.id, created: false, name: hit.name };
    const row = {
      id: uid(), name: clean, short: clean.slice(0, 4).toUpperCase(),
      color: "#5A6473", logoLight: null, logoDark: null,
    };
    if (!dry) out.opponents.push(row);
    return { id: row.id, created: true, name: clean };
  };

  const report = { seasons: [], skipped: [], newOpponents: [], recordChecks: [] };

  for (const s of data) {
    const span = spanOf(s.seasonName);
    if (!span) continue;
    if (!s.players.length && !s.games.length) { report.skipped.push(span.key + " - nothing published"); continue; }

    const existing = out.seasons[span.key];
    if (existing && ((existing.schedule || []).length || (existing.roster || []).length)) {
      report.skipped.push(span.key + " - already has "
        + (existing.roster || []).length + " players and "
        + (existing.schedule || []).length + " games");
      continue;
    }

    const roster = s.players.map((p) => ({
      id: uid(),
      name: p.name,
      number: p.number || "",
      position: /goal/i.test(p.section) ? "G" : /defen/i.test(p.section) ? "D" : "F",
      shoots: p.shoots || "",
      height: p.height ? p.height.replace("-", "' ") + '"' : "",
      weight: p.weight || "",
      hometown: p.hometown || "",
      year: "",
      achaId: p.id || null,
      stats: {},
    }));

    const schedule = [];
    for (const g of s.games) {
      const date = dateOf(span, g.date_with_day);
      const homeIsUs = /California-Berkeley/i.test(g.home_team_city || "");
      const oppRaw = homeIsUs ? g.visiting_team_city : g.home_team_city;
      const opp = findOpp(oppRaw);
      if (opp.created) report.newOpponents.push(opp.name);

      /* A forfeit is a result as far as the standings are concerned - the
         league's own record for 2022-23 and 2024-25 counts one each, and the
         feed carries the score alongside the status. Only a game with no
         score at all (postponed, or not yet played) has no result. */
      const status = g.game_status || "";
      const decided = /final|forfeit/i.test(status);
      const forfeit = /forfeit/i.test(status);
      const hg = Number(g.home_goal_count);
      const vg = Number(g.visiting_goal_count);
      const haveScore = decided && Number.isFinite(hg) && Number.isFinite(vg);

      schedule.push({
        id: "acha-" + s.seasonId + "-" + g.game_id,
        date,
        opponentId: opp.id,
        homeAway: homeIsUs ? "H" : "A",
        venue: g.venue_name || "",
        location: "",
        time: decided ? "" : status,
        gameType: "regular",
        roundLabel: "",
        streamUrl: "", replayUrl: "",
        achaGameId: g.game_id,
        ...(forfeit ? { forfeit: true } : {}),
        result: haveScore
          ? { us: homeIsUs ? hg : vg, them: homeIsUs ? vg : hg,
              ot: /\bOT\b/i.test(status), so: /\bSO\b/i.test(status) }
          : null,
      });
    }
    schedule.sort((a, b) => (a.date || "").localeCompare(b.date || ""));

    /* What the games say, against whatever override the season carried. */
    let w = 0, l = 0, t = 0;
    for (const g of schedule) {
      if (!g.result) continue;
      if (g.result.us > g.result.them) w++;
      else if (g.result.us < g.result.them) l++;
      else t++;
    }
    const prev = (existing || {}).record;
    if (prev && (prev.w || prev.l || prev.t)) {
      const same = Number(prev.w || 0) === w && Number(prev.l || 0) === l && Number(prev.t || 0) === t;
      report.recordChecks.push(span.key + ": override " + (prev.w || 0) + "-" + (prev.l || 0) + "-" + (prev.t || 0)
        + " vs games " + w + "-" + l + "-" + t + (same ? " ✓" : "  DIFFERS"));
    }

    if (!dry) {
      out.seasons[span.key] = {
        ...(existing || {}),
        label: existing && existing.label ? existing.label : span.key,
        roster,
        schedule,
        /* Computed from the game log now, so the override goes. */
        record: schedule.some((g) => g.result) ? null : (existing || {}).record || null,
      };
    }

    report.seasons.push({
      season: span.key, players: roster.length, games: schedule.length,
      withResults: schedule.filter((g) => g.result).length, record: w + "-" + l + "-" + t,
      firstDate: (schedule[0] || {}).date, lastDate: (schedule[schedule.length - 1] || {}).date,
    });
  }

  report.newOpponents = [...new Set(report.newOpponents)];
  return { site: out, report };
};
