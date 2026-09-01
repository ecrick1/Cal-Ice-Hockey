# -*- coding: utf-8 -*-
"""Correct a draw properly, nudge the clock by a second, and drop the
stoppage question.

Four changes, three of them the same complaint: the console recorded things
it would not let you fix.

  Correcting a faceoff offered a period and a clock, which are the two
  things least likely to be wrong about it. What is wrong is who won it.
  So the edit bar now offers the side, and the winner within that side -
  including "team, no player", because that is a real answer here.

  A miss and a stoppage were editable only by time as well; a miss now
  takes its shooter and a stoppage its reason.

  The clock nudged by ten seconds and a minute. A puck that goes in with
  eight seconds showing is corrected by one second at a time, so plus and
  minus one are there now.

And the "who did it" prompt after every whistle comes out. It asked a
question nobody at a rink has time for, on every icing. The goalie-freeze
question stays: it was asked for separately, it is two buttons rather than
two rosters, and a freeze is the one whistle where the answer is already
known.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------- the generic stoppage prompt
sub("""      {stopWho && stopWho.reason !== "Goalie freeze" && (
        <div className="austop">
          <span className="h6">{STOP_WHO[stopWho.reason] || "Who did it?"}</span>
          {/* Goaltenders are in the list: they play the puck too. */}
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
      )}
""", "")

# Only a freeze still asks, so only a freeze sets the prompt.
sub("""    setStopAsk(false);
    setStopWho({ id: pid, reason });
  };""",
    """    setStopAsk(false);
    /* Only the freeze asks. Every other whistle is a reason and a time, and
       stopping to name someone for an icing costs the scorekeeper the next
       thing that happens. */
    if (reason === "Goalie freeze") setStopWho({ id: pid, reason });
  };""")

# ------------------------------------------------------------- the clock
sub("""              {[[-60, "−1:00"], [-10, "−:10"], [10, "+:10"], [60, "+1:00"]].map(([d, label]) => (""",
    """              {[[-60, "−1:00"], [-10, "−:10"], [-1, "−:01"], [1, "+:01"], [10, "+:10"], [60, "+1:00"]].map(([d, label]) => (""")

# ------------------------------------------------------- correcting a play
sub("""          {editPlay.kind === "penalty" && (""",
    """          {editPlay.kind === "faceoff" && (
            <>
              {/* The side first, because changing it changes who can have
                  won it - and the winner list has to be the right bench. */}
              <select value={editDraft.team || "us"}
                onChange={(e) => setEditDraft({
                  ...editDraft, team: e.target.value, winner: "", winnerId: null,
                })}>
                <option value="us">{usLabel}</option>
                <option value="them">{oppName || "Them"}</option>
              </select>
              {editDraft.team === "us" ? (
                <select value={editDraft.winnerId || ""}
                  onChange={(e) => setEditDraft({
                    ...editDraft,
                    winnerId: e.target.value || null,
                    winner: e.target.value ? nameOf(e.target.value) : "",
                  })}>
                  {/* A draw with no name on it is a complete answer, not a
                      blank one, so it is worded as the team rather than as
                      an empty option. */}
                  <option value="">{usLabel} — no player</option>
                  {skaters.filter((p) => p.position !== "G").map((p) => (
                    <option key={p.id} value={p.id}>#{p.number} {p.name}</option>
                  ))}
                </select>
              ) : theirs.length ? (
                <select value={editDraft.winner || ""}
                  onChange={(e) => setEditDraft({
                    ...editDraft, winner: e.target.value, winnerId: null,
                  })}>
                  <option value="">{oppName || "Them"} — no player</option>
                  {theirs.map((p) => (
                    <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
                  ))}
                </select>
              ) : (
                <input className="auentryname" value={editDraft.winner || ""}
                  placeholder={(oppName || "Their") + " player"}
                  onChange={(e) => setEditDraft({
                    ...editDraft, winner: e.target.value, winnerId: null,
                  })} />
              )}
            </>
          )}

          {editPlay.kind === "miss" && (
            editDraft.team === "us" ? (
              <select value={editDraft.shooterId || ""}
                onChange={(e) => setEditDraft({
                  ...editDraft,
                  shooterId: e.target.value || null,
                  shooter: e.target.value ? nameOf(e.target.value) : "",
                })}>
                <option value="">{usLabel} — no player</option>
                {skaters.filter((p) => p.position !== "G").map((p) => (
                  <option key={p.id} value={p.id}>#{p.number} {p.name}</option>
                ))}
              </select>
            ) : (
              <input className="auentryname" value={editDraft.shooter || ""}
                placeholder={(oppName || "Their") + " player"}
                onChange={(e) => setEditDraft({
                  ...editDraft, shooter: e.target.value, shooterId: null,
                })} />
            )
          )}

          {editPlay.kind === "stoppage" && (
            <select value={editDraft.reason || "Other"}
              onChange={(e) => setEditDraft({ ...editDraft, reason: e.target.value })}>
              {STOP_REASONS.map((r) => <option key={r}>{r}</option>)}
            </select>
          )}

          {editPlay.kind === "penalty" && (""")

io.open(p, 'w', encoding='utf-8').write(s)
print('edits, clock and stoppage prompt')
