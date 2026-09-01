# -*- coding: utf-8 -*-
"""An odds line on head to head, from the two seasons either side of it.

Everything on that card is a fact already recorded. This is the one line
that is a claim, so it is worth writing down how it is arrived at and what
it is not.

  1. Each side's strength comes from goals rather than results - a
     Pythagorean expectation, GF squared over GF squared plus GA squared.
     Goal difference over a season is a steadier read on a team than its
     win-loss record, which turns one-goal games into whole units.

  2. That figure is pulled toward even in proportion to how little has been
     played: ten games of an even prior. Four games at 5-0 is not a .99
     team, and without this the first fortnight of a season produces
     absurdities.

  3. The two are put against each other with log5, which is the standard
     way to turn two win expectations into one matchup: it says two .700
     teams meet at even, and a .700 against a .300 is not simply .700.

  4. Home ice moves the odds by a factor of 1.22, which is the historical
     home edge in hockey - about 55-45 between teams otherwise equal. A
     neutral site gets nothing.

What it does not know: who either team played. Neither record is adjusted
for strength of schedule, and in a division where opponents range from
national qualifiers to first-year programs that is the largest source of
error by some distance. It also knows nothing about who is hurt, who is
travelling, or who is in net. The card says so.

Shown only when both sides have five games on the board. Below that the
number would be noise wearing a percentage sign.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------------------------- the maths
sub("""function seasonRecord(season) {""",
    """/**
 * Win expectation from goals for and against, pulled toward even by how
 * little has been played.
 *
 * `PRIOR` is measured in games: at ten, a team's own goals carry half the
 * weight after ten games and three quarters after thirty. It is what stops
 * a 4-0 start reading as a certainty.
 */
const ODDS_PRIOR = 10;
function pythagorean(gf, ga, gp) {
  const f = Number(gf) || 0;
  const a = Number(ga) || 0;
  const n = Number(gp) || 0;
  if (!n || f + a === 0) return null;
  const raw = (f * f) / (f * f + a * a);
  return (raw * n + 0.5 * ODDS_PRIOR) / (n + ODDS_PRIOR);
}

/**
 * Two win expectations into one matchup probability, by log5, then home ice.
 *
 * Returns the home-or-neutral-adjusted chance that the first side wins, or
 * null when either side has too little played to say anything.
 */
const HOME_EDGE = 1.22;
function matchupOdds(a, b, side) {
  const pa = pythagorean(a.gf, a.ga, a.gp);
  const pb = pythagorean(b.gf, b.ga, b.gp);
  if (pa == null || pb == null) return null;
  if ((Number(a.gp) || 0) < 5 || (Number(b.gp) || 0) < 5) return null;
  const both = pa * pb;
  const den = pa + pb - 2 * both;
  if (!den) return 0.5;
  let p = (pa - both) / den;
  if (side === "H" || side === "A") {
    const edge = side === "H" ? HOME_EDGE : 1 / HOME_EDGE;
    const odds = (p / (1 - p)) * edge;
    p = odds / (1 + odds);
  }
  return Math.min(0.97, Math.max(0.03, p));
}

function seasonRecord(season) {""")

# ----------------------------------------------------------------- the row
sub("""  const COMPARE_ROWS = opp.data ? [
    ["Record", us.w + "-" + us.l + (us.t ? "-" + us.t : ""),
      opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : ""), false],""",
    """  /* The one line on this card that is a claim rather than a record. */
  const odds = opp.data ? matchupOdds(us, opp.data, game.homeAway) : null;
  const COMPARE_ROWS = opp.data ? [
    ["Record", us.w + "-" + us.l + (us.t ? "-" + us.t : ""),
      opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : ""), false],
    ...(odds == null ? [] : [["Odds", Math.round(odds * 100) + "%",
      Math.round((1 - odds) * 100) + "%", true]]),""")

# ------------------------------------------------------------- the caveat
sub("""            {COMPARE_ROWS.map(([label, a, b, bar]) => {""",
    """            {odds != null && (
              <p className="bsm gcnone gpnote gcoddsnote">
                Odds are from goals for and against on both sides, weighted for how
                much of each season has been played and for
                {game.homeAway === "H" ? " home ice" : game.homeAway === "A" ? " playing away" : " a neutral rink"}.
                Neither record is adjusted for who they played.
              </p>
            )}
            {COMPARE_ROWS.map(([label, a, b, bar]) => {""")

# -------------------------------------------------------------------- CSS
sub(""".gcbar.norail { padding-bottom: 12px; }""",
    """.gcbar.norail { padding-bottom: 12px; }
/* Under the rows rather than over them: the numbers are the point, and this
   is the footnote that keeps them honest. */
.gcoddsnote { order: 99; margin-top: 14px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('odds row added')
