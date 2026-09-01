# -*- coding: utf-8 -*-
"""Hand pass and high stick, a reason you can type, and no strength until it settles.

Three things about the whistle.

Two reasons were missing. A hand pass and a high stick are ordinary
stoppages that were being filed under "Other", which tells a reader nothing
and puts two different things in one bucket.

And "Other" is now a box you can type in, because a list of nine reasons
will never be the list of every reason. What is typed becomes the reason on
the play and the words on the band, so an unusual whistle reads as what it
was rather than as "Other".

The third is the one that was actually wrong. Penalties at one whistle go in
one at a time, and the strength was recomputed and published after each: two
coincidental minors meant the site announced a Cal power play, then a USC
power play, then 4-on-4, in the seconds it took to type the second name. The
first two were never true. Nobody watching wants the console's typing speed
broadcast to them.

So while a whistle is being sorted out, the strength holds. The penalties
are still recorded the moment they are entered - the data is right - but the
readout says a penalty is being assessed instead of naming a count that is
about to change. It settles when the whistle does: Done, or play restarting.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ================================================================ reasons
sub("""const STOP_REASONS = [
  "Goal", "Penalty", "Icing", "Offside", "Puck out of play", "Goalie freeze",
  "Injury", "Net off moorings", "Other",
];""",
    """const STOP_REASONS = [
  "Goal", "Penalty", "Icing", "Offside", "Hand pass", "High stick",
  "Puck out of play", "Goalie freeze", "Injury", "Net off moorings",
];""")

# ====================================== the strength holds while it settles
sub("""function strengthState(live, now) {
  const active = activePenalties(live, now);
  const serving = active.filter((p) => p.shorts);""",
    """/* A whistle whose penalties are still being entered.
 *
 * They go in one at a time, so between the first name and the second the
 * count is a real number that is about to be wrong: two coincidental minors
 * read as a power play until the second one lands. Held rather than
 * published, because the alternative is broadcasting how fast somebody
 * types. */
const assessing = (live) => !!(live && live.assessing);

function strengthState(live, now) {
  const active = activePenalties(live, now);
  const serving = active.filter((p) => p.shorts);""")

# --------------------------------------------------------- the public tag
sub("""function StrengthTag({ live, now, usAbbr, size }) {
  if (!live) return null;
  const st = strengthState(live, now);
  if (st.kind === "EV") return null;""",
    """function StrengthTag({ live, now, usAbbr, size }) {
  if (!live) return null;
  /* A count that is about to change is worse than no count. */
  if (assessing(live)) {
    return (
      <span className={"strtag pending" + (size === "sm" ? " sm" : "")}>
        <span className="strtaglab">Penalty pending</span>
      </span>
    );
  }
  const st = strengthState(live, now);
  if (st.kind === "EV") return null;""")

sub("""/* Even and a man down each. Not a power play for anyone, so not the gold,
   and too much of an event to wear the kill's outline. */
.strtag.ev4 { background: #EEF0FB; color: #3B3F7A; box-shadow: inset 0 0 0 1px #C9CDEC; }""",
    """/* Even and a man down each. Not a power play for anyone, so not the gold,
   and too much of an event to wear the kill's outline. */
.strtag.ev4 { background: #EEF0FB; color: #3B3F7A; box-shadow: inset 0 0 0 1px #C9CDEC; }
/* Still being sorted out at the whistle: not a strength, a wait. */
.strtag.pending { background: #FDF3E2; color: #7A5A17; box-shadow: inset 0 0 0 1px #EBD9B4; }
.sboard .strtag.pending { background: #FDF3E2; color: #7A5A17; box-shadow: inset 0 0 0 1px #EBD9B4; }""")

# ------------------------------------------------------- the console band
sub("""              <span className="austrengthtag">
                {strength.kind === "EV" ? "Even strength"
                  : strength.kind === "E4" ? strength.label
                  : strength.kind + " " + strength.label}
              </span>""",
    """              <span className="austrengthtag">
                {live.assessing ? "Penalty pending"
                  : strength.kind === "EV" ? "Even strength"
                  : strength.kind === "E4" ? strength.label
                  : strength.kind + " " + strength.label}
              </span>""")

# ------------------------------------------- set it, and clear it with the bar
sub("""  const holdForPenalty = () => {
    setStopAsk(false);
    setPenPending({ period: curPeriod, clock: fmtClock(left) });
  };""",
    """  const holdForPenalty = () => {
    setStopAsk(false);
    setPenPending({ period: curPeriod, clock: fmtClock(left) });
    /* On the game, not just in this console: the public strength tag reads
       the same flag, and it is the one being spared the guesswork. */
    setLive({ assessing: true });
  };

  /* The whistle is settled - everything that was called has been entered. */
  const doneAssessing = () => {
    setPenPending(null);
    if (live.assessing) setLive({ assessing: false });
  };""")

sub("""    setStopAsk(false);
    setOpenForm(null);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);""",
    """    setStopAsk(false);
    setOpenForm(null);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('reasons added; strength waits for the whistle to settle')
