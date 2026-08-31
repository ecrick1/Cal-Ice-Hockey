# -*- coding: utf-8 -*-
"""Two adjustments to the comparison rows.

Head to head: a record has no bar at all now, not even the neutral track.
There is nothing to divide between two hyphenated figures, and an empty rail
under them only asked the reader why it was there.

Players to watch: the two numbers move inboard, either side of the category
they belong to, and get set at size. Out at the edges they read as captions
under the faces; in the middle they read as the comparison.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# ------------------------------------------------- head to head: no rail
sub("""                <div className="gcbar" key={label}>
                  <span className="gcbarval">{a}</span>
                  <span className="gcbarlab">{label}</span>
                  <span className="gcbarval right">{b}</span>
                  <span className="gcbartrack">
                    {bar && Number.isFinite(x) && Number.isFinite(y) ? (
                      <>
                        <span className="gcbarfill left" style={{ width: pa + "%", background: usColor }} />
                        <span className="gcbarfill right" style={{ width: (100 - pa) + "%", background: themColor }} />
                      </>
                    ) : <span className="gcbarnone" />}
                  </span>
                </div>""",
    """                <div className={"gcbar" + (bar ? "" : " norail")} key={label}>
                  <span className="gcbarval">{a}</span>
                  <span className="gcbarlab">{label}</span>
                  <span className="gcbarval right">{b}</span>
                  {bar && Number.isFinite(x) && Number.isFinite(y) && (
                    <span className="gcbartrack">
                      <span className="gcbarfill left" style={{ width: pa + "%", background: usColor }} />
                      <span className="gcbarfill right" style={{ width: (100 - pa) + "%", background: themColor }} />
                    </span>
                  )}
                </div>""")

# ------------------------------ players to watch: numbers beside the label
sub("""              <span className="gcbarlab">{label}</span>
              <span className="h2hface right">""",
    """              <span className="h2hnum">{a}</span>
              <span className="gcbarlab">{label}</span>
              <span className="h2hnum right">{them == null ? "\\u2014" : them}</span>
              <span className="h2hface right">""")

sub("""              <span className="gcbarval">{a}</span>
              <span className="gcbarval right">{them == null ? "\\u2014" : them}</span>
              <span className="gcbartrack">""",
    """              <span className="gcbartrack">""")

# ------------------------------------------------------------------- CSS
sub(""".h2hbar { grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); }
.h2hbar .gcbarlab { grid-row: 1; grid-column: 2; align-self: center; }
.h2hbar .gcbarval { grid-row: 2; grid-column: 1; }
.h2hbar .gcbarval.right { grid-row: 2; grid-column: 3; }
.h2hbar .gcbartrack { grid-row: 3; margin-top: 6px; }""",
    """/* Face, number, category, number, face - the comparison reads inward to the
   middle rather than out at the two edges. */
.h2hbar { grid-template-columns: minmax(0, 1fr) auto minmax(74px, auto) auto minmax(0, 1fr);
  gap: 4px 14px; }
.h2hbar .gcbarlab { grid-column: 3; align-self: center; }
.h2hnum { font-family: var(--body); font-weight: 800; font-size: 28px; letter-spacing: -0.02em;
  color: var(--ink); font-variant-numeric: tabular-nums; line-height: 1; text-align: right; }
.h2hnum.right { text-align: left; }
.h2hbar .gcbartrack { grid-column: 1 / -1; margin-top: 10px; }
/* Nothing to divide, so no rail under it. */
.gcbar.norail { padding-bottom: 12px; }""")

sub("""  .h2hbar .h2hface { grid-row: auto; }
  .h2hbar .h2hface.right { grid-column: 3; }""",
    """  .h2hbar { grid-template-columns: 1fr auto; gap: 4px 10px; }
  .h2hbar .h2hface { grid-row: auto; grid-column: 1; }
  .h2hbar .h2hface.right { grid-column: 1; }
  .h2hbar .gcbarlab { grid-column: 1 / -1; grid-row: 1; text-align: left;
    font-size: 12px; color: var(--ink); }
  .h2hnum, .h2hnum.right { grid-column: 2; text-align: right; font-size: 22px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('bars adjusted')
