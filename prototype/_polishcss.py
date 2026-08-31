# -*- coding: utf-8 -*-
"""Styles for the stacked goaltending list, the split names and the centred
watch/tickets row."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

START = "/* Goaltending, one block a side, faces on the cards. */"
END = "@media (max-width: 900px) {"
i = s.index(START)
j = s.index(END, i)

NEW = """/* Goaltending: a band of team totals, then that team's keepers under it,
   then the visitors the same way. One column, so the two blocks are read in
   order rather than compared cell by cell - the comparison is the bars
   above. */
.gtblock + .gtblock { margin-top: 22px; }
.gtband, .gtrow { display: grid; grid-template-columns: minmax(0, 1fr) repeat(4, minmax(52px, 74px));
  align-items: center; gap: 10px; }
.gtband { background: var(--ice); border-radius: 10px; padding: 12px 16px; }
.gtbandmark { display: flex; align-items: center; }
.gtbandmark img { height: 30px; width: auto; max-width: 46px; object-fit: contain; display: block; }
.gtrow { width: 100%; text-align: left; background: none; border: 0;
  border-bottom: 1px solid var(--border); padding: 12px 16px; }
.gtrow:last-child { border-bottom: 0; }
button.gtrow { cursor: pointer; }
button.gtrow:hover { background: var(--page); }
.gtwho { display: flex; align-items: center; gap: 12px; min-width: 0; }
.gtmark { width: 44px; height: 44px; object-fit: contain; flex: 0 0 auto; }
.gtnames { display: flex; flex-direction: column; min-width: 0; line-height: 1.15; }
/* Given name light, surname bold under it - a team sheet, not a sentence. */
.gtfirst { font-size: 12.5px; font-weight: 500; color: var(--muted); }
.gtlast { font-size: 15px; font-weight: 800; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; }
.gtnum { font-size: 11px; font-weight: 600; color: var(--muted); margin-top: 2px; }
.gtstat { display: flex; flex-direction: column; align-items: center; text-align: center; }
.gtstat strong { font-family: var(--body); font-weight: 800; font-size: 17px; color: var(--ink);
  letter-spacing: -0.02em; line-height: 1.15; font-variant-numeric: tabular-nums; }
.gtband .gtstat strong { font-size: 19px; }
.gtstatlab { font-size: 10px; font-weight: 700; color: var(--muted); margin-top: 2px; }

@media (max-width: 900px) {"""

s = s[:i] + NEW + s[j + len(END):]

# The old two-column grid rule is gone with the block above; drop what is left
# of it in the narrow breakpoint.
s = s.replace("""@media (max-width: 900px) {
  .gtgrid { grid-template-columns: 1fr; }
}
""", """@media (max-width: 620px) {
  /* Four stat columns will not fit beside a name, so the name takes the row
     and the numbers sit under it. */
  .gtband, .gtrow { grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .gtwho, .gtbandmark { grid-column: 1 / -1; }
  .gtrow { padding: 12px 4px; }
  .gtband { padding: 12px; }
}
""")

# Players to watch: same split, and the centred CTA row.
s = s.replace(""".h2hname { font-weight: 800; font-size: 13.5px; color: var(--ink); line-height: 1.25;
  overflow: hidden; text-overflow: ellipsis; }""",
""".h2hname { display: flex; flex-direction: column; line-height: 1.2; min-width: 0; }
.h2hfirst { font-size: 12px; font-weight: 500; color: var(--muted); }
.h2hlast { font-size: 14.5px; font-weight: 800; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; }
.h2hface.right .h2hname { align-items: flex-end; }
.h2hname.unknown .h2hlast { color: var(--muted); font-weight: 700; }""")

s = s.replace("""button.h2hface:hover .h2hname { color: var(--blue); }
.h2hname.unknown { color: var(--muted); font-weight: 700; }""",
"""button.h2hface:hover .h2hlast { color: var(--blue); }""")

s = s.replace(""".gpbar { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 18px; }""",
"""/* Centred, with the same air above and below - the two things somebody
   reading a preview of a game that has not happened actually wants. */
.gpbar { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  padding: 20px 0; margin: 0; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('css done')
