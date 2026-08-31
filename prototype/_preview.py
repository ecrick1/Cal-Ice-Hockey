"""A game preview with something in it before a season has been played.

The first game of a year has no form to show, so the preview falls back to the
season before and says so. Everything here is computed from games that were
actually played - a figure the play-by-play cannot support prints as a dash
rather than a zero.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------------------- the helpers
sub("""function GamePreview({ site, game, season, onPlayer, story, openPost }) {""",
    """/**
 * Season totals for the team, off the play-by-play.
 *
 * Power play and penalty kill both come from penalties: the other side's trips
 * to the box are your chances, and yours are theirs. Face-offs are only there
 * if somebody logged them during live scoring, so that one is usually absent -
 * and absent prints as a dash, not as nought per cent.
 */
function seasonTeamStats(site, season) {
  const played = (season.schedule || []).filter((g) => g.result && countsToward(g));
  let ppGoalsUs = 0, ppGoalsThem = 0, pensUs = 0, pensThem = 0;
  let drawsUs = 0, drawsThem = 0, gf = 0, ga = 0;

  for (const g of played) {
    gf += Number(g.result.us) || 0;
    ga += Number(g.result.them) || 0;
    for (const x of g.plays || []) {
      if (x.kind === "goal" && x.strength === "PP" && x.period !== "SO") {
        if (x.team === "us") ppGoalsUs++; else ppGoalsThem++;
      } else if (x.kind === "penalty") {
        if (x.team === "us") pensUs++; else pensThem++;
      } else if (x.kind === "faceoff") {
        if (x.team === "us") drawsUs++; else drawsThem++;
      }
    }
  }

  const pct = (n, d) => (d ? Math.round((n / d) * 100) : null);
  const per = (n, d) => (d ? (n / d).toFixed(2) : null);
  const draws = drawsUs + drawsThem;
  return {
    gp: played.length,
    /* Chances are the other team's penalties. */
    pp: pct(ppGoalsUs, pensThem),
    /* Kills are your own penalties that did not end in a goal against. */
    pk: pensUs ? Math.round(((pensUs - ppGoalsThem) / pensUs) * 100) : null,
    fo: draws ? pct(drawsUs, draws) : null,
    gfpg: per(gf, played.length),
    gapg: per(ga, played.length),
  };
}

/** The season a preview should describe: this one once it has games, else the last one that did. */
function formSeason(site, seasonName) {
  const own = site.seasons[seasonName];
  if ((own.schedule || []).some((g) => g.result)) return { name: seasonName, season: own, prior: false };
  const earlier = Object.keys(site.seasons)
    .filter((n) => n < seasonName)
    .sort()
    .reverse()
    .find((n) => (site.seasons[n].schedule || []).some((g) => g.result)
      || (site.seasons[n].roster || []).length);
  return earlier
    ? { name: earlier, season: site.seasons[earlier], prior: true }
    : { name: seasonName, season: own, prior: false };
}

function GamePreview({ site, game, season, seasonName, onPlayer, story, openPost }) {""")

io.open(p, 'w', encoding='utf-8').write(s)
print('helpers done')
