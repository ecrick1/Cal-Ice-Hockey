# -*- coding: utf-8 -*-
"""A \\uXXXX escape in JSX *text* is printed literally; only a JS string
literal interprets it. These five sit in text positions, so they get the real
character instead."""
import io
import re

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

DASH = u'—'
BARE = '\\u2014'

targets = [
    '<span className="h2hnum empty">%s</span>',
    '<span><strong>%s</strong>GP</span>',
    '<span><strong>%s</strong>GAA</span>',
    '<span><strong>%s</strong>SV%%</span>',
    '<span><strong>%s</strong>SO</span>',
]
for t in targets:
    old = t % BARE
    n = s.count(old)
    assert n, old
    s = s.replace(old, t % DASH)
    print('%d  %s' % (n, old[:52]))

left = re.findall(r'>\\u[0-9a-fA-F]{4}<', s)
print('remaining bare escapes in text:', left)
io.open(p, 'w', encoding='utf-8').write(s)
