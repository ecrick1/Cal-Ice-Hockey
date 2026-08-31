# -*- coding: utf-8 -*-
"""Prefer the league's own aggregate; fall back to a pasted season."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


sub("""/** Their roster, live from the league. Names, numbers and positions - no stats. */""",
    """/**
 * Their season, added up from the league's own game summaries.
 *
 * Every summary carries both benches, so walking a team's finished games
 * gives their totals exactly - no pasting, and it refreshes itself. The
 * server does the walking and holds the answer, because it is one request per
 * game.
 */
function useOpponentSeasonStats(opponent, achaSeasonId) {
  const [state, setState] = useState({ loading: false, data: null });
  const teamId = opponent && opponent.achaTeamId;
  useEffect(() => {
    if (!teamId || !achaSeasonId) { setState({ loading: false, data: null }); return; }
    let alive = true;
    setState({ loading: true, data: null });
    fetch("/acha/team-season?season_id=" + achaSeasonId + "&team=" + teamId)
      .then((r) => r.json())
      .then((j) => {
        if (!alive) return;
        setState({ loading: false, data: (j && j.skaters && j.skaters.length) ? j : null });
      })
      .catch(() => { if (alive) setState({ loading: false, data: null }); });
    return () => { alive = false; };
  }, [teamId, achaSeasonId]);
  return state;
}

/** Their roster, live from the league. Names, numbers and positions - no stats. */""")

sub("""  /* Their season, if somebody has put it in. */
  const theirStats = ((opponentRec || {}).seasonStats || {})[form.name] || null;""",
    """  /* The league's own aggregate first; a pasted season stands in when the feed
     has nothing - an opponent outside the ACHA, or a year before its records
     begin. */
  const live = useOpponentSeasonStats(opponentRec, form.season.achaSeasonId);
  const pasted = ((opponentRec || {}).seasonStats || {})[form.name] || null;
  const theirStats = live.data || pasted;""")

# The goalie block reads gaa/svpct as strings from a paste; the aggregate has
# counts. Normalise at the point of use.
sub("""          {(theirStats ? theirStats.goalies.slice(0, 2) : theirGoalies).map((p, i) => (""",
    """          {(theirStats ? theirStats.goalies.slice(0, 2).map((p) => {
            /* A pasted row already carries the rates; an aggregated one
               carries saves and goals against, so the rates come from those. */
            if (p.gaa != null || p.svpct != null) return p;
            const faced = (p.saves || 0) + (p.ga || 0);
            return { ...p,
              gaa: p.gp ? ((p.ga || 0) / p.gp).toFixed(2) : null,
              svpct: faced ? (p.saves / faced).toFixed(3).replace(/^0/, "") : null };
          }) : theirGoalies).map((p, i) => (""")

sub("""            ? "Roster live from the league; totals from " + (theirStats.source || "a stored season")
              + ", so a player who dressed without appearing there shows dashes."
            : "Their roster is live from the league; it carries no season totals."}""",
    """            ? "Roster and totals live from the league" + (theirStats.games ? " \\u2014 " + theirStats.games + " games" : "")
              + ". A player with no line in any box score shows dashes."
            : "Their roster is live from the league; it carries no season totals."}""")

sub("""        {!theirStats && (
          <p className="bsm gcnone gpnote">
            The league publishes their schedule and roster but not their players' season
            totals. Paste them in under Opponents and they appear here.
          </p>
        )}""",
    """        {!theirStats && (
          <p className="bsm gcnone gpnote">
            {live.loading
              ? "Reading their season from the league\\u2026"
              : "The league has no box scores for them this season. Paste their totals under Opponents and they appear here."}
          </p>
        )}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('wired to live aggregate')
