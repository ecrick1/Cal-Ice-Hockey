# -*- coding: utf-8 -*-
"""Styles for the redesigned preview: the comparison bar carrying two faces,
and goaltender cards with headshots."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

OLD_START = "/* The preview's wide sections. NHL-style: our side on the left, theirs on"
OLD_END = "/* Two columns of numbers with the label between them, so the eye compares"

i = s.index(OLD_START)
j = s.index(OLD_END)
assert i < j

NEW = """/* Players to watch rides the Game stats bar: same grid, same slanted meeting
   of the two team colours, with a face at each end above it. */
.h2hbar { grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); }
.h2hbar .gcbarlab { grid-row: 1; grid-column: 2; align-self: center; }
.h2hbar .gcbarval { grid-row: 2; grid-column: 1; }
.h2hbar .gcbarval.right { grid-row: 2; grid-column: 3; }
.h2hbar .gcbartrack { grid-row: 3; margin-top: 6px; }
.h2hface { display: flex; align-items: center; gap: 9px; background: none; border: 0;
  padding: 0; cursor: pointer; text-align: left; min-width: 0; grid-row: 1; }
.h2hface.right { flex-direction: row-reverse; text-align: right; cursor: default;
  grid-column: 3; }
.h2hface.right .h2hnames { align-items: flex-end; }
.h2hmark { width: 38px; height: 38px; object-fit: contain; flex: 0 0 auto; }
.h2hnames { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.h2hname { font-weight: 800; font-size: 13.5px; color: var(--ink); line-height: 1.25;
  overflow: hidden; text-overflow: ellipsis; }
button.h2hface:hover .h2hname { color: var(--blue); }
.h2hname.unknown { color: var(--muted); font-weight: 700; }
.h2hpos { font-size: 11px; font-weight: 600; color: var(--muted); white-space: nowrap; }
.gpseason { margin: -4px 0 16px; }
.gpnote { margin-top: 14px; }

/* Goaltending, one block a side, faces on the cards. */
.gtgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.gtside { min-width: 0; }
.gtteamline { padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.gtline { display: flex; flex-wrap: wrap; gap: 4px 14px; }
.gtline span { display: flex; flex-direction: column; font-size: 10px; font-weight: 700;
  color: var(--muted); }
.gtline strong { font-family: var(--body); font-weight: 800; font-size: 17px; color: var(--ink);
  line-height: 1.15; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.gtcard { display: block; width: 100%; text-align: left; margin-top: 12px; padding: 12px;
  border: 1px solid var(--border); border-radius: 10px; background: #fff; cursor: pointer; }
div.gtcard { cursor: default; }
button.gtcard:hover { border-color: var(--blue); }
.gthead { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; min-width: 0; }
.gtmark { width: 42px; height: 42px; object-fit: contain; flex: 0 0 auto; }
.gtnames { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.gtname { font-weight: 800; font-size: 14px; color: var(--ink); line-height: 1.2;
  overflow: hidden; text-overflow: ellipsis; }
.gtnum { font-size: 11px; font-weight: 700; color: var(--muted); }

@media (max-width: 900px) {
  .gtgrid { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  /* Two faces will not fit either side of a label, so the bar keeps the
     numbers and the names move under it. */
  .h2hbar .h2hface { grid-row: auto; }
  .h2hbar .h2hface.right { grid-column: 3; }
  .h2hmark, .h2hface .ppavatar { display: none; }
  .h2hname { font-size: 12.5px; }
  .h2hpos { white-space: normal; }
}

"""
s = s[:i] + NEW + s[j:]
io.open(p, 'w', encoding='utf-8').write(s)
print('css replaced')
