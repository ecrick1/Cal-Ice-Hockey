# -*- coding: utf-8 -*-
"""A goal counts as a shot on the season page too.

The season stats table counts a player's shots off the plays and counted
only the ones that were saved or missed the net, so a goal - the shot that
worked - was the one shot that did not count as a shot. The box score says
otherwise and so does the rulebook, and a player with two goals and one save
made against him read as one shot rather than three.

Same definition in both places now: a shot on goal is a shot play or a goal.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""  const shotsBy = eachGame((p, g) => (g.plays || [])
    .filter((x) => x.kind === "shot" && x.shooterId === p.id).length);""",
    """  /* A goal is a shot that went in, so it counts. Leaving it out made the
     one shot that worked the only one that did not count as a shot, and put
     this column at odds with the box score, which has always counted both. */
  const shotsBy = eachGame((p, g) => (g.plays || []).filter((x) =>
    (x.kind === "shot" && x.shooterId === p.id)
    || (x.kind === "goal" && x.team === "us" && x.period !== "SO" && x.scorerId === p.id)
  ).length);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('a goal is a shot on the season page too')
