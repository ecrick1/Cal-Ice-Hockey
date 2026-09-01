# -*- coding: utf-8 -*-
"""The per-player face-off stats come out.

Two columns of em-dashes on every row of every box score, a second question
at every draw to feed them, and three fields carried through the totals for
a number nobody wanted. It went in on request and it is coming out on
request; what it cost while it was there was two of the twelve columns and a
press per face-off, which is the wrong trade for a statistic a club side
does not keep.

The draws themselves stay. "CAL won the draw" is a play, not a statistic -
it is how the play-by-play says where the puck went after a whistle, and it
was there long before any of this.

The team face-off percentage on the Game stats panel stays too. It predates
this, it is counted from the draws rather than from any player line, and
removing it was not what was asked for.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# =========================================================== the columns
sub("""              <StatTh label="S" /><StatTh label="FO" /><StatTh label="FO%" />
              <StatTh label="PIM" /><StatTh label="PPG" /><StatTh label="SHG" />""",
    """              <StatTh label="S" />
              <StatTh label="PIM" /><StatTh label="PPG" /><StatTh label="SHG" />""")

sub("""                <td>{r.l.shots || 0}</td>
                <td>{foRecord(r.l)}</td>
                <td className="gcbtpts">{foPct(r.l)}</td>
                <td>{r.l.pim || 0}</td>""",
    """                <td>{r.l.shots || 0}</td>
                <td>{r.l.pim || 0}</td>""")

sub("""
/* Draws won and lost. A dash rather than 0-0 for anyone who never took one,
   because never being sent to the circle and losing every draw are not the
   same thing to read. */
function foRecord(l) {
  const w = Number(l.fow) || 0, x = Number(l.fol) || 0;
  return w + x ? w + "-" + x : "\\u2014";
}
function foPct(l) {
  const w = Number(l.fow) || 0, x = Number(l.fol) || 0;
  return w + x ? Math.round((w / (w + x)) * 100) + "%" : "\\u2014";
}""", "")

sub("""  FO: "Face-offs won and lost",
  "FO%": "Face-off win percentage",
""", "")

# ============================================================ the totals
sub("""    /* Counted off the play-by-play as the game is scored. A draw records
       both ends, so a centre's record reads against something. */
    shots: 0, fow: 0, fol: 0,""",
    """    /* Counted off the play-by-play as the game is scored. */
    shots: 0,""")

sub("""    t.shots += Number(line.shots) || 0;
    t.fow += Number(line.fow) || 0;
    t.fol += Number(line.fol) || 0;""",
    """    t.shots += Number(line.shots) || 0;""")

sub("""    "w", "l", "tie", "shots", "fow", "fol",""",
    """    "w", "l", "tie", "shots",""")

# ======================================================== the tallies
sub("""      else if (x.kind === "faceoff") {
        /* The play is filed under whoever won it, so ours is the winner on
           our draws and the loser on theirs. */
        if (x.team === "us") add(x.winnerId, "fow");
        else add(x.loserId, "fol");
      }""", "")

sub("""        const next = { ...cur, shots: t.shots || 0, fow: t.fow || 0, fol: t.fol || 0 };
        if (cur.shots !== next.shots || cur.fow !== next.fow || cur.fol !== next.fol) {""",
    """        const next = { ...cur, shots: t.shots || 0 };
        if (cur.shots !== next.shots) {""")

sub("""          } else if (x.kind === "shot") {
            add(find(x.shooterId, x.shooter), "shots");
          } else if (x.kind === "faceoff") {
            add(find(x.winnerId, x.winner), "fow");
          }
        } else if (x.kind === "faceoff" && x.team === "us") {
          /* Our draw, so theirs is the one who lost it. */
          add(find(x.loserId, x.loser), "fol");
        }""",
    """          } else if (x.kind === "shot") {
            add(find(x.shooterId, x.shooter), "shots");
          }
        }""")

sub("""        const m = {
          ...r, g: c.g || 0, a: c.a || 0, pim: c.pim || 0,
          shots: c.shots || 0, fow: c.fow || 0, fol: c.fol || 0,
        };
        if (m.g !== r.g || m.a !== r.a || m.pim !== r.pim
          || m.shots !== r.shots || m.fow !== r.fow || m.fol !== r.fol) touched = true;""",
    """        const m = { ...r, g: c.g || 0, a: c.a || 0, pim: c.pim || 0, shots: c.shots || 0 };
        if (m.g !== r.g || m.a !== r.a || m.pim !== r.pim
          || m.shots !== r.shots) touched = true;""")

# ===================================================== back to one question
sub("""  /* A draw is two players. Recording only the winner threw away half of it:
     a centre's record is what he won against what he took. */
  const commitFaceoff = (team, won, lost) => {
    push({
      plays: [...plays, {
        id: uid(), kind: "faceoff", team,
        period: curPeriod,
        /* The draw happened when play resumed, not when the name was picked. */
        clock: (faceoffAsk && faceoffAsk.clock) || fmtClock(left),
        ...won, ...lost,
      }],
    });
    setFaceoffAsk(null);
  };

  /* Who won, and then who lost - but only when the winner was named. Most
     draws are a scramble and the honest answer is a side rather than a man;
     if nobody could say who won it, nobody can say who lost it either. */
  const pickWinner = (team, value) => {
    const us = team === "us";
    const won = {
      winnerId: us ? value || null : null,
      winner: us ? nameOf(value) : value,
    };
    if (!value) return commitFaceoff(team, won, {});
    setFaceoffAsk({ ...(faceoffAsk || {}), team, won });
  };

  const pickLoser = (value) => {
    const a = faceoffAsk || {};
    /* The loser is on the other bench from the winner. */
    const theirsLost = a.team === "us";
    commitFaceoff(a.team, a.won, {
      loserId: theirsLost ? null : value || null,
      loser: theirsLost ? value : nameOf(value),
    });
  };""",
    """  /* One question. Who lost a draw was collected for a per-player record that
     is no longer kept, and it cost a press at every face-off. */
  const winFaceoff = (team, value) => {
    const us = team === "us";
    push({
      plays: [...plays, {
        id: uid(), kind: "faceoff", team,
        period: curPeriod,
        /* The draw happened when play resumed, not when the name was picked. */
        clock: (faceoffAsk && faceoffAsk.clock) || fmtClock(left),
        winnerId: us ? value || null : null,
        winner: us ? nameOf(value) : value,
      }],
    });
    setFaceoffAsk(null);
  };""")

io.open(p, 'w', encoding='utf-8').write(s)
print('per-player face-off stats removed')
