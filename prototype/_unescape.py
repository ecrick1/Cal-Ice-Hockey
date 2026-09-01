# -*- coding: utf-8 -*-
"""Arrows that are arrows.

A \\uXXXX sequence is an escape inside a JavaScript string and six ordinary
characters inside JSX text. The move and remove buttons were written with
the second while meaning the first, so every one of them read "\\u2191"
instead of an arrow. Same mistake as the face-off prompt's em-dashes, in the
same shape, from the same habit of writing the escape into the patch script
rather than the character.

Replaced with the characters themselves, which is what should have been
there: JSX text needs no escaping.
"""
import io
import re

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

CHARS = {
    '2715': u'✕', '2191': u'↑', '2193': u'↓',
    '2190': u'←', '2192': u'→', '2014': u'—',
}

before = s
for code, ch in CHARS.items():
    s = s.replace('>' + '\\u' + code + '<', '>' + ch + '<')
    s = s.replace('>' + '\\u' + code + '</button>}', '>' + ch + '</button>}')
# "— pick one —" inside an <option>
s = s.replace('>' + '\\u2014' + ' pick one ' + '\\u2014' + '<',
              '>' + u'—' + ' pick one ' + u'—' + '<')

io.open(p, 'w', encoding='utf-8').write(s)
left = re.findall(r'>\\u[0-9a-fA-F]{4}', s)
print('changed:', s != before, '| JSX-text escapes left:', len(left))
