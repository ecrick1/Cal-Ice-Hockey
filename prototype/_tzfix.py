# -*- coding: utf-8 -*-
"""Restore the word boundaries the heredoc ate."""
import io
p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()
a = '  }).replace(/AM/, "am").replace(/PM/, "pm");'
b = '  }).replace(/\bAM\b/, "am").replace(/\bPM\b/, "pm");'
assert s.count(a) == 1
io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
