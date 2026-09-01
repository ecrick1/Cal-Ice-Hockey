# -*- coding: utf-8 -*-
"""Shots on goal, per player, in the public box score.

The column existed in the console and nowhere the public could see it, and
for a game scored live it was empty anyway: every shot records who took it,
and nothing ever put that on the shooter's line.

So the line is counted off the play-by-play rather than written to twice.
Saves already work this way - they fall out of shots faced and goals against
instead of being a third number that has to agree with the other two - and
shots are the same kind of fact. Correct the shooter on a play and the box
score follows on its own; delete the play and it follows again. There is no
reversal to get wrong, which is the half of this that usually rots.

A typed line still wins where there is one. Games imported from a league
sheet have shots and no play-by-play to count, so the number entered is the
number shown; live games have the plays and no typed line. Each takes
whichever it has, the way the power-play counts already do.

A goal is a shot that went in, so it counts on the scorer's line as both.
It is not a save - the goaltender's line takes it as a shot faced and a goal
against, which is what it already did.

Where shots were counted for the team but never attributed to anyone - the
plain +1 with nobody named - the total under the table says so rather than
letting the column quietly come up short of the team's number.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------ count them off the plays
sub("""  const penNumber = (x, mine) => (mine
    ? numberOf(x.playerId, x.player) : oppNumberOf(x.player, x.playerId));""",
    """  const penNumber = (x, mine) => (mine
    ? numberOf(x.playerId, x.player) : oppNumberOf(x.player, x.playerId));

  /* Shots on goal per player, counted off the play-by-play.
   *
   * The same reasoning as the goaltender's line: this is not a fact to be
   * entered beside the plays, it is a fact the plays already hold. Counting
   * it means correcting a shooter fixes the box score too, and no reversal
   * has to be remembered when a play is deleted.
   *
   * A goal is a shot that went in and counts here. It is not a save, which
   * is why the goaltender's line takes it as a shot faced and a goal
   * against and never as a stop.
   *
   * Ours key on the roster id and theirs on the name, because that is what
   * each side records. */
  const shotTally = (() => {
    const us = {}, them = {};
    const add = (m, k) => { if (k) m[k] = (m[k] || 0) + 1; };
    const nm = (v) => String(v || "").toLowerCase();
    for (const x of plays) {
      const mine = x.team === "us";
      if (x.kind === "shot") add(mine ? us : them, mine ? x.shooterId : nm(x.shooter));
      else if (x.kind === "goal") add(mine ? us : them, mine ? x.scorerId : nm(x.scorer));
    }
    return { us, them };
  })();

  /* A typed line wins: a game off a league sheet has shots and no plays to
     count, and a game scored live has the plays and no typed line. */
  const withShots = (row, mine) => {
    const l = row.l || {};
    if (l.shots !== undefined && l.shots !== null && l.shots !== "") return row;
    const tally = mine ? shotTally.us : shotTally.them;
    const n = tally[mine ? row.id : String(row.name || "").toLowerCase()];
    return n ? { ...row, l: { ...l, shots: n } } : row;
  };

  /* Shots the scorekeeper counted for the team without naming anyone. The
     column would otherwise come up short of the team's own total with
     nothing to say why. */
  const unnamedShots = (mine) => {
    const total = mine ? totalShots.us : totalShots.them;
    const named = Object.values(mine ? shotTally.us : shotTally.them)
      .reduce((a, b) => a + b, 0);
    return Math.max(0, (Number(total) || 0) - named);
  };""")

# ------------------------------------------------------ the column itself
sub("""              <th>#</th><th>Player</th>
              {showSpot && <th>Pos</th>}
              <th>G</th><th>A</th><th>P</th><th>PIM</th><th>PPG</th><th>SHG</th>""",
    """              <th>#</th><th>Player</th>
              {showSpot && <th>Pos</th>}
              <th>G</th><th>A</th><th>P</th>
              <th title="Shots on goal">S</th>
              <th>PIM</th><th>PPG</th><th>SHG</th>""")

sub("""                <td className="gcbtpts">{pts(r.l)}</td>
                <td>{r.l.pim || 0}</td>""",
    """                <td className="gcbtpts">{pts(r.l)}</td>
                <td>{r.l.shots || 0}</td>
                <td>{r.l.pim || 0}</td>""")

# ---------------------------------------------------------- feed the rows
sub("""                <BoxTable title="Forwards" showSpot rows={skaters
                  .filter((e) => e.p.position === "F")
                  .map((e) => ({ id: e.p.id, number: e.p.number, name: e.p.name, spot: e.p.spot, l: e.l }))}
                  onPlayer={onPlayer} />
                <BoxTable title="Defense" rows={skaters
                  .filter((e) => e.p.position === "D")
                  .map((e) => ({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }))}
                  onPlayer={onPlayer} />
                {/* Anything with an unrecognised position still has to appear. */}
                <BoxTable title="Skaters" rows={skaters
                  .filter((e) => e.p.position !== "F" && e.p.position !== "D")
                  .map((e) => ({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }))}
                  onPlayer={onPlayer} />
                <GoalieTable rows={goalies.map((e) => ({
                  id: e.p.id, number: e.p.number, name: e.p.name, l: e.l,
                }))} onPlayer={onPlayer} />
              </>""",
    """                <BoxTable title="Forwards" showSpot rows={skaters
                  .filter((e) => e.p.position === "F")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, spot: e.p.spot, l: e.l }, true))}
                  onPlayer={onPlayer} />
                <BoxTable title="Defense" rows={skaters
                  .filter((e) => e.p.position === "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }, true))}
                  onPlayer={onPlayer} />
                {/* Anything with an unrecognised position still has to appear. */}
                <BoxTable title="Skaters" rows={skaters
                  .filter((e) => e.p.position !== "F" && e.p.position !== "D")
                  .map((e) => withShots({ id: e.p.id, number: e.p.number, name: e.p.name, l: e.l }, true))}
                  onPlayer={onPlayer} />
                <GoalieTable rows={goalies.map((e) => ({
                  id: e.p.id, number: e.p.number, name: e.p.name, l: e.l,
                }))} onPlayer={onPlayer} />
                <UnnamedShots n={unnamedShots(true)} />
              </>""")

sub("""                <BoxTable title="Forwards" showSpot rows={oppSkaters
                  .filter((x) => oppPos(x) === "F")
                  .map((x) => ({ id: x.id, number: x.number, name: x.name, spot: oppSpot(x), l: x }))} />
                <BoxTable title="Defense" rows={oppSkaters
                  .filter((x) => oppPos(x) === "D")
                  .map((x) => ({ id: x.id, number: x.number, name: x.name, l: x }))} />
                <BoxTable title="Skaters" rows={oppSkaters
                  .filter((x) => !oppPos(x))
                  .map((x) => ({ id: x.id, number: x.number, name: x.name, l: x }))} />""",
    """                <BoxTable title="Forwards" showSpot rows={oppSkaters
                  .filter((x) => oppPos(x) === "F")
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, spot: oppSpot(x), l: x }, false))} />
                <BoxTable title="Defense" rows={oppSkaters
                  .filter((x) => oppPos(x) === "D")
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, l: x }, false))} />
                <BoxTable title="Skaters" rows={oppSkaters
                  .filter((x) => !oppPos(x))
                  .map((x) => withShots({ id: x.id, number: x.number, name: x.name, l: x }, false))} />""")

# ------------------------------------------------------------ the footnote
sub("""function pts(l) {
  return (Number(l.g) || 0) + (Number(l.a) || 0);
}""",
    """function pts(l) {
  return (Number(l.g) || 0) + (Number(l.a) || 0);
}

/* Shots the scorekeeper counted for the team without naming a shooter. The
   S column adds up to less than the team's own total when this happens, and
   saying so is better than leaving the reader to find the gap. */
function UnnamedShots({ n }) {
  if (!n) return null;
  return (
    <p className="bsm gcnone gcpad" style={{ margin: "10px 0 0" }}>
      {n === 1 ? "1 shot was" : n + " shots were"} counted for the team without a
      shooter recorded, so {n === 1 ? "it is" : "they are"} not on anyone's line.
    </p>
  );
}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('shots on goal, per player')
