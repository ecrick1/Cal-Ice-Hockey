# -*- coding: utf-8 -*-
"""Shots reach the stat lines, and a draw records both players.

Two things.

Shots were being assigned to shooters all night and landing nowhere. The
shooter went onto the play, and the play-by-play showed it, and the public
box score counted it off the plays - but no player line ever held a `shots`
field, so the admin box score was blank and season and career totals had
nothing to add up. The one screen where the number is supposed to live was
the one screen that never saw it.

So the lines are written from the plays, the way the goaltender's saves
already are: counted fresh on every write rather than bumped up and down.
Counting means an edited shooter or a deleted shot corrects the line with
it, and there is no reversal anywhere to forget. Goals count as shots here
too, because a goal is a shot that went in.

Only for a game being scored. A game typed up from a league sheet has its
shots entered by hand and a play-by-play that was never complete, so
recomputing would wipe what was typed in favour of what was not.

And a face-off is two players, not one. It recorded who won and threw away
who lost, which is half a statistic: a centre's record is what he won
against what he took, and the second number was going in the bin every time.
The prompt asks for both now, and both go on the line - won and lost - so a
draw finally counts for the man who lost it as well.

The second question is only asked when the first was answered by name. Most
draws are a scramble and the honest answer is a side rather than a player;
if nobody could say who won it, nobody can say who lost it either, and the
fast path stays one press.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ==================================================== lines built from plays
sub("""  const setLineFields = (playerId, fields) =>""",
    """  /**
   * The per-player counts the plays already hold: shots on goal, and draws
   * won and lost.
   *
   * Counted fresh rather than bumped, the same reasoning as the goaltender's
   * saves. A shooter corrected on a play, or a play deleted, fixes the line
   * with it - there is no +1 somewhere and a -1 somewhere else that have to
   * be kept in step, which is the arrangement that produced an assist nobody
   * could get rid of.
   *
   * A goal counts as a shot, because a goal is a shot that went in.
   *
   * Not for a typed-up game: those have their shots entered by hand and a
   * play-by-play that was never complete, so counting would replace what
   * somebody typed with what they did not.
   */
  const writeCounts = (nextPlays) => {
    if (retro) return;
    const tally = {};
    const add = (id, key) => {
      if (!id) return;
      tally[id] = tally[id] || {};
      tally[id][key] = (tally[id][key] || 0) + 1;
    };
    for (const x of nextPlays || []) {
      if (x.kind === "shot" && x.team === "us") add(x.shooterId, "shots");
      else if (x.kind === "goal" && x.team === "us" && x.period !== "SO") add(x.scorerId, "shots");
      else if (x.kind === "faceoff") {
        /* The play is filed under whoever won it, so ours is the winner on
           our draws and the loser on theirs. */
        if (x.team === "us") add(x.winnerId, "fow");
        else add(x.loserId, "fol");
      }
    }
    setDraft((st) => {
      const all = st.gameStats || {};
      const forGame = { ...(all[game.id] || {}) };
      let touched = false;
      /* Everyone with a line, so a deleted shot takes the count back down
         rather than leaving the last number that was written. */
      const ids = new Set([...Object.keys(forGame), ...Object.keys(tally)]);
      for (const id of ids) {
        const t = tally[id] || {};
        const cur = forGame[id] || { dressed: true, g: 0, a: 0, pim: 0 };
        const next = { ...cur, shots: t.shots || 0, fow: t.fow || 0, fol: t.fol || 0 };
        if (cur.shots !== next.shots || cur.fow !== next.fow || cur.fol !== next.fol) {
          forGame[id] = next;
          touched = true;
        }
      }
      return touched ? { ...st, gameStats: { ...all, [game.id]: forGame } } : st;
    });
  };

  const setLineFields = (playerId, fields) =>""")

sub("""    setGame(game.id, patch);
    if (patch.live) writeGoalie(patch.live);
    publish();""",
    """    setGame(game.id, patch);
    if (patch.live) writeGoalie(patch.live);
    if (patch.plays) writeCounts(patch.plays);
    publish();""")

# ======================================================= both ends of a draw
sub("""  const winFaceoff = (team, value) => {
    const us = team === "us";
    push({
      plays: [...plays, {
        id: uid(), kind: "faceoff", team,
        period: curPeriod,
        /* The draw happened when play resumed, not when the name was picked. */
        clock: (faceoffAsk && faceoffAsk.clock) || fmtClock(left),
        winnerId: us ? value || null : null,
        winner: us ? nameOf(value) : value,
      }],
    });
    setFaceoffAsk(null);
  };""",
    """  /* A draw is two players. Recording only the winner threw away half of it:
     a centre's record is what he won against what he took. */
  const commitFaceoff = (team, won, lost) => {
    push({
      plays: [...plays, {
        id: uid(), kind: "faceoff", team,
        period: curPeriod,
        /* The draw happened when play resumed, not when the name was picked. */
        clock: (faceoffAsk && faceoffAsk.clock) || fmtClock(left),
        ...won, ...lost,
      }],
    });
    setFaceoffAsk(null);
  };

  /* Who won, and then who lost - but only when the winner was named. Most
     draws are a scramble and the honest answer is a side rather than a man;
     if nobody could say who won it, nobody can say who lost it either. */
  const pickWinner = (team, value) => {
    const us = team === "us";
    const won = {
      winnerId: us ? value || null : null,
      winner: us ? nameOf(value) : value,
    };
    if (!value) return commitFaceoff(team, won, {});
    setFaceoffAsk({ ...(faceoffAsk || {}), team, won });
  };

  const pickLoser = (value) => {
    const a = faceoffAsk || {};
    /* The loser is on the other bench from the winner. */
    const theirsLost = a.team === "us";
    commitFaceoff(a.team, a.won, {
      loserId: theirsLost ? null : value || null,
      loser: theirsLost ? value : nameOf(value),
    });
  };""")

io.open(p, 'w', encoding='utf-8').write(s)
print('shots reach the lines; a draw has two ends')
