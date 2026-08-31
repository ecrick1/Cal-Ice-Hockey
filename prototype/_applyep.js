/**
 * Rosters and season stats for the years before the ACHA's own feed starts.
 *
 * REAL DATA from EliteProspects, which carries Cal back to 2010-11 where the
 * league's system begins at 2021-22. What it gives is season totals per
 * player - games, goals, assists, penalty minutes, and a goaltender's line -
 * not individual games, because EliteProspects does not publish those. That
 * is exactly what boxScoreTotals() falls back to for a season with no game
 * log, so these years read correctly without one.
 *
 * The seasons here are everything EliteProspects publishes from 2010 on.
 * Three of them - 2011-12, 2015-16, 2016-17 - are not linked from the team
 * page's own season list and were found through a player's career table;
 * 2012-13, 2013-14 and 2014-15 genuinely are not there, and neither is
 * 2020-21, where the league lists Cal as a member with no roster and no games.
 *
 * This fills gaps, it does not overwrite. 2019-20 and 2018-19 were already
 * complete - and carry hometowns EliteProspects does not publish - so nothing
 * of theirs is touched beyond fields that are genuinely empty. A season with
 * a game log is skipped outright.
 */
window.__applyEp = function applyEp(site, data, opts) {
  const dry = !(opts && opts.write);
  const out = JSON.parse(JSON.stringify(site));
  const uid = () => "e" + Math.random().toString(36).slice(2, 9);
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
  const num = (v) => { const n = Number(String(v).replace(/[^\d.]/g, "")); return Number.isFinite(n) ? n : 0; };
  const blank = (v) => v === undefined || v === null || String(v).trim() === "";

  /* The site writes heights with prime marks and weights with a unit. */
  const height = (h) => (blank(h) ? "" : String(h).replace(/'/, "′").replace(/"/, "″"));
  const weight = (w) => (blank(w) ? "" : num(w) ? num(w) + " lbs" : "");

  /* "2019-2020~ACHA II~24~14~10~0~~0~98~64" -> "2019-20" */
  const records = {};
  for (const row of data.teamHistory || []) {
    const c = row.split("~");
    if (blank(c[3])) continue;
    records[c[0].slice(0, 5) + c[0].slice(-2)] = {
      w: num(c[3]),
      /* An overtime loss is still a loss here, which is how the site's own
         computed record counts one. */
      l: num(c[4]) + num(c[7]),
      t: num(c[5]),
      gf: num(c[8]), ga: num(c[9]),
    };
  }

  const log = [];
  const report = { seasons: [], skipped: [], checks: [], log };

  for (const s of data.seasons || []) {
    const key = s.season;
    let season = out.seasons[key];
    const created = !season;
    if (season && (season.schedule || []).length) {
      report.skipped.push(key + " — has a game log, left alone");
      continue;
    }
    if (created) season = { label: key, roster: [], schedule: [], coaches: [], record: null };

    const bio = new Map();
    for (const b of s.B || []) {
      const [name, number, pos, ht, wt, shoots, home] = b.split("~");
      bio.set(norm(name), { number, pos, ht, wt, shoots, home });
    }

    const roster = [...(season.roster || [])];
    const find = (name) => roster.find((p) => norm(p.name) === norm(name));
    const stat = { added: 0, filled: 0, kept: 0 };

    /* Only fill a field the site does not already have; never replace one. */
    const fill = (p, patch, who) => {
      for (const [k, v] of Object.entries(patch)) {
        if (blank(v) || !blank(p[k])) continue;
        p[k] = v;
        log.push(key + "  " + who + "  " + k + " = " + v);
      }
    };
    const hasStats = (p) => Object.values(p.stats || {}).some((v) => Number(v));

    const upsert = (name, fields, stats) => {
      let p = find(name);
      if (!p) {
        p = { id: uid(), name, number: "", position: "", spot: "", shoots: "",
              height: "", weight: "", hometown: "", year: "", stats: {},
              source: "eliteprospects" };
        roster.push(p);
        stat.added++;
        log.push(key + "  + " + name);
      }
      fill(p, fields, name);
      if (hasStats(p)) { stat.kept++; return p; }
      p.stats = stats;
      stat.filled++;
      return p;
    };

    for (const row of s.S || []) {
      const [name, pos, gp, g, a, pim] = row.split("~");
      const b = bio.get(norm(name)) || {};
      upsert(name, {
        number: b.number,
        position: /^G$/i.test(pos) ? "G" : /^D/i.test(pos) ? "D" : "F",
        /* The stats table names a forward's spot where the roster page only
           says "F". Worth keeping - the site shows it and has it nowhere. */
        spot: /^(LW|C|RW)$/i.test(pos) ? pos.toUpperCase() : "",
        height: height(b.ht), weight: weight(b.wt), shoots: b.shoots,
        hometown: b.home,
      }, { gp: num(gp), g: num(g), a: num(a), pim: num(pim) });
    }

    for (const row of s.G || []) {
      const [name, gp, gaa, svpct, so, toi, svs] = row.split("~");
      const b = bio.get(norm(name)) || {};
      const [m, sec] = String(toi || "").split(":").map(Number);
      const minutes = Number.isFinite(m) ? m + (sec || 0) / 60 : 0;

      /* Goals against is not printed, but goals-against average over the
         minutes played is exactly that. Where the source is consistent it
         comes back whole, and the save percentage - which is published and
         plays no part in the arithmetic - then checks it independently.
         Anything that does not come out whole is left off rather than
         rounded into place. */
      const raw = (num(gaa) * minutes) / 60;
      const ga = minutes > 0 && Math.abs(raw - Math.round(raw)) < 0.15 ? Math.round(raw) : null;
      const saves = num(svs);
      if (ga != null) {
        const derived = saves / (saves + ga);
        const ok = Math.abs(derived - num(svpct)) < 0.001;
        report.checks.push(key + " " + name + ": SV% " + derived.toFixed(3).replace(/^0/, "")
          + " vs published " + svpct + (ok ? "  ✓" : "  DIFFERS"));
      }

      upsert(name, {
        number: b.number, position: "G",
        height: height(b.ht), weight: weight(b.wt), shoots: b.shoots,
        hometown: b.home,
      }, ga != null
        ? { gp: num(gp), g: 0, a: 0, pim: 0, saves, ga, so: num(so), minutes }
        /* No ice time and no save count published, so there is nothing to
           count. The published rates are kept as rates - a zero here would
           read as a shutout season. */
        : { gp: num(gp), g: 0, a: 0, pim: 0, so: num(so), gaa: num(gaa), svpct: num(svpct) });
    }

    const rec = records[key] || null;
    if (rec && season.record) {
      const p = season.record;
      const same = num(p.w) === rec.w && num(p.l) === rec.l && num(p.gf) === rec.gf && num(p.ga) === rec.ga;
      report.checks.push(key + " record: site " + p.w + "-" + p.l + " " + p.gf + ":" + p.ga
        + " vs EP " + rec.w + "-" + rec.l + " " + rec.gf + ":" + rec.ga + (same ? "  ✓" : "  DIFFERS"));
    }

    const goals = roster.reduce((n, p) => n + (Number(p.stats && p.stats.g) || 0), 0);
    const against = roster.reduce((n, p) => n + (Number(p.stats && p.stats.ga) || 0), 0);
    const target = rec || (season.record ? { gf: num(season.record.gf), ga: num(season.record.ga) } : null);
    if (target) {
      report.checks.push(key + " skater goals " + goals + " vs team GF " + target.gf
        + (goals === target.gf ? "  ✓" : "  differs by " + (target.gf - goals)));
      report.checks.push(key + " goalie GA " + against + " vs team GA " + target.ga
        + (against === target.ga ? "  ✓" : "  differs by " + (target.ga - against)));
    }

    if (!dry) {
      season.roster = roster;
      if (!season.record && rec) season.record = rec;
      out.seasons[key] = season;
    }

    report.seasons.push({
      season: key, created, players: roster.length,
      added: stat.added, statsWritten: stat.filled, statsKept: stat.kept,
      record: season.record ? season.record.w + "-" + season.record.l : (rec ? rec.w + "-" + rec.l : "none"),
      goals,
    });
  }

  return { site: out, report };
};
