# -*- coding: utf-8 -*-
"""The penalties already at this whistle are restamped when another lands.

Holding the live readout was only half of it. Each penalty play also carries
the strength it produced, written when it was entered - so the first of two
coincidental minors was stamped with the count as it stood before the second
one existed, and kept it for good.

Tonight's game has the pair: Fung's roughing reads 5-on-4 and Mcquillen
Young's, at the same whistle, reads 4-on-4. Neither the scoreboard nor the
rulebook ever thought it was 5-on-4; it was true for the four seconds
between two names being typed.

So adding a penalty restamps the ones already entered at that whistle. Same
period and same clock is the same stoppage - the clock is stopped while they
go in - which is the test the strength model already uses to decide what
cancels against what.

Only penalties that take a skater off are restamped, and a whistle that
turns out to leave the sides even has the stamp taken off rather than left
saying something that is no longer the case.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""      ...(madeIt && penaltyKind(p.kind).shorts ? { strength: madeIt } : {}),
    }));""",
    """      ...(madeIt && penaltyKind(p.kind).shorts ? { strength: madeIt } : {}),
    }));

    /* The penalties already entered at this whistle were stamped with the
       strength as it stood before this one existed. Two coincidental minors
       left the first of them reading 5-on-4 for ever. Same period and same
       clock is the same stoppage - the clock is stopped while they are
       entered - so those are brought up to what the whistle actually
       produced, and a whistle that turns out even loses the stamp rather
       than keeping one that is no longer true. */
    const settled = retro ? plays : plays.map((x) => {
      if (x.kind !== "penalty") return x;
      if (x.period !== when.period || x.clock !== when.clock) return x;
      if (!penaltyKind(kindOf(x)).shorts) return x;
      const { strength, ...rest } = x;
      return madeIt ? { ...rest, strength: madeIt } : rest;
    });""")

sub("""    push({
      plays: [...plays, ...newPlays],
      live: retro
        ? { ...live, ejected }""",
    """    push({
      plays: [...settled, ...newPlays],
      live: retro
        ? { ...live, ejected }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the whole whistle gets the same stamp')
