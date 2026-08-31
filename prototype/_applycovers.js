/**
 * Give every game recap a cover.
 *
 * Two sources, in order of how much they can honestly claim:
 *
 *   1. A photograph of the two teams that actually played. The library has
 *      action shots of Cal against USC and against Washington, and six of the
 *      thirty games are against those two. Where there are two shots of the
 *      same opponent they alternate, so a weekend series does not run the
 *      same picture twice.
 *   2. Otherwise the matchup card built by _covers.mjs from the two crests.
 *      An unrelated action shot would tell a reader they are looking at a
 *      game they are not; two crests say only who played, which is true.
 *
 * The club's own thirteen articles are left alone - they already carry the
 * cover the team chose for them.
 */
window.__applyCovers = function applyCovers(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  /* Opponent name -> the photographs on file of Cal playing them. */
  const PHOTOS = {
    USC: ["/photos/cal-usc.jpg", "/photos/cal-usc-2.jpg"],
    Washington: ["/photos/cal-washington.jpg", "/photos/cal-washington-2.jpg"],
  };

  const slug = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const opps = out.opponents || [];
  const byId = new Map(opps.map((o) => [o.id, o]));
  const news = out.news || [];
  const byGame = new Map();
  for (const n of news) if (n.gameId) byGame.set(n.gameId, n);

  const used = {};
  const report = { photo: 0, matchup: 0, skipped: 0, noOpponent: [] };

  for (const game of season.schedule || []) {
    const story = byGame.get(game.id);
    if (!story) { report.skipped++; continue; }

    const o = byId.get(game.opponentId);
    if (!o) { report.noOpponent.push(game.date); continue; }

    const shots = PHOTOS[o.name];
    if (shots && shots.length) {
      const i = used[o.name] || 0;
      story.image = shots[i % shots.length];
      used[o.name] = i + 1;
      report.photo++;
    } else {
      story.image = "/covers/" + slug(o.name) + ".jpg";
      report.matchup++;
    }
  }

  out.news = news;
  report.withCover = news.filter((n) => n.image).length;
  report.without = news.filter((n) => !n.image).map((n) => n.title);
  return { site: out, report };
};
