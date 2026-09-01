# -*- coding: utf-8 -*-
"""The sortable headings explain themselves too, and the dead glossary goes.

The stats page's headings are buttons, because clicking one sorts by it, and
their tooltip was already spoken for: "Sort by SHG" tells you what the click
does and nothing about what the letters mean, which is the question actually
being asked.

Both now. "Short-handed goals — click to sort" says what it is first, since
that is what someone hovering wants, and what the button does second.

And the glossary list itself comes out, along with the styles for the panel
that used to hold it. Its contents were moved out to where every table can
read them, and a copy left behind on one page would be the copy that goes
stale.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------- what it is, then what it does
sub("""                <button className={`sortbtn ${on ? "on" : ""}`} onClick={() => toggleSort(col)}
                  title={"Sort by " + col.label}>
                  {col.label}""",
    """                {/* What the letters mean first - that is what someone hovering
                    is asking - and what the click does after it. */}
                <button className={`sortbtn ${on ? "on" : ""}`} onClick={() => toggleSort(col)}
                  title={(statMeaning(col.label) || col.title || col.label)
                    + " — click to sort"}>
                  {col.label}""")

sub("""              <th key={col.key} title={col.title}
                aria-sort={on ? (gSortDir === "asc" ? "ascending" : "descending") : "none"}>
                <button className={`sortbtn ${on ? "on" : ""}`}
                  onClick={() => {""",
    """              <th key={col.key}
                title={(statMeaning(col.label) || col.title || col.label) + " — click to sort"}
                aria-sort={on ? (gSortDir === "asc" ? "ascending" : "descending") : "none"}>
                <button className={`sortbtn ${on ? "on" : ""}`}
                  onClick={() => {""")

# ------------------------------------------------------------ the list goes
sub("""  const GLOSSARY = [
    /* Skaters */
    ["GP", "Games played"],
    ["G", "Goals"],
    ["A", "Assists"],
    ["PTS", "Points (G + A)"],
    ["S", "Shots"],
    ["PIM", "Penalty minutes"],
    ["PPG", "Power play goals"],
    ["SHG", "Short handed goals"],
    ["SOG", "Shootout goals"],
    ["GWG", "Game winning goals"],
    ["TG", "Tying goals"],
    /* Goaltenders */
    ["W-L-T", "Wins, losses, ties"],
    ["GA", "Goals against"],
    ["SV", "Saves"],
    ["SV%", "Save percentage"],
    ["GAA", "Goals against average"],
    ["SO", "Shutouts"],
    /* Game by game */
    ["GF", "Goals for"],
    ["SHA", "Shots against"],
  ];

""", "")

# ------------------------------------------------------------------- CSS
sub(""".glosswrap { margin-top: 22px; border-top: 1px solid var(--border); padding-top: 18px; }
.glossbar { display: inline-flex; align-items: center; gap: 8px; background: none; border: 0;""",
    """/* A heading that will explain itself if you hover it, and says so with the
   underline that means exactly that everywhere else on the web. */
.statabbr[title] { text-decoration: underline dotted var(--border); text-underline-offset: 3px;
  cursor: help; }
.sortbtn[title] { cursor: pointer; }

.glossbar { display: inline-flex; align-items: center; gap: 8px; background: none; border: 0;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('sortable headings explain themselves; glossary removed')
