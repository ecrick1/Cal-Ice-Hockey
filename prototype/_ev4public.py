# -*- coding: utf-8 -*-
"""Four-on-four, said out loud on the public side.

The strength tag on the front page, the scoreboard strip and the game page
all went quiet at even strength, which was the right call when even strength
meant five a side. It does not any more: a penalty each is 4-on-4 and the tag
now has a state for it, so it needs a colour that is neither the gold of a
power play nor the outline of a kill. Indigo, because it is neither.

And the play-by-play says what each call did to the ice - "4-on-4" beside a
matching pair, "5-on-3" beside the second of two - so a game read back in
March still says what a game watched in November said.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------------- the tag has a third state
sub(""".strtag.pk { background: transparent; color: var(--muted); box-shadow: inset 0 0 0 1px var(--border); }""",
    """.strtag.pk { background: transparent; color: var(--muted); box-shadow: inset 0 0 0 1px var(--border); }
/* Even and a man down each. Not a power play for anyone, so not the gold,
   and too much of an event to wear the kill's outline. */
.strtag.ev4 { background: #EEF0FB; color: #3B3F7A; box-shadow: inset 0 0 0 1px #C9CDEC; }""")

sub(""".sboard .strtag.pk { color: var(--muted); box-shadow: inset 0 0 0 1px var(--border); }""",
    """.sboard .strtag.pk { color: var(--muted); box-shadow: inset 0 0 0 1px var(--border); }
.sboard .strtag.ev4 { background: #EEF0FB; color: #3B3F7A; box-shadow: inset 0 0 0 1px #C9CDEC; }""")

# ------------------------------------------------------ and on the play list
sub("""                  const detail = x.kind === "penalty"
                    ? x.player + " — " + x.minutes + " minutes for " + x.infraction""",
    """                  const detail = x.kind === "penalty"
                    ? x.player + " — " + x.minutes + " minutes for " + x.infraction
                      + (x.strength ? " · " + x.strength : "")""")

io.open(p, 'w', encoding='utf-8').write(s)
print('four-on-four said out loud')
