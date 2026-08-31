# -*- coding: utf-8 -*-
"""The head-to-head row on a phone.

Five columns cannot survive 375px, and collapsing them to three put our
number where their player belongs. Stacked instead: the category over one
line a side, each name with its number at the end of its own row - which is
how the two sides stay legible when they cannot sit next to each other.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

OLD = """@media (max-width: 700px) {
  .h2hhead, .h2hrow { grid-template-columns: 1fr auto 1fr; }
  /* On a phone the two faces stack under the number they belong to. */
  .h2hhead span:nth-child(2) { display: none; }
  .h2hrow > .h2hplayer { grid-column: span 1; }
  .h2hrow .h2hcat { grid-column: 2; grid-row: 1; }
  .h2hnum { font-size: 22px; }
  .h2hmark, .h2hplayer .pcard-photo { display: none; }
  .gtgrid { grid-template-columns: 1fr; }
}"""

NEW = """@media (max-width: 700px) {
  .h2hhead { display: none; }
  .h2hrow { grid-template-columns: 1fr auto; gap: 6px 10px;
    grid-template-areas: "cat cat" "pus nus" "pthem nthem"; }
  .h2hrow > .h2hplayer:nth-child(1) { grid-area: pus; }
  .h2hrow > .h2hnum:nth-child(2) { grid-area: nus; }
  .h2hrow > .h2hcat { grid-area: cat; text-align: left; text-transform: none;
    font-size: 12px; color: var(--ink); }
  .h2hrow > .h2hnum:nth-child(4) { grid-area: nthem; }
  .h2hrow > .h2hplayer:nth-child(5) { grid-area: pthem; flex-direction: row;
    text-align: left; }
  .h2hrow > .h2hplayer:last-child .h2hnames { align-items: flex-start; }
  .h2hnum { font-size: 22px; align-self: center; }
  .h2hmark { width: 28px; height: 28px; }
  .h2hplayer .ppavatar, .h2hplayer svg.ppavatar { width: 28px; height: 28px; }
  .gtgrid { grid-template-columns: 1fr; }
}"""

assert s.count(OLD) == 1
s = s.replace(OLD, NEW)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
