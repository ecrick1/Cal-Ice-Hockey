/**
 * Apply the shot counts from the ACHA game reports.
 *
 * The site reads shots on goal from `game.live.periodShots` and
 * `game.live.shotsUs/shotsThem` - the shape a game that was scored live
 * leaves behind. A finished game is still "final" because gameState() keys
 * off `result`, not off `live`, so filling that in adds the shots without
 * making anything look in progress.
 *
 * The report prints one column per period and then the total, so the
 * columns are read positionally: 1st, 2nd, 3rd, then OT and SO where a game
 * went that far. The last number is the total and is used as a check, not
 * as a period.
 */
window.__applyShots = function applyShots(site, data) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  const COLUMNS = ["1", "2", "3", "OT", "SO"];
  const byDate = new Map((season.schedule || []).map((g) => [g.date, g]));
  const report = { games: 0, missed: [], totalsDisagree: [] };

  for (const src of data) {
    const game = byDate.get(src.date);
    if (!game) { report.missed.push(src.date); continue; }
    const us = src.shots.us || [];
    const them = src.shots.them || [];
    if (!us.length || !them.length) { report.missed.push(src.date + " (no shot line)"); continue; }

    const periodShots = {};
    const fill = (arr, side) => {
      arr.slice(0, -1).forEach((n, i) => {
        const p = COLUMNS[i];
        if (!p) return;
        periodShots[p] = periodShots[p] || { us: 0, them: 0 };
        periodShots[p][side] = n;
      });
    };
    fill(us, "us");
    fill(them, "them");

    const usTotal = us[us.length - 1];
    const themTotal = them[them.length - 1];
    const sum = (o, side) => Object.values(o).reduce((n, x) => n + x[side], 0);
    if (sum(periodShots, "us") !== usTotal || sum(periodShots, "them") !== themTotal) {
      report.totalsDisagree.push(src.date);
    }

    game.live = { ...(game.live || {}), periodShots,
      shotsUs: usTotal, shotsThem: themTotal };
    report.games++;
  }

  return { site: out, report };
};
