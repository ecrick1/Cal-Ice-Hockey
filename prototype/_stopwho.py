# -*- coding: utf-8 -*-
"""After the whistle, ask who.

The console already asked why play stopped. Icing, offside, a puck over the
glass and a goaltender freezing it are all things a particular player did,
and the reason on its own leaves the play-by-play saying that something
happened to nobody.

It asks in the same shape as the shot and faceoff prompts: the reason is
logged first so the stoppage is on the sheet whatever happens next, and the
name is attached to it a moment later. Skipping is one press and leaves a
stoppage with a reason and no name, which is what it was before.

The question is worded for the reason - who iced it, who was offside, who
is hurt - because "who did it" is wrong for half of them, and a wrongly
worded question gets a wrong answer at a rink.

Both benches are offered, and goaltenders are in the list: a freeze is the
one stoppage that is almost always theirs.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------- the question asked
sub("""const STOP_REASONS = [
  "Icing", "Offside", "Penalty", "Puck out of play", "Goalie freeze",
  "Injury", "Net off moorings", "Other",
];""",
    """const STOP_REASONS = [
  "Icing", "Offside", "Penalty", "Puck out of play", "Goalie freeze",
  "Injury", "Net off moorings", "Other",
];

/* Who the whistle was about. "Who did it" is wrong for half of these, and a
   question worded wrongly gets answered wrongly at a rink. */
const STOP_WHO = {
  "Icing": "Who iced it?",
  "Offside": "Who was offside?",
  "Penalty": "Who took the penalty?",
  "Puck out of play": "Who put it out?",
  "Goalie freeze": "Who froze it?",
  "Injury": "Who is hurt?",
  "Net off moorings": "Who knocked the net off?",
};""")

# ------------------------------------------------------------- the sequence
sub("""  const logStop = (reason) => {
    push({
      plays: [...plays, {
        id: uid(), kind: "stoppage", reason,
        period: curPeriod, clock: fmtClock(left),
      }],
    });
    setStopAsk(false);
  };""",
    """  /* The reason is written first so the stoppage is on the sheet whatever
     happens next, and the name is attached to that same play a moment
     later - the shot and faceoff prompts work the same way. */
  const [stopWho, setStopWho] = useState(null);

  const logStop = (reason) => {
    const pid = uid();
    push({
      plays: [...plays, {
        id: pid, kind: "stoppage", reason,
        period: curPeriod, clock: fmtClock(left),
      }],
    });
    setStopAsk(false);
    setStopWho({ id: pid, reason });
  };

  const nameStopper = (team, value) => {
    const us = team === "us";
    push({
      plays: plays.map((p) => (p.id === stopWho.id ? {
        ...p, byTeam: team,
        byId: us ? value || null : null,
        by: us ? nameOf(value) : value,
      } : p)),
    });
    setStopWho(null);
  };""")

# ------------------------------------------------------------------ the bar
sub("""      {stopAsk && (
        <div className="austop">
          <span className="h6">Why did play stop?</span>
          {STOP_REASONS.map((r) => (
            <button className="btn bGhost bSm" key={r} onClick={() => logStop(r)}>{r}</button>
          ))}
          <button className="btn bGhost bSm austopskip" onClick={() => setStopAsk(false)}>
            Don't log it
          </button>
        </div>
      )}""",
    """      {stopAsk && (
        <div className="austop">
          <span className="h6">Why did play stop?</span>
          {STOP_REASONS.map((r) => (
            <button className="btn bGhost bSm" key={r} onClick={() => logStop(r)}>{r}</button>
          ))}
          <button className="btn bGhost bSm austopskip" onClick={() => setStopAsk(false)}>
            Don't log it
          </button>
        </div>
      )}

      {stopWho && (
        <div className="austop">
          <span className="h6">{STOP_WHO[stopWho.reason] || "Who did it?"}</span>
          {/* Goaltenders included: a freeze is the one stoppage that is
              nearly always theirs. */}
          <select value="" onChange={(e) => nameStopper("us", e.target.value)}>
            <option value="">{usLabel} — pick a player</option>
            {skaters.map((p) => (
              <option key={p.id} value={p.id}>#{p.number} {p.name}</option>
            ))}
          </select>
          {theirs.length ? (
            <select value="" onChange={(e) => nameStopper("them", e.target.value)}>
              <option value="">{oppName || "Them"} — pick a player</option>
              {theirs.map((p) => (
                <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
              ))}
            </select>
          ) : (
            <input placeholder={(oppName || "Their") + " player"} onKeyDown={(e) => {
              if (e.key === "Enter") nameStopper("them", e.currentTarget.value.trim());
            }} />
          )}
          <button className="btn bGhost bSm austopskip" onClick={() => setStopWho(null)}>
            Don't know
          </button>
        </div>
      )}""")

# ------------------------------------------------- reading it back later
sub("""                    ) : (
                      <>
                        <span className="auplaykind stop">WHISTLE</span>
                        <span className="auplaywho">{p.reason || "Stoppage"}</span>
                      </>
                    )}""",
    """                    ) : (
                      <>
                        <span className="auplaykind stop">WHISTLE</span>
                        <span className="auplaywho">{p.reason || "Stoppage"}</span>
                        {p.by && <span className="auplayassist">{p.by}</span>}
                      </>
                    )}""", 2)

io.open(p, 'w', encoding='utf-8').write(s)
print('stoppage now asks who')
