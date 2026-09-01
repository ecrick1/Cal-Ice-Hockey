# -*- coding: utf-8 -*-
"""The ticker runs for the intermission clock too.

The page only re-rendered while the game clock was running, which was right
when the game clock was the only clock. An intermission counts down with the
game clock stopped, so every screen showing it - the console, the strip, the
home banner, the game page - would have painted the break once and then sat
there, frozen on whatever second it happened to start on.

One predicate now, asked in all four places: a clock is ticking if the game
clock is running or a break is counting down. A paused break stops the timer
again, because a paused clock is not moving and nothing needs repainting.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""/* How long a break between periods runs.""",
    """/* Is anything counting down? The game clock, or a break between periods -
   the second of which runs with the first deliberately stopped, so asking
   only about the game clock left every intermission frozen on screen. A
   paused break is not moving and does not need the repaint. */
function clockTicking(live) {
  return !!(live && (live.running || (live.intermission && live.breakAt)));
}

/* How long a break between periods runs.""")

sub("""  const tick = useClockTick(schedule.some((g) => g.live && g.live.running));""",
    """  const tick = useClockTick(schedule.some((g) => clockTicking(g.live)));""")

sub("""  const liveRunning = !!(game && game.live && game.live.running);
  const now = useClockTick(liveRunning);""",
    """  const liveRunning = !!(game && game.live && game.live.running);
  const now = useClockTick(clockTicking(game && game.live));""")

sub("""  const tick = useClockTick(!!(liveGame && liveGame.live && liveGame.live.running));""",
    """  const tick = useClockTick(clockTicking(liveGame && liveGame.live));""")

sub("""  const now = useClockTick(!!live.running);""",
    """  const now = useClockTick(clockTicking(live));""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the ticker follows both clocks')
