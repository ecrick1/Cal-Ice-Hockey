/**
 * A recap article for every finished 2025-26 game.
 *
 * The prose here is generated - these are demo articles, not the team's
 * writing - but every FACT in them is read out of the game record already on
 * the site: the scorers, assists, strengths and times come from the imported
 * play-by-play, the saves from the box score, the venue from the schedule.
 * Nothing is invented, so nothing can contradict the box score a reader can
 * open in the next tab. Where the record does not say something, the
 * sentence is left out rather than filled in.
 *
 * Two games are skipped because the club published a real article about
 * them: a generated recap must never sit on top of the team's own writing.
 * Those articles are linked to their games instead, along with two previews.
 */
window.__applyRecaps = function applyRecaps(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  const opps = out.opponents || [];
  const oppOf = (g) => opps.find((o) => o.id === g.opponentId) || {};
  /* Re-runnable: a previous pass's generated recaps are dropped rather than
     duplicated. Only articles this file wrote are touched - the club's own
     ones carry no `generated` flag and survive. */
  const news = (out.news || []).filter((n) => !n.generated);
  for (const g of season.schedule || []) {
    if (g.recapId && !(out.news || []).some((n) => n.id === g.recapId && !n.generated)) delete g.recapId;
  }
  const uid = () => "r" + Math.random().toString(36).slice(2, 9);

  /* ---- the club's own articles, matched to the games they describe ----
     Matched by reading them, not by date arithmetic: article 13 names the
     4-1 USC win of January 24, article 11 opens on the 6-2 Big Freeze loss,
     and the two previews name the weekend they look ahead to. */
  const OWN = [
    ["Golden Bears Respond on Senior Night", "2026-01-24", "recapId"],
    ["Cal Splits Weekend Series with LMU", "2025-11-15", "recapId"],
    ["California Ice Hockey Gearing up for the Crown Jewel", "2025-11-15", "previewId"],
    ["Golden Bears Back on the Ice After Winter Break", "2026-01-16", "previewId"],
  ];
  const byDate = new Map((season.schedule || []).map((g) => [g.date, g]));
  const linkedOwn = [];
  const claimed = new Set();
  for (const [titleStart, date, field] of OWN) {
    const story = news.find((n) => (n.title || "").startsWith(titleStart));
    const game = byDate.get(date);
    if (!story || !game) { linkedOwn.push("MISSED " + date + " " + titleStart); continue; }
    game[field] = story.id;
    if (field === "recapId") claimed.add(date);
    linkedOwn.push(date + " " + field + " <- " + story.title.slice(0, 44));
  }

  /* ---- helpers over the game record ---- */
  const ORD = { "1": "first", "2": "second", "3": "third", OT: "overtime" };
  const surname = (n) => String(n || "").trim().split(/\s+/).slice(-1)[0];
  const list = (a) =>
    a.length <= 1 ? (a[0] || "") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
  const plural = (n, one, many) => n + " " + (n === 1 ? one : many);
  const times = (n) => (n === 1 ? "once" : n === 2 ? "twice" : n + " times");

  const made = [];
  const skipped = [];

  for (const game of season.schedule || []) {
    const r = game.result;
    if (!r || r.us == null || r.them == null) { skipped.push(game.date + " - no result"); continue; }
    if (claimed.has(game.date)) { skipped.push(game.date + " - club article"); continue; }

    const o = oppOf(game);
    const them = o.name || "the opposition";
    const home = game.homeAway === "H";
    const win = r.us > r.them, loss = r.us < r.them;
    const decided = r.so ? " in a shootout" : r.ot ? " in overtime" : "";
    const goals = (game.plays || []).filter((p) => p.kind === "goal");
    const ours = goals.filter((p) => p.team === "us" && p.period !== "SO");

    /* Who scored, most goals first, then alphabetically - so the order is
       stable rather than dependent on the order goals arrived in. */
    const tally = new Map();
    for (const g of ours) tally.set(g.scorer, (tally.get(g.scorer) || 0) + 1);
    const scorers = [...tally.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    const multi = scorers.filter(([, n]) => n > 1);

    const helpers = new Map();
    for (const g of ours) for (const a of g.assists || []) helpers.set(a, (helpers.get(a) || 0) + 1);
    /* "Led the way with 1 assist" is not a fact about anyone when four
       players had one each. A leader is only named when the count is
       actually higher than everyone else's. */
    const ranked = [...helpers.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    const topAssist = ranked.length && (ranked.length === 1 || ranked[0][1] > ranked[1][1])
      ? ranked[0] : null;

    /* The goaltender who actually played, from the box score - the one with
       the most minutes when two dressed and both saw the ice. */
    const lines = (out.gameStats || {})[game.id] || {};
    const roster = season.roster || [];
    let keeper = null;
    for (const [pid, ln] of Object.entries(lines)) {
      if (!ln || !ln.dressed) continue;
      if (!(Number(ln.saves) || Number(ln.minutes))) continue;
      const p = roster.find((x) => x.id === pid);
      if (!p) continue;
      if (!keeper || (Number(ln.minutes) || 0) > (Number(keeper.ln.minutes) || 0)) keeper = { p, ln };
    }
    const saves = keeper ? Number(keeper.ln.saves) || 0 : 0;

    /* ---- headline ---- */
    const margin = Math.abs(r.us - r.them);
    const vb = win
      ? (margin >= 5 ? "Roll Past" : margin === 1 ? "Edge" : "Down")
      : loss
        ? (margin >= 5 ? "Fall Heavily To" : margin === 1 ? "Come Up Short Against" : "Fall To")
        : "Draw With";
    const title = "Bears " + vb + " " + them + ", " + r.us + "-" + r.them
      + (r.so ? " in Shootout" : r.ot ? " in Overtime" : "");

    /* ---- subheader: the single most notable real thing ---- */
    let blurb;
    if (multi.length) {
      blurb = multi[0][0] + " scored " + plural(multi[0][1], "goal", "goals")
        + (saves ? " and " + surname(keeper.p.name) + " turned aside " + saves : "")
        + (home ? " at the Oakland Ice Center." : " on the road.");
    } else if (saves) {
      blurb = keeper.p.name + " made " + plural(saves, "save", "saves")
        + " as Cal " + (win ? "took" : loss ? "dropped" : "tied") + " the "
        + (home ? "home" : "road") + " game.";
    } else {
      blurb = (win ? "A win" : loss ? "A loss" : "A draw") + " "
        + (home ? "at the Oakland Ice Center." : "on the road at " + (game.venue || "the opposition rink") + ".");
    }

    /* ---- body ---- */
    const paras = [];
    paras.push("Cal " + (win ? "beat" : loss ? "lost to" : "drew with") + " " + them + " "
      + r.us + "-" + r.them + decided + " at " + (game.venue || "the rink") + ".");

    if (scorers.length) {
      paras.push(list(scorers.map(([n, c]) => (c > 1 ? n + " (" + c + ")" : n)))
        + " scored for the Bears."
        + (topAssist ? " " + topAssist[0] + " led the way with "
          + plural(topAssist[1], "assist", "assists") + "." : ""));
    } else if (r.us === 0) {
      paras.push("Cal was shut out.");
    }

    /* Period by period, using only the goals the play-by-play recorded. */
    for (const per of ["1", "2", "3", "OT"]) {
      const inPer = goals.filter((g) => g.period === per);
      if (!inPer.length) continue;
      const usIn = inPer.filter((g) => g.team === "us");
      const themIn = inPer.length - usIn.length;
      const bits = usIn.map((g) => g.scorer + " at " + g.clock
        + (g.strength && g.strength !== "EV" ? " (" + g.strength + ")" : ""));
      paras.push("In the " + ORD[per] + ", Cal "
        + (usIn.length ? "scored through " + list(bits) : "did not score")
        + (themIn ? ", while " + them + " answered " + times(themIn) : "")
        + ".");
    }

    if (saves) {
      paras.push(keeper.p.name + " finished with " + plural(saves, "save", "saves")
        + " on " + (saves + (Number(keeper.ln.ga) || 0)) + " shots.");
    }

    const id = uid();
    news.push({
      id, date: game.date, tag: "RECAP", title, blurb,
      body: paras.join("\n\n"), author: "",
      image: null, published: true, publishAt: null,
      generated: true, gameId: game.id,
    });
    game.recapId = id;
    made.push(game.date + "  " + r.us + "-" + r.them + "  " + title.slice(0, 56));
  }

  news.sort((x, y) => (y.date || "").localeCompare(x.date || ""));
  out.news = news;
  return { site: out, report: { generated: made.length, linkedOwn, skipped, list: made } };
};
