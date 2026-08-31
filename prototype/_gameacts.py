# -*- coding: utf-8 -*-
"""Two pills on the card itself, not a text link under a rule.

Game center was a text link with an arrow, sitting alone at the far right of
the footer - the least prominent thing on the card, and the one people most
want. It becomes a pill, cut to the same pattern as the watch link, and the
pair moves up above the rule into the card body where the game is.

The replay pill loses its dot for a play mark and reads "Replay". A dot next
to the word Live means something - it is pulsing, the game is on now - but
the same dot next to a finished game said nothing at all.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)


# -------------------------------------------------------------------- icon
sub("""const IcBars = (p) => <Ic {...p} d={<path d="M5 20V12M12 20V4M19 20v-6" />} />;""",
    """const IcBars = (p) => <Ic {...p} d={<path d="M5 20V12M12 20V4M19 20v-6" />} />;
/* Play, in a filled circle. Solid rather than stroked, to sit beside the
   filled game-centre mark without one looking lighter than the other. */
const IcPlayCircle = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true"
    style={{ display: "block", flex: "0 0 auto" }}>
    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2M9.5 16.5v-9l7 4.5z" />
  </svg>
);""")

# ------------------------------------------------------------- the pill text
sub("""      <span className={isFinal ? "watchdot" : "livedot"} aria-hidden="true" />
      {isFinal ? "Watch replay" : "Watch live"}""",
    """      {isFinal
        ? <IcPlayCircle size={size === "sm" ? 14 : 17} />
        : <span className="livedot" aria-hidden="true" />}
      {isFinal ? "Replay" : "Watch live"}""")

# ------------------------------------------------- the card: pills, not links
sub("""                    <div className="gamefoot">
                      <WatchLink game={g} />
                      <button className="gb-link" style={{ fontWeight: 700, display: "inline-flex", gap: 7, alignItems: "center" }}
                        onClick={() => setOpenInfo(open ? null : g.id)} aria-expanded={open}>
                        Quick look {open ? <IcMinusC size={19} /> : <IcPlusC size={19} />}
                      </button>
                      <button className="gb-link" style={{ marginLeft: "auto", fontWeight: 700, display: "inline-flex", gap: 7, alignItems: "center" }}
                        onClick={() => onGame && onGame(g.id)}>
                        Game center <IcArrowR size={17} />
                      </button>
                    </div>""",
    """                      <div className="gameacts">
                        <WatchLink game={g} />
                        <button className="watchbtn" onClick={() => onGame && onGame(g.id)}>
                          <IcGameCenter size={17} /> Game center
                        </button>
                      </div>
                    </div>
                    <div className="gamefoot">
                      <button className="gb-link" style={{ fontWeight: 700, display: "inline-flex", gap: 7, alignItems: "center" }}
                        onClick={() => setOpenInfo(open ? null : g.id)} aria-expanded={open}>
                        Quick look {open ? <IcMinusC size={19} /> : <IcPlusC size={19} />}
                      </button>
                    </div>""")

# The actions row closes `.gamemain`, so the old close tag has to go.
sub("""                        <p className="bsm" style={{ margin: r ? "5px 0 0" : 0, color: "var(--muted)", fontWeight: 600 }}>
                          <strong style={{ color: "var(--ink)" }}>{fmtDateParen(g.date)}</strong> · <IcClock size={13} style={{ marginRight: 4 }} />{localTime(g.date, g.time)}
                        </p>
                      </div>
                    </div>
                      <div className="gameacts">""",
    """                        <p className="bsm" style={{ margin: r ? "5px 0 0" : 0, color: "var(--muted)", fontWeight: 600 }}>
                          <strong style={{ color: "var(--ink)" }}>{fmtDateParen(g.date)}</strong> · <IcClock size={13} style={{ marginRight: 4 }} />{localTime(g.date, g.time)}
                        </p>
                      </div>
                      <div className="gameacts">""")

# -------------------------------------------------------------------- CSS
sub(""".gamefoot { border-top: 1px solid #EEF1F4; padding: 10px 22px; display: flex; }
/* Watch live sits right against Quick look; without a gap they read as one
   control rather than two. */
.gamefoot .watchbtn { margin-right: 10px; }""",
    """.gamefoot { border-top: 1px solid #EEF1F4; padding: 10px 22px; display: flex; }
/* Replay and Game center, on their own line inside the card rather than
   under the rule. A full-width flex item, so they break to a row of their
   own however the rest of the card has wrapped. */
.gameacts { flex: 1 0 100%; display: flex; flex-wrap: wrap; gap: 10px; }
button.watchbtn { border: 0; cursor: pointer; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('actions row built')
