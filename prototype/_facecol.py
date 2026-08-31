# -*- coding: utf-8 -*-
"""The right-hand face was still pinned to column 3 from the three-column
layout, where it collided with the category label and pushed the numbers to
their own rows. It belongs in the last column now."""
import io
p = "../reference/cal-ice-hockey-app.jsx"
s = io.open(p, encoding="utf-8").read()
a = """.h2hface.right { flex-direction: row-reverse; text-align: right; cursor: default;
  grid-column: 3; }"""
b = """.h2hface.right { flex-direction: row-reverse; text-align: right; cursor: default;
  grid-column: 5; }"""
assert s.count(a) == 1
io.open(p, "w", encoding="utf-8").write(s.replace(a, b))
print("ok")
