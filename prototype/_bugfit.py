# -*- coding: utf-8 -*-
"""The scoreboard controls stay inside the scoreboard.

Adding the break controls put seven things in the row under the clock -
period, Start, End intermission, Pause break, the length, Timeout - and that
row sits in the middle column of a three-column grid whose outer columns
hold the shot counters. An auto-sized grid track takes whatever its contents
demand, so the middle grew and squeezed the sides until the plus button on
the visitors' shots hung twenty-one pixels outside the panel.

Two changes, because either alone leaves the other case broken.

The break controls move to a row of their own, under the ones that are
always there. They only exist during an intermission, and a row that changes
length depending on whether the teams are on the ice is a row that will
overflow again the next time something is added to it.

And the panel is made able to shrink. The middle track can now go below what
its contents would like, the control rows wrap when they have to, and so do
the shot counters - so a narrow window folds the buttons onto another line
instead of pushing them through the wall. That is the part that stops this
happening again for a reason nobody has thought of yet.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ================================================ the break gets its own row
sub("""            {onBreak && (
              <>
                <button className="btn bSm bGhost"
                  onClick={() => setLive(live.breakAt
                    ? { breakMs: intermissionLeft(live, now), breakAt: null }
                    : { breakAt: Date.now() })}>
                  {live.breakAt ? "Pause break" : "Resume break"}
                </button>
                <select value={breakChoice}
                  title="How long the break runs"
                  onChange={(e) => setLive({
                    breakLen: Number(e.target.value),
                    breakMs: Number(e.target.value) * 60 * 1000,
                    breakAt: live.breakAt ? Date.now() : null,
                  })}>
                  {INTERMISSION_CHOICES.map((m) => (
                    <option key={m} value={m}>{m} min</option>
                  ))}
                </select>
              </>
            )}
            {!retro && (""",
    """            {!retro && (""")

sub("""                Timeout
              </button>
            )}
          </div>
          {/* The arm is up and play has not stopped.""",
    """                Timeout
              </button>
            )}
          </div>

          {/* Only while the teams are off the ice. On its own row because a
              control row that changes length with the state of the game is a
              row that overflows the next time anything is added to it. */}
          {onBreak && (
            <div className="aubugctl aubugbreakctl">
              <button className="btn bSm bGhost"
                onClick={() => setLive(live.breakAt
                  ? { breakMs: intermissionLeft(live, now), breakAt: null }
                  : { breakAt: Date.now() })}>
                {live.breakAt ? "Pause break" : "Resume break"}
              </button>
              <select value={breakChoice}
                title="How long the break runs"
                onChange={(e) => setLive({
                  breakLen: Number(e.target.value),
                  breakMs: Number(e.target.value) * 60 * 1000,
                  breakAt: live.breakAt ? Date.now() : null,
                })}>
                {INTERMISSION_CHOICES.map((m) => (
                  <option key={m} value={m}>{m} min</option>
                ))}
              </select>
            </div>
          )}
          {/* The arm is up and play has not stopped.""")

# ================================================== and the panel can shrink
sub(""".adminui .aubug { display: grid; grid-template-columns: 1fr auto 1fr; gap: 18px;""",
    """/* Every track allowed to go below its contents' preferred width. An auto
   track takes whatever it is asked for, which is how the middle column grew
   until it pushed the visitors' shot buttons out through the side of the
   panel. Shrinking is what lets the rows below wrap instead. */
.adminui .aubug { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr);
  gap: 18px;""")

sub(""".adminui .aubugctl { display: flex; gap: 8px; align-items: center; }""",
    """.adminui .aubugctl { display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; justify-content: center; }
/* The break controls, on their own line under the ones always there. */
.adminui .aubugbreakctl { margin-top: 2px; }""")

sub(""".adminui .aushots { display: flex; align-items: center; justify-content: center; gap: 8px;
  margin-top: 10px; font-size: 12px; color: var(--au-dim); }""",
    """.adminui .aushots { display: flex; align-items: center; justify-content: center; gap: 8px;
  flex-wrap: wrap; margin-top: 10px; font-size: 12px; color: var(--au-dim); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the controls stay inside')
