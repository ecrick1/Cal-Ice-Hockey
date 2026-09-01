# -*- coding: utf-8 -*-
"""Say that play is stopped, and ask who shot it.

A frozen clock and a running one look identical from outside. Somebody
watching the scoreboard sees "2nd - 12:34" and cannot tell whether that is
the game or a photograph of it, and a clock that has not moved for two
minutes reads as a broken page rather than a whistle. So a whistle mark sits
beside the time whenever play is stopped and the period is still on: not an
intermission, which says so already, and not the warm-up, which has no clock
to stop.

One helper decides it, because the three places that show a live clock -
the strip, the home banner and the game page - had three copies of the
same condition waiting to happen.

And the save prompt asks who shot it. It was logging the shot with the
goaltender credited and the shooter blank, which is a save with nobody
taking it. The list is the shooting bench, already known from which
goaltender froze it, and there is still a button for the times nobody saw.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the helper
sub("""/* "2nd · 12:34", or "End 2nd" during an intermission. */
function liveLabel(live, now) {""",
    """/**
 * Is the clock stopped mid-period?
 *
 * An intermission and the warm-up both say what they are, so neither counts:
 * this is the whistle in the middle of play, which is the state a frozen
 * clock cannot tell you about on its own.
 */
function atWhistle(live) {
  return !!(live && !live.running && !live.intermission && !live.warmup);
}

/* "2nd · 12:34", or "End 2nd" during an intermission. */
function liveLabel(live, now) {""")

# ------------------------------------------------------- the three surfaces
sub("""                          <span className="livedot" aria-hidden="true" />LIVE · {liveLabel(g.live, tick)}
                          <StrengthTag live={g.live} now={tick} size="sm" />""",
    """                          <span className="livedot" aria-hidden="true" />LIVE · {liveLabel(g.live, tick)}
                          {atWhistle(g.live) && (
                            <span className="whistlemark" title="Play stopped">
                              <IcWhistle size={13} />
                            </span>
                          )}
                          <StrengthTag live={g.live} now={tick} size="sm" />""")

sub("""                  <span className="gcwhen">{liveLabel(game.live, now)}</span>
                  <StrengthTag live={game.live} now={now} usAbbr={usAbbr} />""",
    """                  <span className="gcwhen">
                    {liveLabel(game.live, now)}
                    {atWhistle(game.live) && (
                      <span className="whistlemark" title="Play stopped">
                        <IcWhistle size={15} />
                      </span>
                    )}
                  </span>
                  <StrengthTag live={game.live} now={now} usAbbr={usAbbr} />""")

sub("""                        <span className="livedot" aria-hidden="true" />Live · {liveLabel(feature.live, tick)}""",
    """                        <span className="livedot" aria-hidden="true" />Live · {liveLabel(feature.live, tick)}
                        {atWhistle(feature.live) && (
                          <span className="whistlemark" title="Play stopped">
                            <IcWhistle size={14} />
                          </span>
                        )}""")

# ------------------------------------------------------------------- CSS
sub(""".livedot { display: inline-block; width: 7px; height: 7px; border-radius: 50%;""",
    """/* Play is stopped. Quieter than the live dot beside it - it qualifies that
   dot rather than competing with it. */
.whistlemark { display: inline-flex; align-items: center; margin-left: 6px;
  vertical-align: -2px; opacity: 0.7; }
.livedot { display: inline-block; width: 7px; height: 7px; border-radius: 50%;""")

# ==================================================== who shot it, on a save
sub("""  const logSaveShot = () => {
    const { freezeId, shooter, keeper, period, clock } = saveAsk;
    const shot = {
      id: uid(), kind: "shot", team: shooter,
      period, clock, goalie: keeper || "",
    };""",
    """  const logSaveShot = (value) => {
    const { freezeId, shooter, keeper, period, clock } = saveAsk;
    const us = shooter === "us";
    const shot = {
      id: uid(), kind: "shot", team: shooter,
      period, clock, goalie: keeper || "",
      shooterId: us ? value || null : null,
      shooter: us ? nameOf(value) : value || "",
    };""")

sub("""      {saveAsk && (
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
      )}""",
    """      {saveAsk && (
        <div className="austop">
          <span className="h6">Was it a save? Who shot it?</span>
          {/* Which goaltender froze it settles which bench shot, so only one
              list is offered. */}
          {saveAsk.shooter === "us" ? (
            <select value="" onChange={(e) => logSaveShot(e.target.value)}>
              <option value="">{usLabel} — pick a player</option>
              {skaters.filter((p) => p.position !== "G").map((p) => (
                <option key={p.id} value={p.id}>#{p.number} {p.name}</option>
              ))}
            </select>
          ) : theirs.length ? (
            <select value="" onChange={(e) => logSaveShot(e.target.value)}>
              <option value="">{oppName || "Them"} — pick a player</option>
              {theirs.map((p) => (
                <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
              ))}
            </select>
          ) : (
            <input placeholder={(oppName || "Their") + " shooter"} onKeyDown={(e) => {
              if (e.key === "Enter") logSaveShot(e.currentTarget.value.trim());
            }} />
          )}
          <button className="btn bGhost bSm" onClick={() => logSaveShot("")}>
            Count it — shooter unknown
          </button>
          <button className="btn bGhost bSm austopskip" onClick={() => setSaveAsk(null)}>
            Not a save
          </button>
        </div>
      )}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('whistle mark and the shooter on a save')
