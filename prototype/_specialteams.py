# -*- coding: utf-8 -*-
"""Special teams on the Team Stats tab.

Power play and penalty kill, summed from the per-game figures the league
publishes. Both are printed as the fraction they came from as well as the
rate, because a rate over two thirds of a season is not the same thing as a
rate over all of it - and about a third of games have no opportunities
recorded at all. The card says how many games it covers rather than quietly
averaging over the ones that happen to be there.

Face-offs are not here and cannot be: the ACHA publishes the fields and
every game reads zero attempts.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------------------------- the maths
sub("""function schedStats(schedule, override) {""",
    """/**
 * Power play and penalty kill for a season, and the games they cover.
 *
 * `g.pp` is the league's own per-game count; null means the scorekeeper
 * recorded no opportunities for either side that night, which is not the
 * same as neither team having had one. Those games stay out of both halves
 * of the fraction rather than being counted as nought for nought.
 */
function specialTeams(schedule) {
  const rows = (schedule || []).filter((g) => g.result && g.pp);
  const played = (schedule || []).filter((g) => g.result).length;
  if (!rows.length) return null;
  const sum = (f) => rows.reduce((n, g) => n + f(g), 0);
  const ppg = sum((g) => g.pp.us.g), ppo = sum((g) => g.pp.us.opp);
  const ppga = sum((g) => g.pp.them.g), pko = sum((g) => g.pp.them.opp);
  return {
    games: rows.length, played,
    ppg, ppo, pp: ppo ? (100 * ppg / ppo) : null,
    ppga, pko, killed: pko - ppga, pk: pko ? (100 * (1 - ppga / pko)) : null,
  };
}

function schedStats(schedule, override) {""")

# ------------------------------------------------------------------ the card
sub("""                  <div className="reccell"><p className="reclab">Streak</p><p className="recnum">{s.streak}</p></div>
                </div>
              </>
            )}""",
    """                  <div className="reccell"><p className="reclab">Streak</p><p className="recnum">{s.streak}</p></div>
                </div>
                {(() => {
                  const st = specialTeams(season.schedule);
                  if (!st) return null;
                  return (
                    <>
                      <h2 className="statsec" style={{ marginTop: 34 }}>Special Teams</h2>
                      <div className="recgrid">
                        <div className="reccell">
                          <p className="reclab">Power play</p>
                          <p className="recnum">{st.pp == null ? "\\u2014" : st.pp.toFixed(1) + "%"}</p>
                          <p className="recsub">{st.ppg} for {st.ppo}</p>
                        </div>
                        <div className="reccell">
                          <p className="reclab">Penalty kill</p>
                          <p className="recnum">{st.pk == null ? "\\u2014" : st.pk.toFixed(1) + "%"}</p>
                          <p className="recsub">{st.killed} of {st.pko}</p>
                        </div>
                        <div className="reccell">
                          <p className="reclab">PP goals against</p>
                          <p className="recnum">{st.ppga}</p>
                        </div>
                        <div className="reccell">
                          <p className="reclab">Games covered</p>
                          <p className="recnum">{st.games}<span className="recof">/{st.played}</span></p>
                        </div>
                      </div>
                      <p className="statnote">
                        Special teams come from the ACHA's game summaries. Where a
                        scorekeeper recorded no opportunities for either side, the game is
                        left out of both figures rather than counted as none
                        {st.games < st.played
                          ? " \\u2014 " + (st.played - st.games) + " of " + st.played + " this season."
                          : "."}
                        {" "}Face-off percentage is not shown because the league publishes no
                        face-off counts.
                      </p>
                    </>
                  );
                })()}
              </>
            )}""")

# -------------------------------------------------------------------- CSS
sub(""".statnote { margin: 10px 2px 0; font-size: 12px; color: var(--muted); line-height: 1.5; }""",
    """.statnote { margin: 10px 2px 0; font-size: 12px; color: var(--muted); line-height: 1.5; }
/* The fraction a rate came from, under the rate. */
.recsub { margin: 4px 0 0; font-size: 12px; font-weight: 700; color: var(--muted);
  font-variant-numeric: tabular-nums; }
.recof { font-size: 0.62em; font-weight: 700; color: var(--muted); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('special teams added')
