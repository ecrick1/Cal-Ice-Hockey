# -*- coding: utf-8 -*-
"""The penalty band becomes a scoreboard: each bench's box on its own side.

The penalties were a single row of pills reading left to right in the order
they were called, each one carrying the opponent's name as a prefix to say
whose it was. So working out who was short meant reading every chip and
picking the prefixes out, at exactly the moment - a scramble, two calls, a
clock stopped - when there is no time to read anything.

They sit where the scoreboard above already puts the two teams: ours on the
left, theirs on the right, strength in the middle. That is the arrangement
every rink board in the country uses for the same reason, and the console
had it two inches higher up for the score and shots already.

Stacked when there is more than one, newest at the bottom, so a second call
against the same bench is a second line under the first rather than a chip
somewhere along a row. Which side is carrying two is then the shape of the
thing rather than something to be counted.

The prefix goes with it. A chip on their side is theirs, and repeating the
opponent's name on every one of them was the flat row's problem restated.
Ejections keep their place on the side of the bench that lost the player.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------------------------- the band
sub("""      <div className={"austrength " + strength.kind.toLowerCase()}>
        <span className="austrengthtag">
          {strength.kind === "EV" ? "Even strength"
            : strength.kind === "E4" ? strength.label
            : strength.kind + " " + strength.label}
        </span>
        {live.delayed && (
          <span className="audelaytag">
            Delayed penalty · {live.delayed === "us" ? usLabel : oppName || "Them"}
          </span>
        )}
        {live.goalieUs === "empty" && (
          <span className="auemptytag">{usLabel} net empty</span>
        )}
        {live.goalieThem === "Empty net" && (
          <span className="auemptytag">{oppName || "Them"} net empty</span>
        )}
        {strength.active.map((p) => (
          <button className={"aupen " + (p.shorts ? "" : "aupenfull")} key={p.id}
            onClick={() => endPenalty(p.id)}
            title={p.shorts
              ? "End this penalty early"
              : "Served by the player — the team is not short. End it early"}>
            {p.team === "us" ? "" : oppName + " · "}{p.player} {fmtClock(p.left * 1000)}
            {p.halfServed && <span className="aupennote">2nd half</span>}
            {!p.shorts && <span className="aupennote">no advantage</span>}
            {" ✕"}
          </button>
        ))}
        {ejected.map((e, i) => (
          <span className="aupen aupenout" key={"ej" + i}>
            {e.team === "us" ? "" : oppName + " · "}{e.name}
            <span className="aupennote">ejected</span>
          </span>
        ))}
        {!strength.active.length && !ejected.length && (
          <span className="bsm" style={{ color: "var(--au-faint)" }}>No penalties being served.</span>
        )}
      </div>""",
    """      {(() => {
        /* Each bench's box on its own side, the way the scoreboard two inches
           above already arranges the same two teams. A chip on the right is
           theirs, so it does not have to say so. */
        const boxFor = (side) => (
          <div className={"aupenbox " + side}>
            {strength.active.filter((p) => p.team === side).map((p) => (
              <button className={"aupen " + (p.shorts ? "" : "aupenfull")} key={p.id}
                onClick={() => endPenalty(p.id)}
                title={p.shorts
                  ? "End this penalty early"
                  : "Served by the player — the team is not short. End it early"}>
                {p.player} {fmtClock(p.left * 1000)}
                {p.halfServed && <span className="aupennote">2nd half</span>}
                {!p.shorts && <span className="aupennote">no advantage</span>}
                {" ✕"}
              </button>
            ))}
            {ejected.filter((e) => e.team === side).map((e, i) => (
              <span className="aupen aupenout" key={"ej" + i}>
                {e.name}
                <span className="aupennote">ejected</span>
              </span>
            ))}
          </div>
        );
        const nothing = !strength.active.length && !ejected.length;
        return (
          <div className={"austrength " + strength.kind.toLowerCase()}>
            {boxFor("us")}
            <div className="aupenmid">
              <span className="austrengthtag">
                {strength.kind === "EV" ? "Even strength"
                  : strength.kind === "E4" ? strength.label
                  : strength.kind + " " + strength.label}
              </span>
              {live.delayed && (
                <span className="audelaytag">
                  Delayed · {live.delayed === "us" ? usLabel : oppName || "Them"}
                </span>
              )}
              {live.goalieUs === "empty" && (
                <span className="auemptytag">{usLabel} net empty</span>
              )}
              {live.goalieThem === "Empty net" && (
                <span className="auemptytag">{oppName || "Them"} net empty</span>
              )}
              {nothing && (
                <span className="bsm" style={{ color: "var(--au-faint)" }}>
                  No penalties being served.
                </span>
              )}
            </div>
            {boxFor("them")}
          </div>
        );
      })()}""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .austrength { display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  border: 1px solid var(--au-line); border-radius: 10px; padding: 10px 14px;
  background: var(--au-panel); }""",
    """/* Ours, the strength, theirs - the same three across as the scoreboard
   above it, so which bench is short is the shape rather than a read. */
.adminui .austrength { display: grid; grid-template-columns: 1fr auto 1fr;
  align-items: center; gap: 10px 14px;
  border: 1px solid var(--au-line); border-radius: 10px; padding: 10px 14px;
  background: var(--au-panel); }
/* Stacked, because a second call against one bench is a second line under
   the first and not a chip further along a row. */
.adminui .aupenbox { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.adminui .aupenbox.us { align-items: flex-start; }
.adminui .aupenbox.them { align-items: flex-end; }
.adminui .aupenmid { display: flex; flex-direction: column; align-items: center; gap: 6px;
  text-align: center; }
/* Narrow: the three columns become three rows and the sides square up,
   because two chips pushed to opposite edges of a phone read as unrelated. */
@media (max-width: 720px) {
  .adminui .austrength { grid-template-columns: 1fr; }
  .adminui .aupenbox.us, .adminui .aupenbox.them { align-items: center; }
  .adminui .aupenbox:empty { display: none; }
}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('each bench has its own box')
