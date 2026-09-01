# -*- coding: utf-8 -*-
"""The box score's tables line up, and a goaltender gets his decision.

Forwards, Defense and Goaltending are three separate tables stacked down one
page, and each was sized independently: twelve columns in the first, eleven
in the second because defencemen were not given a position column, six in
the third. Auto layout then gave each one's name column whatever its own
longest name needed, so the names stepped left and right down the page and
nothing read as one sheet.

Two fixes, because the widths alone would not have done it. The identifying
columns - number, player, position - are pinned to the same widths in all
three tables, and defencemen get the position column the forwards already
had, so the same three columns start in the same three places everywhere.
The stat columns after them are each table's own business and always were.

And the goaltender's decision. The data is there - a finished game and a
scoreline is all a decision is - so the column is added, but only filled
when it can be filled honestly: when one goaltender played the whole game.
Two keepers in one game means the decision belongs to whoever was in net for
the winning goal, and for an imported game there is nothing that says which.
A dash is the truthful answer there, and the season page's W-L-T, which has
always credited both, is left alone rather than quietly changed underneath a
number somebody may have quoted.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================= defence gets a position column
sub("""                <BoxTable title="Defense" rows={skaters
                  .filter((e) => e.p.position === "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }, true))}
                  onPlayer={onPlayer} />""",
    """                <BoxTable title="Defense" showSpot rows={skaters
                  .filter((e) => e.p.position === "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, spot: "D", l: e.l }, true))}
                  onPlayer={onPlayer} />""")

sub("""                <BoxTable title="Skaters" rows={skaters
                  .filter((e) => e.p.position !== "F" && e.p.position !== "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }, true))}
                  onPlayer={onPlayer} />""",
    """                <BoxTable title="Skaters" showSpot rows={skaters
                  .filter((e) => e.p.position !== "F" && e.p.position !== "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }, true))}
                  onPlayer={onPlayer} />""")

sub("""                <BoxTable title="Defense" rows={oppSkaters
                  .filter((x) => oppPos(x) === "D")
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, l: x }, false))} />
                <BoxTable title="Skaters" rows={oppSkaters
                  .filter((x) => !oppPos(x))
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, l: x }, false))} />""",
    """                <BoxTable title="Defense" showSpot rows={oppSkaters
                  .filter((x) => oppPos(x) === "D")
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, spot: "D", l: x }, false))} />
                <BoxTable title="Skaters" showSpot rows={oppSkaters
                  .filter((x) => !oppPos(x))
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, l: x }, false))} />""")

# ================================================== the goaltender's decision
sub("""function GoalieTable({ rows, onPlayer }) {
  if (!rows.length) return null;
  return (
    <section className="gcpad gcboxsec">
      <h2 className="statsec">Goaltending</h2>
      <div className="twrap">
        <table className="stats gcbt">
          <thead>
            <tr><th>#</th><th>Goaltender</th><th>SA</th><th>SV</th><th>GA</th><th>SV%</th></tr>
          </thead>""",
    """/* Which of W, L or T a goaltender takes for the game.
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
}

function GoalieTable({ rows, onPlayer, result, mine }) {
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
          </thead>""")

sub("""                  <td className="gcbtname">
                    {onPlayer
                      ? <button className="pboxname" onClick={() => onPlayer(r.id)}>{r.name}</button>
                      : r.name}
                  </td>
                  <td>{sa}</td>""",
    """                  <td className="gcbtname">
                    {onPlayer
                      ? <button className="pboxname" onClick={() => onPlayer(r.id)}>{r.name}</button>
                      : r.name}
                  </td>
                  <td className="gcbtdec">{dec && dec.id === r.id ? dec.mark : "\\u2014"}</td>
                  <td>{sa}</td>""")

sub("""                <GoalieTable rows={goalies.map((e) => ({
                  id: e.p.id, number: e.p.number, name: e.p.name, l: e.l,
                }))} onPlayer={onPlayer} />""",
    """                <GoalieTable rows={goalies.map((e) => ({
                  id: e.p.id, number: e.p.number, name: e.p.name, l: e.l,
                }))} onPlayer={onPlayer} result={game.result} mine />""")

# ------------------------------------------------------------------- CSS
sub(""".gcbt { width: 100%; }""",
    """/* Three tables stacked down one page - forwards, defence, goaltenders - were
   each sized to their own contents, so the name column started in a different
   place in each and the sheet read as three. The identifying columns are
   pinned to the same widths in all of them; the stat columns after are each
   table's own and always were. */
.gcbt { width: 100%; }
.gcbt th:nth-child(1), .gcbt td:nth-child(1) { width: 46px; }
.gcbt th:nth-child(2), .gcbt td:nth-child(2) { width: 210px; }
.gcbt th:nth-child(3), .gcbt td:nth-child(3) { width: 52px; }
.gcbtdec { font-weight: 800; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the tables line up; the keeper gets his decision')
