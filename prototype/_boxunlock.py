# -*- coding: utf-8 -*-
"""The box score opens for a live game, so a check has somewhere to be fixed.

Live scoring raises a check the moment a player line stops agreeing with the
play-by-play, names the player and says what they are off by - and then the
one screen that can correct a player line was disabled until the game went
final. So the console could tell you a number was wrong and give you no way
to put it right until the game was over. That is worse than not flagging it.

The gate was written when a box score was something typed up afterwards. It
is not any more: live scoring writes those lines as the game happens, which
means it can put a wrong number in one, which means the way to correct it
has to be open at the same time. A game being scored has a box score by
definition - it is the thing being filled in.

Nothing in the editor needed changing to allow it. Every use of the final
score inside it was already written to cope with not having one, because it
was always possible to open a game whose score had been cleared.

The check in the console says where to go, because knowing a number is wrong
and knowing which screen fixes it are two different pieces of knowledge and
it only ever had the first.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the gate
sub("""              <button className="btn bGhost aucount" style={{ fontSize: 12, padding: "5px 8px" }}
                disabled={!g.result}
                title={g.result ? "Enter per-player stats" : "Mark the game final first"}
                onClick={() => setOpenBox(openBox === g.id ? null : g.id)}>""",
    """              {/* Open for a game being scored as well as a finished one. Live
                  scoring writes these lines as the game happens, so it can put
                  a wrong number in one, so the way to correct it has to be open
                  while the game is on - the reconciliation checks are raised
                  then and they have to be answerable then. */}
              <button className="btn bGhost aucount" style={{ fontSize: 12, padding: "5px 8px" }}
                disabled={!g.result && !g.live}
                title={g.result || g.live
                  ? "Enter and correct per-player stats"
                  : "Mark the game final first, or score it live"}
                onClick={() => setOpenBox(openBox === g.id ? null : g.id)}>""")

sub("""        Tick "Final?" to enter a score, then open Box to record who scored. Season and
        career totals are calculated from those box scores.""",
    """        Tick "Final?" to enter a score, then open Box to record who scored. A game
        being scored live has its Box open too, so a line can be corrected without
        waiting for the final. Season and
        career totals are calculated from those box scores.""")

# ------------------------------------------- and say so where it is raised
sub("""        <div className="aumismatch">
          <span className="aumismatchtag">Check</span>
          {liveChecks.map((c) => (
            <span className="aumismatchitem" key={c.key || c.label}>
              <b>{c.label}</b> {c.detail}
            </span>
          ))}
        </div>""",
    """        <div className="aumismatch">
          <span className="aumismatchtag">Check</span>
          {liveChecks.map((c) => (
            <span className="aumismatchitem" key={c.key || c.label}>
              <b>{c.label}</b> {c.detail}
            </span>
          ))}
          {/* Knowing a number is wrong and knowing which screen fixes it are
              two different things, and this only had the first. */}
          <span className="aumismatchwhere">
            Correct a player's line on Schedule → this game → Box.
          </span>
        </div>""")

sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
/* Where to go about it, on its own line under the checks. */
.adminui .aumismatchwhere { flex-basis: 100%; font-size: 11.5px; color: var(--au-faint); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the box opens while the game is on')
