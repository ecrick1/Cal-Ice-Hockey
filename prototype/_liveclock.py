# -*- coding: utf-8 -*-
"""End of the 1st Period, the break says it is a break, and the clock stops shoving.

Three things about the same clock.

The play-by-play bands said "1st period over", which reads like a note
rather than a marker. "End of 1st Period" is what a scoresheet writes, and
"Start of 1st Period" opposite it. Overtime and the shootout get their own
words, because "End of OT Period" is not a thing anybody says.

The header said "End 2nd" during the break after the first, which was wrong
in two ways at once: the break is an intermission, and the period stored
during one is the period about to start, not the one just finished. It reads
"1st · Intermission · 14:02" now - the period that just ended, what is
happening, and how long is left of it.

And the clock stopped dragging everything after it sideways. It was plain
text in the middle of a line, so 10:00 becoming 9:59 pulled the whistle
mark, the strength tag and the score a character to the left, and again on
every tick. It sits in a fixed-width box with tabular figures now, so the
digits change and nothing moves.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# =========================================== what the header actually says
sub("""/* "2nd · 12:34", or "End 2nd" during an intermission. */
function liveLabel(live, now) {
  if (!live) return "";
  /* Before the first faceoff. The game is listed - the stream is up, the
     doors are open - but there is no clock to report yet. */
  if (live.warmup) return "Warm-up";
  const p = live.period || "1";
  const named = p === "1" ? "1st" : p === "2" ? "2nd" : p === "3" ? "3rd" : p;
  if (live.intermission && !live.running) {
    /* The one thing everyone in the building wants to know. Once it has run
       out it stops being news and the period is what matters again. */
    const bl = intermissionLeft(live, now);
    const head = p === "3" ? "End of regulation" : "End " + named;
    return bl > 0 ? head + " · " + fmtClock(bl) : head;
  }
  return named + " · " + fmtClock(clockLeft(live, now));
}""",
    """const PERIOD_ORDER = ["1", "2", "3", "OT", "SO"];
const periodName = (p) => (p === "1" ? "1st" : p === "2" ? "2nd" : p === "3" ? "3rd" : p);

/**
 * The header's two halves: what part of the game this is, and the clock.
 *
 * Kept apart so the clock can be given a box of its own. As one string it
 * was plain text in the middle of a line, and 10:00 becoming 9:59 pulled
 * everything after it a character to the left, every second.
 *
 * During a break the period stored is the one about to start, not the one
 * just finished - starting an intermission moves it on - so the name is
 * taken from the period before it. "1st \\u00b7 Intermission" is the break
 * after the first, which is what somebody reading it wants to know.
 */
function liveParts(live, now) {
  if (!live) return { head: "", clock: null };
  /* Before the first faceoff. The game is listed - the stream is up, the
     doors are open - but there is no clock to report yet. */
  if (live.warmup) return { head: "Warm-up", clock: null };
  const p = live.period || "1";
  if (live.intermission && !live.running) {
    const i = PERIOD_ORDER.indexOf(p);
    const done = i > 0 ? PERIOD_ORDER[i - 1] : p;
    const bl = intermissionLeft(live, now);
    return {
      head: periodName(done) + " \\u00b7 Intermission",
      clock: bl > 0 ? fmtClock(bl) : null,
    };
  }
  return { head: periodName(p), clock: fmtClock(clockLeft(live, now)) };
}

/* The same thing as one string, for anywhere that needs text rather than
   markup. */
function liveLabel(live, now) {
  const { head, clock } = liveParts(live, now);
  return clock ? head + " \\u00b7 " + clock : head;
}

/* The period and the clock, with the clock in a box of a fixed width so the
   digits can change without moving the badges and the score beside them. */
function LiveWhen({ live, now }) {
  const { head, clock } = liveParts(live, now);
  return (
    <>
      {head}
      {clock ? <>{" \\u00b7 "}<span className="liveclock">{clock}</span></> : null}
    </>
  );
}""")

# ------------------------------------------------- the three places it shows
sub("""<span className="livedot" aria-hidden="true" />LIVE · {liveLabel(g.live, tick)}""",
    """<span className="livedot" aria-hidden="true" />LIVE · <LiveWhen live={g.live} now={tick} />""")

sub("""                    {liveLabel(game.live, now)}""",
    """                    <LiveWhen live={game.live} now={now} />""")

sub("""<span className="livedot" aria-hidden="true" />Live · {liveLabel(feature.live, tick)}""",
    """<span className="livedot" aria-hidden="true" />Live · <LiveWhen live={feature.live} now={tick} />""")

# ============================================= what the bands say
sub("""                      : (PERIOD_LABEL[x.period] || x.period)
                        /* "1st period over", but just "OT over" - there is only
                           ever one, so the noun adds nothing. */
                        + (x.period === "OT" || x.period === "SO" ? " " : " period ")
                        + (x.phase === "start" ? "under way" : "over");""",
    """                      : periodMoment(x.period, x.phase);""")

sub("""const PERIOD_LABEL = { "1": "1st", "2": "2nd", "3": "3rd", OT: "OT", SO: "SO" };""",
    """const PERIOD_LABEL = { "1": "1st", "2": "2nd", "3": "3rd", OT: "OT", SO: "SO" };

/* What a scoresheet writes at the top and bottom of a period. Overtime and
   the shootout are named rather than numbered, because "End of OT Period" is
   not a thing anybody says. */
function periodMoment(period, phase) {
  const edge = phase === "start" ? "Start of " : "End of ";
  if (period === "OT") return edge + "Overtime";
  if (period === "SO") return edge + "the Shootout";
  return edge + (PERIOD_LABEL[period] || period) + " Period";
}""")

# ------------------------------------------------------------------- CSS
sub(""".livedot { display: inline-block; width: 7px; height: 7px; border-radius: 50%;""",
    """/* A box wide enough for the longest reading it will hold, so counting down
   changes the digits and moves nothing. Tabular figures because a 1 and a 7
   are not the same width otherwise, and the clock would still twitch. */
.liveclock { display: inline-block; min-width: 4.6ch; text-align: left;
  font-variant-numeric: tabular-nums; }

.livedot { display: inline-block; width: 7px; height: 7px; border-radius: 50%;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('end of period, intermission named, clock in a box')
