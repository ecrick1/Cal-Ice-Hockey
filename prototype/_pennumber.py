# -*- coding: utf-8 -*-
"""A penalty knows who took it, so the summary can print the number.

Colten Fazio had no number beside his penalty, and neither did anyone else
on our side: the penalty summary looks the player up on the roster by id,
and the penalty play was never given one. The box the penalty runs in got
the id, because the console has to know whose minutes are ticking - but the
line written to the play-by-play alongside it kept only the name. Every
other play carries its player's id. This one was the exception.

So it carries it. And because that fixes nothing already recorded - this
season's games included - the lookup falls back to the name when there is no
id, which is exactly what the visitors' side has always done. One roster,
one spelling, and the name is what the console wrote from the roster in the
first place.

The fallback stays even though the id is now written, because a name is what
a game typed up from a paper scoresheet has, and there is no id to give it.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------- write the id in future
sub("""    const newPlays = pens.map((p) => ({
      id: p.id, kind: "penalty", team: penTeam, ...when,
      player, minutes: p.minutes,""",
    """    const newPlays = pens.map((p) => ({
      id: p.id, kind: "penalty", team: penTeam, ...when,
      /* The id as well as the name: the summary prints the number off the
         roster, and a name alone leaves it to guess. */
      player, playerId, minutes: p.minutes,""")

# --------------------------------------------- and read the ones already in
sub("""  const numberOf = (id) => {
    const p = (season.roster || []).find((x) => x.id === id);
    return p && p.number ? p.number : "";
  };""",
    """  /* By id, or by name for anything recorded before the id was written down
     and for games typed up off a paper scoresheet, which never have one.
     The visitors' side has always worked this way. */
  const numberOf = (id, name) => {
    const roster = season.roster || [];
    const p = (id && roster.find((x) => x.id === id))
      || (name && roster.find((x) => (x.name || "").toLowerCase()
        === String(name).toLowerCase()));
    return p && p.number ? p.number : "";
  };""")

sub("""  const penNumber = (x, mine) => (mine ? numberOf(x.playerId) : oppNumberOf(x.player, x.playerId));""",
    """  const penNumber = (x, mine) => (mine
    ? numberOf(x.playerId, x.player) : oppNumberOf(x.player, x.playerId));""")

sub("""    const n = mine ? numberOf(id) : oppNumberOf(name, id);""",
    """    const n = mine ? numberOf(id, name) : oppNumberOf(name, id);""")

sub("""                    const jersey = mine ? numberOf(x.scorerId) : oppNumberOf(x.scorer);""",
    """                    const jersey = mine ? numberOf(x.scorerId, x.scorer) : oppNumberOf(x.scorer);""")

sub("""                                    const jn = mine ? numberOf(id) : oppNumberOf(nm);""",
    """                                    const jn = mine ? numberOf(id, nm) : oppNumberOf(nm);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('penalties carry the player id')
