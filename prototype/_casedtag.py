# -*- coding: utf-8 -*-
"""Fix the word-boundary that a shell heredoc ate.

The regex was written as a word boundary followed by a lowercase letter and
arrived as just the letter, which uppercases every character rather than the
first of each word. Written from a file this time, because a backslash in a
heredoc has now been eaten four times in this project and the lesson is
apparently not one I learn by intending to.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

old = 'return String(t || "").toLowerCase().replace(/[a-z]/g, (c) => c.toUpperCase());'
new = 'return String(t || "").toLowerCase().replace(/\\b[a-z]/g, (c) => c.toUpperCase());'

assert s.count(old) == 1, s.count(old)
io.open(p, 'w', encoding='utf-8').write(s.replace(old, new))
print('word boundary restored')
