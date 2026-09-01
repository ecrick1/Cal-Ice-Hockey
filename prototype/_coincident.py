# -*- coding: utf-8 -*-
"""One whistle, more than one penalty.

Entering the second penalty of a scrum meant re-finding the form after the
bar had closed, with the clock stopped and both benches yelling - and the
console had no idea the two calls belonged together. So the bar stays up.
It says how many have gone in at this whistle and waits for the next one,
and Done closes it.

That is also what makes them coincidental: every penalty entered while the
bar is up is stamped with the whistle's time rather than with the moment
the form was submitted, so the strength model sees one stoppage and cancels
the pair. Nothing is typed twice and no box is ticked.

Each penalty gets the resulting strength written onto its play, so reading
a game back a month later still says what the ice looked like. It is
recorded at the moment it is true rather than recomputed later, because the
clock it was true on has stopped by then.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================ what the ice looked like after
sub("""    const newPlays = pens.map((p) => ({
      id: p.id, kind: "penalty", team: penTeam, ...when,
      player, minutes: p.minutes,
      infraction: p.kind === "misconduct" && rows.length > 1 ? "Misconduct" : penWhat,
    }));""",
    """    /* The strength this call produced, written down while it is true. The
       clock these penalties run on has stopped by the time anyone reads the
       game back, so it cannot be worked out again afterwards. */
    const after = retro ? null : strengthState(
      { ...live, penalties: [...(live.penalties || []), ...pens] }, now);
    const madeIt = after && after.kind !== "EV" ? after.label : null;

    const newPlays = pens.map((p) => ({
      id: p.id, kind: "penalty", team: penTeam, ...when,
      player, minutes: p.minutes,
      infraction: p.kind === "misconduct" && rows.length > 1 ? "Misconduct" : penWhat,
      ...(madeIt && penaltyKind(p.kind).shorts ? { strength: madeIt } : {}),
    }));""")

# ================================================ the bar waits for the next
sub("""      plays: [...plays, ...newPlays],
      live: retro
        ? { ...live, ejected }
        : { ...live, penalties: [...(live.penalties || []), ...pens], ejected, delayed: null },
    });
    setPenPlayer(""); setPenOpp("");
    setPenPending(null);
  };""",
    """      plays: [...plays, ...newPlays],
      live: retro
        ? { ...live, ejected }
        : { ...live, penalties: [...(live.penalties || []), ...pens], ejected, delayed: null },
    });
    setPenPlayer(""); setPenOpp("");
    /* The bar stays up. A scrum is two or four calls at one whistle and the
       second one was being entered after the form had closed; leaving it
       open is also what stamps them all with the same stoppage, which is
       what makes them cancel. */
  };""")

sub("""      {penPending && (
        <div className="austop aupenwait">
          <span className="h6">Whistle at {penPending.clock} — enter the penalty</span>
          <span className="bsm">It goes on the sheet with the penalty, not before it.</span>
          <button className="btn bGhost bSm austopskip" onClick={() => setPenPending(null)}>
            No penalty after all
          </button>
        </div>
      )}""",
    """      {penPending && (() => {
        /* Everything already entered at this whistle. Two here means the
           benches are even and a man light rather than anyone up one. */
        const atWhistle = plays.filter((x) => x.kind === "penalty"
          && x.period === penPending.period && x.clock === penPending.clock);
        const mine = atWhistle.filter((x) => x.team === "us").length;
        const theirs = atWhistle.length - mine;
        return (
          <div className="austop aupenwait">
            <span className="h6">
              {atWhistle.length
                ? "Whistle at " + penPending.clock + " — another penalty?"
                : "Whistle at " + penPending.clock + " — enter the penalty"}
            </span>
            <span className="bsm">
              {atWhistle.length
                ? "In so far: " + (mine ? mine + " on " + usLabel : "")
                  + (mine && theirs ? ", " : "")
                  + (theirs ? theirs + " on " + (oppName || "them") : "")
                  + (mine && theirs ? ". Matching calls cancel — both benches skate a man short."
                    : ". Add the other team's if the calls were together.")
                : "It goes on the sheet with the penalty, not before it."}
            </span>
            <button className="btn bGhost bSm austopskip" onClick={() => setPenPending(null)}>
              {atWhistle.length ? "Done" : "No penalty after all"}
            </button>
          </div>
        );
      })()}""")

# ============================================== reading it back on the sheet
sub("""                        <span className="auplaywho">{p.player}</span>
                        <span className="auplayassist">{p.infraction}</span>""",
    """                        <span className="auplaywho">{p.player}</span>
                        <span className="auplayassist">
                          {p.infraction}
                          {p.strength && <b className="auplaystr">{p.strength}</b>}
                        </span>""", 2)

sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
/* What the call did to the ice, beside the call. */
.adminui .auplaystr { font-family: var(--au-mono, monospace); font-size: 10px;
  font-weight: 700; color: #A5B4FC; letter-spacing: 0.04em; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('one whistle, more than one penalty')
