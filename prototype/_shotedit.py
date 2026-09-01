# -*- coding: utf-8 -*-
"""Correct who took a shot, and log the save that caused the whistle.

Two things.

A shot on goal could be corrected by time and by nothing else - the one
field on it that anyone gets wrong is who took it, and a miss already had
that picker while the shot it was copied from did not.

And a freeze is almost always a save. The console asked which goaltender
froze it and stopped there, leaving the shot that caused the whistle
uncounted. It now offers to log it, and puts it in front of the stoppage
rather than after, because that is the order it happened in: the shot, then
the whistle.

The shot goes on unattributed. Naming the shooter is a third question at a
whistle, and the correction bar - which is the other half of this change -
is a better place to answer it than the bench is.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# =============================================== correcting a shot's shooter
sub("""          {editPlay.kind === "miss" && (""",
    """          {(editPlay.kind === "shot" || editPlay.kind === "miss") && (""")

# =========================================================== the save prompt
sub("""  /* A whistle for a penalty, waiting for the penalty.""",
    """  /* A freeze the console is about to offer to count as a save. */
  const [saveAsk, setSaveAsk] = useState(null);

  /* A whistle for a penalty, waiting for the penalty.""")

sub("""  const nameStopper = (team, value) => {""",
    """  /* The shot that caused the whistle, put in front of the whistle - it is
     the order it happened in, and a shot logged after the stoppage reads as
     the next thing rather than the reason for this one. */
  const logSaveShot = () => {
    const { freezeId, shooter, keeper, period, clock } = saveAsk;
    const shot = {
      id: uid(), kind: "shot", team: shooter,
      period, clock, goalie: keeper || "",
    };
    const i = plays.findIndex((p) => p.id === freezeId);
    const next = i < 0
      ? [...plays, shot]
      : [...plays.slice(0, i), shot, ...plays.slice(i)];
    push({ plays: next, live: withShot(live, shooter, 1, period) });
    setSaveAsk(null);
  };

  const nameStopper = (team, value) => {""")

# The freeze buttons hand off to it.
sub("""          <button className="btn bGhost bSm"
            onClick={() => nameStopper("us", ourKeeperId)}>
            {usLabel}{ourKeeperName ? " — " + ourKeeperName : ""}
          </button>
          <button className="btn bGhost bSm"
            onClick={() => nameStopper("them", live.goalieThem || "")}>
            {oppName || "Them"}{live.goalieThem ? " — " + live.goalieThem : ""}
          </button>""",
    """          <button className="btn bGhost bSm"
            onClick={() => {
              const at = { period: stopWho.period, clock: stopWho.clock };
              nameStopper("us", ourKeeperId);
              /* Our goaltender froze it, so the shot was theirs. */
              setSaveAsk({ freezeId: stopWho.id, shooter: "them", keeper: ourKeeperName, ...at });
            }}>
            {usLabel}{ourKeeperName ? " — " + ourKeeperName : ""}
          </button>
          <button className="btn bGhost bSm"
            onClick={() => {
              const at = { period: stopWho.period, clock: stopWho.clock };
              nameStopper("them", live.goalieThem || "");
              setSaveAsk({ freezeId: stopWho.id, shooter: "us",
                keeper: live.goalieThem || "", ...at });
            }}>
            {oppName || "Them"}{live.goalieThem ? " — " + live.goalieThem : ""}
          </button>""")

# The prompt needs the time the whistle went, so it is carried on the hold.
sub("""    if (reason === "Goalie freeze") setStopWho({ id: pid, reason });""",
    """    if (reason === "Goalie freeze") {
      setStopWho({ id: pid, reason, period: curPeriod, clock: fmtClock(left) });
    }""")

# ------------------------------------------------------------------ the bar
sub("""      {penPending && (""",
    """      {saveAsk && (
        <div className="austop">
          <span className="h6">Was it a save?</span>
          <span className="bsm">
            The shot goes on the sheet ahead of the whistle, where it happened.
          </span>
          <button className="btn bGhost bSm" onClick={logSaveShot}>
            Yes — count the shot
          </button>
          <button className="btn bGhost bSm austopskip" onClick={() => setSaveAsk(null)}>
            No
          </button>
        </div>
      )}

      {penPending && (""")

# Play restarting clears it, like every other pending question.
sub("""    /* And a penalty whistle nobody filled in was not a penalty. */
    setPenPending(null);""",
    """    /* And a penalty whistle nobody filled in was not a penalty. */
    setPenPending(null);
    setSaveAsk(null);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('shot editing and the save prompt')
