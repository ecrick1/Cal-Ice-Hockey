# -*- coding: utf-8 -*-
"""An intermission that counts down, instead of a flag that says one is on.

Intermission was a switch. It said "End 2nd" on the public page, stopped the
game clock, and told nobody the thing everyone in the building wants to
know, which is how long until they play again. The scorekeeper had no way to
put fifteen minutes on the board and the viewer had no way to read them.

So it runs on a clock of its own, anchored the same way the game clock is -
what was left when it was last stopped, and when it was last started - so it
survives a reload, a second screen and a browser that was closed at the
break. It cannot borrow the game clock, because the game clock is holding
20:00 for the period about to start and would have to be put back afterwards.

Fifteen minutes by default, which is what the ACHA plays, and settable to
eighteen or twenty for the nights that run long. The length lives on the
game, so a rink that always does eighteen keeps it for the whole night.

It counts to zero and stops there rather than running negative or bouncing
into the next period on its own: what happens next is a decision - the teams
come out, or they do not - and a scoreboard that starts the third by itself
is worse than one that waits to be told.

Starting an intermission also moves the period on, because there is exactly
one period that follows the second and typing it in afterwards was a step
that existed only to be forgotten. The game clock is set to full for it, and
the picker still overrides.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the model
sub("""/* Milliseconds left on the clock right now. */
function clockLeft(live, now) {""",
    """/* How long a break between periods runs. Fifteen is what the ACHA plays;
   the others are here for rinks that run longer. */
const INTERMISSION_CHOICES = [15, 18, 20];
const INTERMISSION_SECS = 15 * 60;

/* Milliseconds left in the intermission.
 *
 * Anchored exactly like the game clock, and separate from it, because the
 * game clock is holding 20:00 for the period about to start - borrowing it
 * would mean putting it back afterwards and getting that right every time. */
function intermissionLeft(live, now) {
  if (!live || !live.intermission) return 0;
  const base = Number(live.breakMs);
  const ms = Number.isFinite(base) ? base : INTERMISSION_SECS * 1000;
  if (!live.breakAt) return Math.max(0, ms);
  return Math.max(0, ms - ((now ?? Date.now()) - live.breakAt));
}

/* Milliseconds left on the clock right now. */
function clockLeft(live, now) {""")

# ------------------------------------------------- what the public reads
sub("""  if (live.intermission) return p === "3" ? "End of regulation" : "End " + named;""",
    """  if (live.intermission) {
    /* The one thing everyone in the building wants to know. Once it has run
       out it stops being news and the period is what matters again. */
    const bl = intermissionLeft(live, now);
    const head = p === "3" ? "End of regulation" : "End " + named;
    return bl > 0 ? head + " · " + fmtClock(bl) : head;
  }""")

# --------------------------------------------------------- the console
sub("""            {/* Stops the clock as well as saying so — an intermission with a
                running clock is a state nobody wants to explain. */}
            {!retro && (
              <button className={"btn bSm " + (live.intermission ? "bNavy" : "bGhost")}
                onClick={() => setLive({
                  intermission: !live.intermission,
                  running: false, clockMs: left, startedAt: null,
                })}>
                Intermission
              </button>
            )}""",
    """            {/* Stops the game clock as well as saying so — an intermission
                with a running clock is a state nobody wants to explain. */}
            {!retro && (
              <button className={"btn bSm " + (live.intermission ? "bNavy" : "bGhost")}
                onClick={() => (live.intermission
                  ? setLive({ intermission: false, breakAt: null })
                  : startIntermission())}>
                {live.intermission ? "End intermission" : "Intermission"}
              </button>
            )}
            {!retro && live.intermission && (
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
            )}""")

# The clock face shows whichever clock is actually running.
sub("""          <p className="aubugclock">{retro ? "FINAL" : fmtClock(left)}</p>""",
    """          {/* Whichever clock is actually running. During a break the game
              clock is parked on the next period and is not the number
              anybody is looking for. */}
          <p className={"aubugclock" + (live.intermission ? " aubugbreak" : "")}>
            {retro ? "FINAL" : live.intermission ? fmtClock(breakLeft) : fmtClock(left)}
          </p>
          {live.intermission && !retro && (
            <p className="aubugbreaklab">
              {breakLeft > 0 ? "Intermission" : "Intermission over"}
            </p>
          )}""")

# ------------------------------------------------------------- the start
sub("""  const left = clockLeft(live, now);""",
    """  const left = clockLeft(live, now);
  const breakLeft = intermissionLeft(live, now);
  const breakChoice = Number(live.breakLen) || INTERMISSION_SECS / 60;""")

sub("""  /* ---- Clock ---- */""",
    """  /* The break starts, and the period moves on with it: exactly one period
     follows the second, and typing it in afterwards was a step that existed
     only to be forgotten. The picker still overrides. */
  const startIntermission = () => {
    const order = ["1", "2", "3", "OT"];
    const i = order.indexOf(live.period || "1");
    const next = i >= 0 && i < order.length - 1 ? order[i + 1] : live.period;
    const mins = Number(live.breakLen) || INTERMISSION_SECS / 60;
    push({
      plays: hasPeriodMark("end", live.period || "1") ? plays : [...plays, {
        id: uid(), kind: "period", phase: "end", period: live.period || "1",
        clock: fmtClock(left),
      }],
      live: {
        ...live,
        intermission: true,
        running: false, startedAt: null,
        /* The game clock goes to the top of the period that is coming. */
        period: next, clockMs: periodSecs(next) * 1000,
        breakLen: mins, breakMs: mins * 60 * 1000, breakAt: Date.now(),
      },
    });
  };

  /* ---- Clock ---- */""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
/* The break clock is not the game clock and should not be mistaken for it
   at a glance across a press box. */
.adminui .aubugclock.aubugbreak { color: var(--au-warn, #F5B544); }
.adminui .aubugbreaklab { margin: 2px 0 0; text-align: center; font-size: 10.5px;
  font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--au-faint); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the intermission has a clock')
