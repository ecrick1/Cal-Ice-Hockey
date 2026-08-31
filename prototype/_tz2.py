# -*- coding: utf-8 -*-
"""Swap the remaining public game-time displays over to the reader's zone.

Each site is found by an ASCII-only fragment of its own line and rewritten
with a regex, so no pattern in this file has to carry a middot or an em dash -
which is what kept going wrong.
"""
import io
import re

p = '../reference/cal-ice-hockey-app.jsx'
lines = io.open(p, encoding='utf-8').read().split('\n')

# (anchor unique to the line, what to replace on it, what to replace it with)
JOBS = [
    ('<dd>{fmtDate(game.date)}{game.time ?',
     [('{fmtDate(game.date)}', '{localDate(game.date, game.time)}'),
      ('+ game.time :', '+ localTime(game.date, game.time) :')]),
    ('{game.time && <p>{game.time}</p>}',
     [('<p>{game.time}</p>', '<p>{localTime(game.date, game.time)}</p>')]),
    (': st === "live" ? "Live" : (g.time || "TBD")}',
     [('(g.time || "TBD")', '(localTime(g.date, g.time) || "TBD")')]),
    ('<span className="caltime">{g.time || "TBD"}</span>',
     [('{g.time || "TBD"}', '{localTime(g.date, g.time) || "TBD"}')]),
    ('{decidedIn(g.result)}</strong> : g.time}</td>',
     [('</strong> : g.time}', '</strong> : localTime(g.date, g.time)}')]),
    ('<IcClock size={13} style={{ marginRight: 4 }} />{g.time}',
     [('/>{g.time}', '/>{localTime(g.date, g.time)}')]),
    ('<span><strong>Date:</strong> {fmtDate(g.date)}',
     [('{fmtDate(g.date)}', '{localDate(g.date, g.time)}'),
      ('{g.time}</span>', '{localTime(g.date, g.time)}</span>')]),
    ('${g.result.ot ? " (OT)" : ""}` : g.time}</td>',
     [('` : g.time}', '` : localTime(g.date, g.time)}')]),
    ('{featureState === "scheduled" && feature.time ?',
     [('+ feature.time :', '+ localTime(feature.date, feature.time) :')]),
]

done = {}
for i, line in enumerate(lines):
    for anchor, edits in JOBS:
        if anchor not in line:
            continue
        new = line
        for a, b in edits:
            assert a in new, (anchor, a)
            new = new.replace(a, b)
        lines[i] = new
        done[anchor] = done.get(anchor, 0) + 1

missing = [a for a, _ in JOBS if a not in done]
assert not missing, missing
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
for a, _ in JOBS:
    print('%d  %s' % (done[a], a[:58]))
