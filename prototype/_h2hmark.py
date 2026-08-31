# -*- coding: utf-8 -*-
"""Stacked, the two lines lost the one thing that said whose they were."""
import io
p = "../reference/cal-ice-hockey-app.jsx"
s = io.open(p, encoding="utf-8").read()
a = """  /* PlayerAvatar renders a bare img or svg and writes its own inline
     display, which a stylesheet rule cannot outrank - the same reason
     .ppshot has to shout at it. */
  .h2hmark, .h2hface > img, .h2hface > svg { display: none !important; }"""
b = """  /* Kept, small: with the two sides stacked rather than opposite, the
     crest is the only thing saying which line belongs to whom. */
  .h2hmark { width: 26px; height: 26px; }
  .h2hface > img, .h2hface > svg { width: 26px !important; height: 26px !important; }"""
assert s.count(a) == 1
io.open(p, "w", encoding="utf-8").write(s.replace(a, b))
print("ok")
