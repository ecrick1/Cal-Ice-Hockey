# -*- coding: utf-8 -*-
"""Use stored opponent season stats where the club has them.

The ACHA feed publishes an opponent's schedule and roster but not their
players' totals. EliteProspects publishes the totals - and blocks anything
that is not a browser, so it cannot be fetched by the site. The gap is filled
by pasting their table into the console instead, which is a person reading a
page rather than a robot working around a block.

Stored under the opponent, keyed by season, so it survives and can be
corrected. Where it is absent the page still says "Not published" rather than
guessing.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# ----------------------------------------------------- read the stored set
sub("""  const theirRoster = useOpponentRoster(opponentRec, form.season.achaSeasonId);""",
    """  const theirRoster = useOpponentRoster(opponentRec, form.season.achaSeasonId);
  /* Their season, if somebody has put it in. */
  const theirStats = ((opponentRec || {}).seasonStats || {})[form.name] || null;
  const theirBest = (key) => {
    const pool = (theirStats ? theirStats.skaters : []).filter((x) => (key(x) || 0) > 0);
    if (!pool.length) return null;
    return [...pool].sort((a, b) => key(b) - key(a) || (b.g || 0) - (a.g || 0))[0];
  };
  const THEIRS = {
    Points: theirBest((x) => (x.g || 0) + (x.a || 0)),
    Goals: theirBest((x) => x.g || 0),
    Assists: theirBest((x) => x.a || 0),
  };
  const theirValue = { Points: (x) => (x.g || 0) + (x.a || 0), Goals: (x) => x.g || 0, Assists: (x) => x.a || 0 };""")

# --------------------------------------------------- their side of a row
sub("""              <span className="h2hnum empty">—</span>
              <span className="h2hplayer empty">
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={44} />}
                <span className="h2hnames">
                  <span className="h2hname">Not published</span>
                  <span className="h2hpos">{themName}</span>
                </span>
              </span>""",
    """              <span className={"h2hnum" + (THEIRS[label] ? "" : " empty")}>
                {THEIRS[label] ? theirValue[label](THEIRS[label]) : "—"}
              </span>
              <span className="h2hplayer empty">
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={44} />}
                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? " known" : "")}>
                    {THEIRS[label] ? THEIRS[label].name : "Not published"}
                  </span>
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? (THEIRS[label].pos || "") + " · " + (THEIRS[label].gp || 0) + " GP"
                      : themName}
                  </span>
                </span>
              </span>""")

sub("""        <p className="bsm gcnone gpnote">
          The league publishes their schedule and roster but not their players' season
          totals, so only Cal's leaders can be shown.
        </p>""",
    """        {!theirStats && (
          <p className="bsm gcnone gpnote">
            The league publishes their schedule and roster but not their players' season
            totals. Paste them in under Opponents and they appear here.
          </p>
        )}""")

# ------------------------------------------------------ their goaltenders
sub("""          {theirGoalies.length ? theirGoalies.map((p) => (
            <div className="gtcard" key={p.id}>
              <span className="gtname">{p.name}<span className="gtnum">#{p.number || "\\u2014"}</span></span>
              <span className="gtline">
                <span><strong>—</strong>GP</span>
                <span><strong>—</strong>GAA</span>
                <span><strong>—</strong>SV%</span>
                <span><strong>—</strong>SO</span>
              </span>
            </div>
          )) : <p className="bsm gcnone">{opp.loading ? "Loading\\u2026" : "No roster published."}</p>}""",
    """          {(theirStats ? theirStats.goalies.slice(0, 2) : theirGoalies).map((p, i) => (
            <div className="gtcard" key={p.id || p.name || i}>
              <span className="gtname">{p.name}
                <span className="gtnum">
                  {p.number ? "#" + p.number
                    : (theirGoalies.find((g) => g.name === p.name) || {}).number
                      ? "#" + theirGoalies.find((g) => g.name === p.name).number : ""}
                </span>
              </span>
              <span className="gtline">
                <span><strong>{p.gp == null ? "—" : p.gp}</strong>GP</span>
                <span><strong>{p.gaa == null ? "—" : p.gaa}</strong>GAA</span>
                <span><strong>{p.svpct == null ? "—" : String(p.svpct).replace(/^0/, "")}</strong>SV%</span>
                <span><strong>{p.so == null ? "—" : p.so}</strong>SO</span>
              </span>
            </div>
          ))}
          {!theirStats && !theirGoalies.length && (
            <p className="bsm gcnone">{opp.loading ? "Loading\\u2026" : "No roster published."}</p>
          )}""")

# ------------------------------------ their roster table gets the numbers
sub("""    : (theirRoster || []).map((p) => ({ p, t: null, mine: false }));""",
    """    : (theirRoster || []).map((p) => {
        /* Matched on name, which is all the two sources share. */
        const st = theirStats && theirStats.skaters.find((x) => x.name === p.name);
        return { p, t: st ? { gp: st.gp, g: st.g, a: st.a, pim: st.pim } : null, mine: false };
      });""")

sub("""      {rosterSide === "them" && (
        <p className="bsm gcnone gpnote">
          Their roster is live from the league; it carries no season totals.
        </p>
      )}""",
    """      {rosterSide === "them" && (
        <p className="bsm gcnone gpnote">
          {theirStats
            ? "Roster live from the league; totals from " + (theirStats.source || "a stored season")
              + ", so a player who dressed without appearing there shows dashes."
            : "Their roster is live from the league; it carries no season totals."}
        </p>
      )}""")

sub(""".h2hplayer.empty .h2hname { color: var(--muted); font-weight: 700; }""",
    """.h2hplayer.empty .h2hname { color: var(--muted); font-weight: 700; }
/* Their leader, once somebody has put their season in. */
.h2hplayer.empty .h2hname.known { color: var(--ink); font-weight: 800; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('wired')
