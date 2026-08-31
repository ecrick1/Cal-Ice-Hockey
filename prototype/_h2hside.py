# -*- coding: utf-8 -*-
"""Stacked, the visiting crest should lead its line the way ours does."""
import io
p = "../reference/cal-ice-hockey-app.jsx"
s = io.open(p, encoding="utf-8").read()
a = """  /* Mirroring the visitor block only made sense opposite ours. */
  .h2hbar > .h2hface.right { flex-direction: row; text-align: left; }
  .h2hbar > .h2hface.right .h2hnames { align-items: flex-start; }"""
b = """  /* Mirroring the visitor block only made sense opposite ours. The mark
     comes after the name in the markup, so reversing puts it in front and
     flex-end packs the pair back to the left edge. */
  .h2hbar > .h2hface.right { flex-direction: row-reverse; justify-content: flex-end;
    text-align: left; }
  .h2hbar > .h2hface.right .h2hnames { align-items: flex-start; }"""
assert s.count(a) == 1, s.count(a)
io.open(p, "w", encoding="utf-8").write(s.replace(a, b))
print("ok")
