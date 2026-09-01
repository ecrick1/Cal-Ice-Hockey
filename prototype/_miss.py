# -*- coding: utf-8 -*-
"""Record a shot that missed the net.

A miss is not a shot on goal and must never be counted as one - that is the
whole reason to record it separately rather than nudging the SOG counter and
taking it back. So it writes its own play and leaves shotsUs, shotsThem and
the per-period buckets alone, which means the shot totals on the scoreboard,
in the box score and in the goaltender's save percentage are unaffected by
pressing it.

It reuses the shot machinery otherwise: the same "who took it?" prompt a
moment later, the same undo by pressing minus, the same place in the
play-by-play. It appears in the game centre's play-type filter as its own
entry, because someone reading back through a period wants to be able to
separate the two.

Nothing derives a stat from it yet. A missed-shot count is a real number
and could be shown, but it would be shown for the games somebody happened
to press it during and blank for the rest, which reads as nought rather
than as unrecorded.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the control
sub("""function Shots({ value, label, onChange }) {
  return (
    <div className="aushots">
      <button className="btn bGhost" aria-label={"One fewer shot for " + label}
        onClick={() => onChange(Math.max(0, value - 1))}>−</button>
      <span><strong>{value}</strong> SOG</span>
      <button className="btn bGhost" aria-label={"One more shot for " + label}
        onClick={() => onChange(value + 1)}>+</button>
    </div>
  );
}""",
    """function Shots({ value, label, onChange, missed, onMiss, onUnmiss }) {
  return (
    <div className="aushots">
      <button className="btn bGhost" aria-label={"One fewer shot for " + label}
        onClick={() => onChange(Math.max(0, value - 1))}>−</button>
      <span><strong>{value}</strong> SOG</span>
      <button className="btn bGhost" aria-label={"One more shot for " + label}
        onClick={() => onChange(value + 1)}>+</button>
      {/* Wide of the net, so it is not a shot on goal and does not touch the
          count beside it. Its own pair of controls rather than a mode on
          the ones above, because the two are pressed in the same second and
          a mode you have to notice is a mode you will get wrong. */}
      <span className="aumissbox">
        <button className="btn bGhost" aria-label={"One fewer miss for " + label}
          disabled={!missed} onClick={onUnmiss}>−</button>
        <span className="aumisscount"><strong>{missed}</strong> wide</span>
        <button className="btn bGhost" aria-label={"One more miss for " + label}
          onClick={onMiss}>+</button>
      </span>
    </div>
  );
}""")

# --------------------------------------------------------------- the write
sub("""  const [shotAsk, setShotAsk] = useState(null);""",
    """  /* A miss writes a play and nothing else: the shot counters, the period
     buckets and every save percentage read off them stay where they were. */
  const missCount = (side) => plays.filter((p) => p.kind === "miss" && p.team === side).length;

  const addMiss = (side) => {
    const pid = uid();
    push({ plays: [...plays, { id: pid, kind: "miss", team: side, ...whenNow() }] });
    setShotAsk({ id: pid, side, missed: true });
  };

  const undoMiss = (side) => {
    for (let i = plays.length - 1; i >= 0; i--) {
      if (plays[i].kind === "miss" && plays[i].team === side) {
        push({ plays: [...plays.slice(0, i), ...plays.slice(i + 1)] });
        return;
      }
    }
  };

  const [shotAsk, setShotAsk] = useState(null);""")

# ------------------------------------------------------------- the two uses
sub("""          <Shots value={live.shotsUs || 0} label={usLabel}
            onChange={(v) => bumpShots("us", v - (live.shotsUs || 0))} />""",
    """          <Shots value={live.shotsUs || 0} label={usLabel}
            onChange={(v) => bumpShots("us", v - (live.shotsUs || 0))}
            missed={missCount("us")} onMiss={() => addMiss("us")}
            onUnmiss={() => undoMiss("us")} />""")

sub("""          <Shots value={live.shotsThem || 0} label={oppName || "Them"}""",
    """          <Shots value={live.shotsThem || 0} label={oppName || "Them"}
            missed={missCount("them")} onMiss={() => addMiss("them")}
            onUnmiss={() => undoMiss("them")}""")

# --------------------------------------------------------- who took it
sub("""          <span className="h6">Who shot it?</span>""",
    """          <span className="h6">{shotAsk.missed ? "Who missed?" : "Who shot it?"}</span>""")

# --------------------------------------------------- reading it back later
sub("""                    ) : p.kind === "faceoff" ? (
                      <>
                        <span className="auplaykind stop">FO</span>
                        <span className="auplaywho">{p.winner || "Faceoff won"}</span>
                      </>""",
    """                    ) : p.kind === "miss" ? (
                      <>
                        <span className="auplaykind stop">MISS</span>
                        <span className="auplaywho">{p.shooter || "Shot missed"}</span>
                      </>
                    ) : p.kind === "faceoff" ? (
                      <>
                        <span className="auplaykind stop">FO</span>
                        <span className="auplaywho">{p.winner || "Faceoff won"}</span>
                      </>""", 2)

sub("""                  ["shot", "Shots on goal"], ["faceoff", "Face-offs"], ["timeout", "Timeouts"],""",
    """                  ["shot", "Shots on goal"], ["miss", "Missed shots"],
                  ["faceoff", "Face-offs"], ["timeout", "Timeouts"],""")

# -------------------------------------------------------------------- CSS
sub(""".adminui .aushots .btn { padding: 2px 9px; font-size: 14px; line-height: 1.2; }""",
    """.adminui .aushots .btn { padding: 2px 9px; font-size: 14px; line-height: 1.2; }
/* Set apart from the shot counter and quieter than it: a miss is worth
   recording and is not the number on the scoreboard. */
.adminui .aumissbox { display: inline-flex; align-items: center; gap: 6px;
  margin-left: 12px; padding-left: 12px; border-left: 1px solid var(--au-line); }
.adminui .aumisscount { font-size: 12px; color: var(--au-dim); }
.adminui .aumisscount strong { font-family: var(--au-mono, monospace); font-size: 13px;
  color: var(--au-text); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('miss wide added')
