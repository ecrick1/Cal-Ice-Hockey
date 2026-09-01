# -*- coding: utf-8 -*-
"""Starting play ends the intermission, and nothing trusts the flag alone.

The old Intermission button stopped the clock and set a flag, and Start set
the clock going again without clearing it. So pressing Intermission and then
Start left a game running with an intermission flag still on - the state the
button's own comment called one nobody wants to explain. It is in tonight's
game right now: running true, intermission true, seven minutes left in the
first.

It cost nothing while an intermission was only a word on the public page.
With a clock behind it, it puts the wrong number on the console: the game
clock is running and the face would show a break that is not happening.

Two fixes, because either alone leaves the other half wrong.

Start clears it, alongside the warm-up flag it already cleared for the same
reason - the puck has dropped, so whatever the game was doing before, it is
not doing it now.

And nothing reads the flag on its own. A break is an intermission and a
stopped clock, everywhere it is asked about, so a game that gets into the
contradictory state again by some route nobody has thought of shows the
clock that is actually running rather than the one that is not.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------- a break is a flag AND a stopped clock
sub("""function intermissionLeft(live, now) {
  if (!live || !live.intermission) return 0;""",
    """function intermissionLeft(live, now) {
  /* Both halves, everywhere. The flag on its own has been wrong before. */
  if (!live || !live.intermission || live.running) return 0;""")

sub("""function clockTicking(live) {
  return !!(live && (live.running || (live.intermission && live.breakAt)));
}""",
    """function clockTicking(live) {
  return !!(live && (live.running || (live.intermission && !live.running && live.breakAt)));
}""")

sub("""  if (live.intermission) {
    /* The one thing everyone in the building wants to know. Once it has run
       out it stops being news and the period is what matters again. */
    const bl = intermissionLeft(live, now);""",
    """  if (live.intermission && !live.running) {
    /* The one thing everyone in the building wants to know. Once it has run
       out it stops being news and the period is what matters again. */
    const bl = intermissionLeft(live, now);""")

# ----------------------------------------------- the puck drops, it is over
sub("""    const running = { running: true, clockMs: left, startedAt: Date.now(), warmup: false };""",
    """    /* Whatever the game was doing before, it is not doing it now: the
       warm-up is over and so is any break. Leaving the intermission flag on
       through a start is what produced a game running with a break clock. */
    const running = {
      running: true, clockMs: left, startedAt: Date.now(),
      warmup: false, intermission: false, breakAt: null,
    };""")

# ------------------------------------------------- and the console face
sub("""          <p className={"aubugclock" + (live.intermission ? " aubugbreak" : "")}>
            {retro ? "FINAL" : live.intermission ? fmtClock(breakLeft) : fmtClock(left)}
          </p>
          {live.intermission && !retro && (
            <p className="aubugbreaklab">
              {breakLeft > 0 ? "Intermission" : "Intermission over"}
            </p>
          )}""",
    """          <p className={"aubugclock" + (onBreak ? " aubugbreak" : "")}>
            {retro ? "FINAL" : onBreak ? fmtClock(breakLeft) : fmtClock(left)}
          </p>
          {onBreak && (
            <p className="aubugbreaklab">
              {breakLeft > 0 ? "Intermission" : "Intermission over"}
            </p>
          )}""")

sub("""  const breakLeft = intermissionLeft(live, now);""",
    """  const breakLeft = intermissionLeft(live, now);
  /* A break is the flag and a stopped clock, never the flag alone. */
  const onBreak = !retro && !!live.intermission && !live.running;""")

sub("""                onClick={() => (live.intermission
                  ? setLive({ intermission: false, breakAt: null })
                  : startIntermission())}>
                {live.intermission ? "End intermission" : "Intermission"}
              </button>
            )}
            {!retro && live.intermission && (""",
    """                onClick={() => (onBreak
                  ? setLive({ intermission: false, breakAt: null })
                  : startIntermission())}>
                {onBreak ? "End intermission" : "Intermission"}
              </button>
            )}
            {onBreak && (""")

io.open(p, 'w', encoding='utf-8').write(s)
print('start clears the break; nothing trusts the flag alone')
