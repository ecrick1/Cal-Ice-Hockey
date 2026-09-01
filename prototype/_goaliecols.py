# -*- coding: utf-8 -*-
"""A goaltender's line for the game: how the goals went in, and how long he played.

The decision comes off. A box score is one game, and W-L-T is a season
answer to a season question - it belongs on the stats page, where it already
is, and put beside a single game it says nothing the scoreline above it has
not already said.

What goes in its place is the line a goaltender is actually read on. Shots
against, saves, goals against, then the three ways a goal goes in - even
strength, on the power play, short-handed - then save percentage and time on
ice. The split is the part that says something the total cannot: three
goals against is a different night when two of them came four-on-five.

The split is counted off the play-by-play, and only when it can be. Each
goal the other team scored carries the strength it was scored at, and who
was in net is read from the goaltender changes: the keeper who started, then
whoever came on, matched against the clock each goal went in on. Where two
keepers split a game and nothing recorded the change, there is no way to say
which of them a goal belongs to, and a dash says so.

It is also checked against the total before being shown. If the goals in the
play-by-play do not add up to the goals against on the lines, the split
would be a confident answer built on an incomplete log, so it is not given.
Seven of this season's thirty games fail that check and will show dashes;
the other twenty-three split cleanly.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ==================================================== when a play happened
sub("""/* Which of W, L or T a goaltender takes for the game.
 *
 * The decision belongs to whoever was in net for the winning goal, and where
 * two keepers played there is nothing on an imported sheet that says which.
 * So it is only given when one of them played the whole game, and a dash
 * otherwise: a decision credited to both would be one more than the team
 * actually earned. */
function goalieDecision(rows, result, mine) {
  if (!result) return null;
  const played = rows.filter((r) => Number(r.l.saves) || Number(r.l.ga) || Number(r.l.minutes));
  if (played.length !== 1) return null;
  const us = Number(result.us) || 0, them = Number(result.them) || 0;
  const ours = mine ? us : them, theirs = mine ? them : us;
  return { id: played[0].id, mark: ours > theirs ? "W" : ours < theirs ? "L" : "T" };
}""",
    """/* Seconds since the opening face-off, read off a play's period and clock, so
   two plays from different periods can be put in order against each other. */
function playElapsed(x) {
  const order = ["1", "2", "3", "OT", "SO"];
  const i = Math.max(0, order.indexOf(String((x && x.period) || "1")));
  const before = order.slice(0, i).reduce((n, k) => n + periodSecs(k), 0);
  const bits = String((x && x.clock) || "0:00").split(":");
  const remain = (Number(bits[0]) || 0) * 60 + (Number(bits[1]) || 0);
  return before + Math.max(0, periodSecs(order[i]) - remain);
}

/**
 * How the goals against each goaltender went in: even strength, power play,
 * short-handed.
 *
 * Counted off the play-by-play. Every goal the other team scored carries the
 * strength it was scored at, and who was in net comes from the goaltender
 * changes - the keeper who started, then whoever came on, matched against the
 * clock each goal went in on.
 *
 * Returns null when it cannot be said honestly: two keepers with nothing
 * recording the change between them, or a play-by-play whose goals do not add
 * up to the goals against on the lines. A split that does not reconcile with
 * the total beside it is a confident answer built on an incomplete log.
 *
 * An empty-net goal counts with the even-strength ones rather than vanishing,
 * so the three columns always add up to the GA column next to them.
 */
function goalieGaSplit(rows, plays, mine) {
  const against = (plays || []).filter((x) => x.kind === "goal"
    && x.team === (mine ? "them" : "us") && x.period !== "SO");
  const total = rows.reduce((n, r) => n + (Number(r.l.ga) || 0), 0);
  if (against.length !== total) return null;

  const played = rows.filter((r) => Number(r.l.saves) || Number(r.l.ga) || Number(r.l.minutes));
  const changes = (plays || [])
    .filter((x) => x.kind === "goalie" && x.team === (mine ? "us" : "them"))
    .sort((a, b) => playElapsed(a) - playElapsed(b));

  let whoAt = null;
  if (changes.length) {
    const opening = changes[0].out || (played[0] || {}).name || "";
    whoAt = (t) => {
      let cur = opening;
      for (const c of changes) {
        if (playElapsed(c) <= t) cur = c.player || ""; else break;
      }
      return cur;
    };
  } else if (played.length === 1) {
    whoAt = () => played[0].name;
  } else if (!against.length) {
    /* Nobody was beaten, so there is nothing to attribute and every keeper
       honestly has none. */
    whoAt = () => null;
  } else return null;

  const out = {};
  for (const r of rows) out[r.id] = { ev: 0, pp: 0, sh: 0 };
  for (const g of against) {
    const nm = String(whoAt(playElapsed(g)) || "").toLowerCase();
    const row = rows.find((r) => String(r.name || "").toLowerCase() === nm);
    if (!row) return null;
    out[row.id][g.strength === "PP" ? "pp" : g.strength === "SH" ? "sh" : "ev"]++;
  }
  return out;
}

/* Minutes as a scoreboard writes them. The field is a number because it is
   typed as one; 40.5 is forty minutes and thirty seconds. */
function fmtTOI(v) {
  const m = Number(v);
  if (!m) return "\\u2014";
  const whole = Math.floor(m);
  const secs = Math.round((m - whole) * 60);
  return whole + ":" + String(secs).padStart(2, "0");
}""")

# ============================================================== the table
sub("""function GoalieTable({ rows, onPlayer, result, mine }) {
  if (!rows.length) return null;
  const dec = goalieDecision(rows, result, mine);
  return (
    <section className="gcpad gcboxsec">
      <h2 className="statsec">Goaltending</h2>
      <div className="twrap">
        <table className="stats gcbt">
          <thead>
            <tr><th>#</th><th>Goaltender</th>
              <th title="Decision — win, loss or tie">DEC</th>
              <th>SA</th><th>SV</th><th>GA</th><th>SV%</th></tr>
          </thead>""",
    """function GoalieTable({ rows, onPlayer, plays, mine }) {
  if (!rows.length) return null;
  const split = goalieGaSplit(rows, plays, mine);
  return (
    <section className="gcpad gcboxsec">
      <h2 className="statsec">Goaltending</h2>
      <div className="twrap">
        <table className="stats gcbt">
          <thead>
            <tr><th>#</th><th>Goaltender</th>
              <th title="Shots against">SA</th>
              <th title="Saves">SV</th>
              <th title="Goals against">GA</th>
              <th title="Goals against at even strength">EV GA</th>
              <th title="Goals against on the power play">PP GA</th>
              <th title="Goals against while short-handed">SH GA</th>
              <th title="Save percentage">SV%</th>
              <th title="Time on ice">TOI</th></tr>
          </thead>""")

sub("""                  <td className="gcbtdec">{dec && dec.id === r.id ? dec.mark : "\\u2014"}</td>
                  <td>{sa}</td>
                  <td>{sv}</td>
                  <td>{ga}</td>
                  <td className="gcbtpts">{sa ? (sv / sa).toFixed(3).replace(/^0/, "") : "—"}</td>""",
    """                  <td>{sa}</td>
                  <td>{sv}</td>
                  <td>{ga}</td>
                  <td>{split ? split[r.id].ev : "\\u2014"}</td>
                  <td>{split ? split[r.id].pp : "\\u2014"}</td>
                  <td>{split ? split[r.id].sh : "\\u2014"}</td>
                  <td className="gcbtpts">{sa ? (sv / sa).toFixed(3).replace(/^0/, "") : "—"}</td>
                  <td>{fmtTOI(r.l.minutes)}</td>""")

sub("""                }))} onPlayer={onPlayer} result={game.result} mine />""",
    """                }))} onPlayer={onPlayer} plays={plays} mine />""")

sub("""                }))} result={game.result} />""",
    """                }))} plays={plays} />""")

sub(""".gcbtdec { font-weight: 800; }""", "")

io.open(p, 'w', encoding='utf-8').write(s)
print('the keeper line: how the goals went in, and how long he played')
