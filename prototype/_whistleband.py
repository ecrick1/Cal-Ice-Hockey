# -*- coding: utf-8 -*-
"""A whistle is a band across the sheet, not a row on it.

Play stopping is not a thing either team did, and it was being listed as
though it were: a time, an icon in the crest's column, a heading and a line
of description, in the same shape as a goal or a hit. That gave the least
eventful line on the sheet the most furniture, and four of them in a row
made a period look busy when nothing had happened in it.

So it takes the shape of what it is - a pause. Full width, a shade darker
than the rows either side, the whistle centred with the reason under it, and
nothing else: no time, no description, no name. Icing is icing. It reads as
the gap between plays rather than as one of them, which is what the eye
wants when it is scanning for the goals.

The reason keeps its own wording. Everything that stops play already says
what it was in two or three words - Goalie freeze, Icing, Offside, Puck out
of play - so the description under it was only ever those words again in a
sentence.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ the band
sub("""                  const title = x.kind === "penalty" ? "Penalty\"""",
    """                  /* A whistle is not a play. It gets the width of the sheet
                     and nothing but the reason, because everything that stops
                     play already says what it was in two words. */
                  if (x.kind === "stoppage") {
                    return (
                      <div className="pbstop" key={x.id}>
                        <span className="pbstopicon" aria-hidden="true"><IcWhistle size={20} /></span>
                        <span className="pbstoplab">{x.reason || "Play stopped"}</span>
                      </div>
                    );
                  }

                  const title = x.kind === "penalty" ? "Penalty\"""")

# The two stoppage branches are dead now; the fallbacks stay for old rows
# written before stoppages carried a kind of their own.
sub("""                    : x.kind === "timeout" ? abbr + " timeout"
                    : x.kind === "stoppage"
                      ? (x.reason || "Play stopped") + (x.by ? " — " + x.by : "")
                      : "Play stopped";""",
    """                    : x.kind === "timeout" ? abbr + " timeout"
                    : "Play stopped";""")

# ------------------------------------------------------------------- CSS
sub(""".pbstr { margin-left: 8px; font-size: 10.5px; font-weight: 800; letter-spacing: 0.06em;
  border: 1px solid currentColor; border-radius: 4px; padding: 1px 5px; vertical-align: middle; }""",
    """.pbstr { margin-left: 8px; font-size: 10.5px; font-weight: 800; letter-spacing: 0.06em;
  border: 1px solid currentColor; border-radius: 4px; padding: 1px 5px; vertical-align: middle; }
/* The whistle: the width of the sheet, a shade darker than the plays either
   side, and stacked so the icon reads before the word. It is the gap between
   plays rather than one of them, so it carries no time and no crest. */
.pbstop { display: grid; justify-items: center; gap: 4px; padding: 14px 16px;
  background: var(--ice); border-top: 1px solid var(--border); }
.gcplays > .pbstop:first-child { border-top: 0; }
.pbstopicon { display: grid; place-items: center; color: var(--muted); }
.pbstoplab { font-size: 13px; font-weight: 700; color: var(--muted); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('whistles are bands')
