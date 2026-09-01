# -*- coding: utf-8 -*-
"""An assist credited to a line that no goal records, and a check that names it.

Two things, one of which caused the other.

The bug. A goal writes its assists through cleanAssists, which drops an
empty pick, a player picked twice, and the scorer picked as their own
assist. The player lines were credited from the raw pair instead. So
choosing the same player in both assist slots, or naming the scorer as an
assist, put a point on someone's line that no goal in the play-by-play
accounts for - and nothing would ever take it off again, because removing
the goal reverses the assists the goal recorded, and this was not one of
them. Both now come from the same cleaned list, which is the only way they
can agree: they are one decision, not two.

The check. "Assists 4 in the play-by-play vs 5 on player lines" is a true
statement and a useless one - it says a number is wrong without saying whose
line to look at, which leaves thirty players to check by hand. It names them
now, with what each one is off by, so the fix is a number to correct rather
than a search. Penalty minutes get the same treatment, since it is the same
question asked of a different column.

Also removes a dead duplicate `scorerId` key sitting directly above its
replacement in the typed-up goal builder. The second always won; the first
had been overwritten for long enough to be read as meaningful.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the cause
sub("""      assistIds: us
        ? cleanAssists([a1, a2], scorer)
        : cleanAssists([oppA1, oppA2], oppScorer).map(theirId),
      assists: us
        ? cleanAssists([a1, a2], scorer).map(nameOf)
        : cleanAssists([oppA1, oppA2], oppScorer).map(theirName),
    };

    if (us) {
      bumpLine(scorer, { g: 1, ...(goalStrength === "PP" ? { ppg: 1 } : {}), ...(goalStrength === "SH" ? { shg: 1 } : {}) });
      [a1, a2].filter(Boolean).forEach((id) => bumpLine(id, { a: 1 }));
    }""",
    """      assistIds: us ? ourAssists : cleanAssists([oppA1, oppA2], oppScorer).map(theirId),
      assists: us
        ? ourAssists.map(nameOf)
        : cleanAssists([oppA1, oppA2], oppScorer).map(theirName),
    };

    if (us) {
      bumpLine(scorer, { g: 1, ...(goalStrength === "PP" ? { ppg: 1 } : {}), ...(goalStrength === "SH" ? { shg: 1 } : {}) });
      /* The same list the play records, not the raw pair. Crediting the pair
         put an assist on a line for a player picked twice, or named as their
         own assist - a point no goal accounted for, and one that removing the
         goal would never take off again, because it reverses the assists the
         goal holds and this was not one of them. */
      ourAssists.forEach((id) => bumpLine(id, { a: 1 }));
    }""")

sub("""  const addGoal = () => {
    if (goalMissing) return;
    const us = goalTeam === "us";
""",
    """  const addGoal = () => {
    if (goalMissing) return;
    const us = goalTeam === "us";
    /* Decided once. The play and the scorer's line both read from this, so
       there is no way for them to disagree. */
    const ourAssists = cleanAssists([a1, a2], scorer);
""")

# ------------------------------------------------ dead key above its twin
sub("""          scorerId: us ? scorer : null,
          scorerId: us ? scorer : (oppRowById(oppName1) ? oppName1 : null),""",
    """          scorerId: us ? scorer : (oppRowById(oppName1) ? oppName1 : null),""")

# ---------------------------------------------------- name who is off
sub("""  const playAssists = plays
    .filter((p) => p.kind === "goal" && p.team === "us" && p.period !== "SO")
    .reduce((t, p) => t + ((p.assists || []).length), 0);""",
    """  const playAssists = plays
    .filter((p) => p.kind === "goal" && p.team === "us" && p.period !== "SO")
    .reduce((t, p) => t + ((p.assists || []).length), 0);

  /* Which lines disagree with the plays, and by how much. A total on its own
     says a number is wrong without saying whose line to open, which leaves
     the whole roster to check by hand. */
  const offBy = (fromPlays, key) => {
    const names = [];
    for (const pl of R) {
      const line = n((L[pl.id] || {})[key]);
      const real = fromPlays[pl.id] || 0;
      if (line !== real) {
        names.push(pl.name + " " + (line > real ? "+" : "\\u2212") + Math.abs(line - real));
      }
    }
    return names;
  };
  const assistsFromPlays = (() => {
    const m = {};
    for (const p of plays) {
      if (p.kind !== "goal" || p.team !== "us" || p.period === "SO") continue;
      for (const id of p.assistIds || []) if (id) m[id] = (m[id] || 0) + 1;
    }
    return m;
  })();
  const pimFromPlays = (() => {
    const m = {};
    for (const p of plays) {
      if (p.kind !== "penalty" || p.team !== "us") continue;
      const pl = p.playerId ? R.find((x) => x.id === p.playerId)
        : R.find((x) => x.name === p.player);
      if (pl) m[pl.id] = (m[pl.id] || 0) + n(p.minutes);
    }
    return m;
  })();
  const whoIsOff = (names) => (names.length
    ? " \\u2014 " + names.slice(0, 4).join(", ")
      + (names.length > 4 ? " and " + (names.length - 4) + " more" : "")
    : "");""")

sub("""  check("assists", "Assists",
    playAssists === boxAssists,
    playAssists + " in the play-by-play vs " + boxAssists + " on player lines",
    !anyBox || !plays.length);

  check("pim", "Penalty minutes",
    playPim === boxPim,
    playPim + " in the play-by-play vs " + boxPim + " on player lines",
    !anyBox || !anyPenaltyPlays);""",
    """  check("assists", "Assists",
    playAssists === boxAssists,
    playAssists + " in the play-by-play vs " + boxAssists + " on player lines"
      + whoIsOff(offBy(assistsFromPlays, "a")),
    !anyBox || !plays.length);

  check("pim", "Penalty minutes",
    playPim === boxPim,
    playPim + " in the play-by-play vs " + boxPim + " on player lines"
      + whoIsOff(offBy(pimFromPlays, "pim")),
    !anyBox || !anyPenaltyPlays);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('assists agree, and the check names who')
