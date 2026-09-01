# -*- coding: utf-8 -*-
"""A draw can belong to a team, and a freeze belongs to a goaltender.

Two gaps in the prompts, both of the same kind: the console insisted on a
name where the honest answer was a side.

Nobody sees who won every draw. Most of a period's faceoffs are a scramble
and the only thing anyone is sure of is which end the puck came out to. So
each side gets a "won it" button beside its player list: the play records
the team and no player, which is what the face-off split has always counted
anyway - it reads the team, not the name.

And a freeze is not a general question. Only one player on each side can
freeze a puck, and the sheet already knows which one is in net. So that
reason gets two buttons instead of two rosters, each naming the goaltender
it will credit, and neither of them requires anyone to remember who started
the period.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ----------------------------------------------------------- faceoff by team
sub("""          {theirs.length ? (
            <select value="" onChange={(e) => winFaceoff("them", e.target.value)}>
              <option value="">{oppName || "Them"} — pick a player</option>
              {theirs.map((p) => (
                <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
              ))}
            </select>
          ) : (
            <button className="btn bGhost bSm" onClick={() => winFaceoff("them", "")}>
              {oppName || "Them"} won it
            </button>
          )}
          <button className="btn bGhost bSm austopskip" onClick={() => setFaceoffAsk(null)}>
            Skip
          </button>""",
    """          {/* Most draws are a scramble and nobody is sure who came out with
              it. The split has always counted the team rather than the name,
              so a side on its own is a complete answer, not a partial one. */}
          <button className="btn bGhost bSm" onClick={() => winFaceoff("us", "")}>
            {usLabel} won it
          </button>
          {theirs.length > 0 && (
            <select value="" onChange={(e) => winFaceoff("them", e.target.value)}>
              <option value="">{oppName || "Them"} — pick a player</option>
              {theirs.map((p) => (
                <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
              ))}
            </select>
          )}
          <button className="btn bGhost bSm" onClick={() => winFaceoff("them", "")}>
            {oppName || "Them"} won it
          </button>
          <button className="btn bGhost bSm austopskip" onClick={() => setFaceoffAsk(null)}>
            Skip
          </button>""")

# A team draw has no name on it, so the log says whose it was.
sub("""                        <span className="auplaykind stop">FO</span>
                        <span className="auplaywho">{p.winner || "Faceoff won"}</span>""",
    """                        <span className="auplaykind stop">FO</span>
                        <span className="auplaywho">
                          {p.winner || (p.team === "us" ? usLabel : oppName || "Them") + " won the draw"}
                        </span>""", 2)

# ------------------------------------------------------------ who froze it
sub("""      {stopWho && (
        <div className="austop">
          <span className="h6">{STOP_WHO[stopWho.reason] || "Who did it?"}</span>
          {/* Goaltenders included: a freeze is the one stoppage that is
              nearly always theirs. */}
          <select value="" onChange={(e) => nameStopper("us", e.target.value)}>""",
    """      {stopWho && stopWho.reason === "Goalie freeze" && (
        <div className="austop">
          <span className="h6">{STOP_WHO["Goalie freeze"]}</span>
          {/* Only one player a side can freeze a puck, and the sheet already
              knows which one is in net. Two buttons, each naming who it will
              credit, rather than two rosters and a decision. */}
          <button className="btn bGhost bSm"
            onClick={() => nameStopper("us", ourKeeperId)}>
            {usLabel}{ourKeeperName ? " — " + ourKeeperName : ""}
          </button>
          <button className="btn bGhost bSm"
            onClick={() => nameStopper("them", live.goalieThem || "")}>
            {oppName || "Them"}{live.goalieThem ? " — " + live.goalieThem : ""}
          </button>
          <button className="btn bGhost bSm austopskip" onClick={() => setStopWho(null)}>
            Don't know
          </button>
        </div>
      )}

      {stopWho && stopWho.reason !== "Goalie freeze" && (
        <div className="austop">
          <span className="h6">{STOP_WHO[stopWho.reason] || "Who did it?"}</span>
          {/* Goaltenders are in the list: they play the puck too. */}
          <select value="" onChange={(e) => nameStopper("us", e.target.value)}>""")

# The keeper on our side, if one is set. "empty" is the empty net, which
# cannot freeze anything.
sub("""  const [stopAsk, setStopAsk] = useState(false);""",
    """  const ourKeeperId = live.goalieUs && live.goalieUs !== "empty" ? live.goalieUs : "";
  const ourKeeperName = ourKeeperId ? nameOf(ourKeeperId) : "";
  const [stopAsk, setStopAsk] = useState(false);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('team draws and goalie freezes')
