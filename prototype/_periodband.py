# -*- coding: utf-8 -*-
"""A period starting or ending is a band, like every other whistle.

The stoppages became bands across the sheet because play stopping is not
something either team did. A period beginning or ending is the same kind of
fact and was still being listed as a play: a time, an icon sitting in the
crest's column, a bold heading and a line of description underneath, in the
shape used for a goal.

It takes the same band now - full width, centred, the whistle above the
words - so the sheet has one shape for "the clock did something" and another
for "a player did something", and the eye can sort them without reading.

The wording is the sentence that used to sit underneath as the description.
"1st period under way" says what "Period Start / 1st period under way" said
in two lines and one heading, and the band has no room for a heading and a
description that repeat each other.

The dead branches that used to build that heading and description come out
with it; every period play now takes the band before it reaches them.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""                  if (x.kind === "stoppage") {
                    return (
                      <div className="pbstop" key={x.id}>
                        <span className="pbstopicon" aria-hidden="true"><IcWhistle size={20} /></span>
                        <span className="pbstoplab">{x.reason || "Play stopped"}</span>
                      </div>
                    );
                  }""",
    """                  /* The clock doing something, rather than a player: a whistle,
                     or a period beginning or ending. All of it gets the width of
                     the sheet and nothing but the words, so the eye can sort the
                     two kinds apart without reading either. */
                  if (x.kind === "stoppage" || x.kind === "period") {
                    const said = x.kind === "stoppage"
                      ? (x.reason || "Play stopped")
                      : (PERIOD_LABEL[x.period] || x.period)
                        /* "1st period over", but just "OT over" - there is only
                           ever one, so the noun adds nothing. */
                        + (x.period === "OT" || x.period === "SO" ? " " : " period ")
                        + (x.phase === "start" ? "under way" : "over");
                    return (
                      <div className="pbstop" key={x.id}>
                        <span className="pbstopicon" aria-hidden="true"><IcWhistle size={20} /></span>
                        <span className="pbstoplab">{said}</span>
                      </div>
                    );
                  }""")

# The heading and description they used to use are unreachable now.
sub("""                    : x.kind === "period" ? (x.phase === "start" ? "Period Start" : "Period End")
""", "")

sub("""                    : x.kind === "period"
                      ? (PERIOD_LABEL[x.period] || x.period)
                        /* "1st period over", but just "OT over" - there is
                           only ever one, so the noun adds nothing. */
                        + (x.period === "OT" || x.period === "SO" ? " " : " period ")
                        + (x.phase === "start" ? "under way" : "over")
""", "")

io.open(p, 'w', encoding='utf-8').write(s)
print('a period is a band too')
