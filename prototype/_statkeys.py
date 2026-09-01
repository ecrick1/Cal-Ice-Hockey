# -*- coding: utf-8 -*-
"""Shots and draws reach the season and career totals.

The box score holds them now, and the totals that read the box score were
adding up a fixed list of keys that did not mention them - so a shot
recorded against a name in the console reached the game's box score and
stopped there. Season stats and a player's career page never saw it, which
is most of what "store it for stats" has to mean.

Three keys added to the totals: shots, and draws won and lost. Nothing else
changes shape - they sum the way goals and minutes already do.

The imported-season fallback carries them too, so a year with totals on the
roster row and no game log behind it reports what it holds rather than
dropping the columns silently.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""  const t = {
    gp: 0, g: 0, a: 0, pim: 0, saves: 0, ga: 0,
    ppg: 0, shg: 0, gwg: 0, minutes: 0,""",
    """  const t = {
    gp: 0, g: 0, a: 0, pim: 0, saves: 0, ga: 0,
    ppg: 0, shg: 0, gwg: 0, minutes: 0,
    /* Counted off the play-by-play as the game is scored. A draw records
       both ends, so a centre's record reads against something. */
    shots: 0, fow: 0, fol: 0,""")

sub("""    t.minutes += Number(line.minutes) || 0;""",
    """    t.minutes += Number(line.minutes) || 0;
    t.shots += Number(line.shots) || 0;
    t.fow += Number(line.fow) || 0;
    t.fol += Number(line.fol) || 0;""")

sub("""  const keys = ["gp", "g", "a", "pim", "ppg", "shg", "gwg", "saves", "ga", "minutes", "so",
    "w", "l", "tie",""",
    """  const keys = ["gp", "g", "a", "pim", "ppg", "shg", "gwg", "saves", "ga", "minutes", "so",
    "w", "l", "tie", "shots", "fow", "fol",""")

io.open(p, 'w', encoding='utf-8').write(s)
print('shots and draws count toward the totals')
