# -*- coding: utf-8 -*-
"""Fix the stacked head-to-head row on a phone.

Five columns collapse to two, and the previous rule left the placement to
auto-flow: the label took the first row, then the cursor put our face and
number on row two but their number on row three and their face on row four,
so the visitor's figure floated a line above the name it belonged to.

Every cell is placed explicitly now - label, our line, their line, bar - and
the visiting block reads left-to-right like ours instead of mirroring, which
only made sense when the two sat opposite each other.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

OLD = """@media (max-width: 620px) {
  /* Two faces will not fit either side of a label, so the bar keeps the
     numbers and the names move under it. */
  .h2hbar { grid-template-columns: 1fr auto; gap: 4px 10px; }
  .h2hbar .h2hface { grid-row: auto; grid-column: 1; }
  .h2hbar .h2hface.right { grid-column: 1; }
  .h2hbar .gcbarlab { grid-column: 1 / -1; grid-row: 1; text-align: left;
    font-size: 12px; color: var(--ink); }
  .h2hnum, .h2hnum.right { grid-column: 2; text-align: right; font-size: 22px; }"""

NEW = """@media (max-width: 620px) {
  /* Two columns: who on the left, their figure on the right, one line a
     side. Placed by hand - auto-flow put the visitor's number a row above
     the name it belongs to. */
  .h2hbar { grid-template-columns: minmax(0, 1fr) auto; gap: 8px 12px;
    align-items: center; }
  .h2hbar > .gcbarlab { grid-area: 1 / 1 / 2 / 3; text-align: left;
    font-size: 12px; font-weight: 800; color: var(--ink); }
  .h2hbar > .h2hface { grid-area: 2 / 1 / 3 / 2; }
  .h2hbar > .h2hnum { grid-area: 2 / 2 / 3 / 3; }
  .h2hbar > .h2hface.right { grid-area: 3 / 1 / 4 / 2; }
  .h2hbar > .h2hnum.right { grid-area: 3 / 2 / 4 / 3; }
  .h2hbar > .gcbartrack { grid-area: 4 / 1 / 5 / 3; margin-top: 4px; }
  /* Mirroring the visitor's block only made sense opposite ours. */
  .h2hbar > .h2hface.right { flex-direction: row; text-align: left; }
  .h2hbar > .h2hface.right .h2hnames { align-items: flex-start; }
  .h2hnum, .h2hnum.right { text-align: right; font-size: 24px; }"""

assert s.count(OLD) == 1
s = s.replace(OLD, NEW)
io.open(p, 'w', encoding='utf-8').write(s)
print('mobile placement fixed')
