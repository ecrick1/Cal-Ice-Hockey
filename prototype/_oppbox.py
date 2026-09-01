# -*- coding: utf-8 -*-
"""Their box score is written from the plays too, and a period ends on the sheet.

Two gaps, both of them the same shape: something recorded during live
scoring that never reached the place it is read back from.

Their side of the box score was only ever written by hand. A penalty called
on their bench went onto the play-by-play, showed up on the strength band,
counted against them in the special-teams numbers - and their box score
still read 0 PIM for the player who took it, because nothing on the live
console has ever written a line for the away team. Wessler's two minutes are
on the sheet tonight and nowhere on his line.

So their rows are counted off the plays the way ours now are: goals,
assists, penalty minutes, shots and draws. Same recount-from-scratch, so
correcting a name or deleting a play fixes their line as it fixes ours, and
the two sides of one box score are finally built the same way.

Matched on the row id where the play carries one and on the name where it
does not, because a play entered before ids were written down has only the
name - which is exactly Wessler's penalty tonight.

And a period now ends on the sheet when the clock says it did. The end was
only written when somebody changed the period, so a period that ran out sat
there unmarked and the play-by-play went straight from the last whistle of
the first to the opening face-off of the second, with nothing between them
saying twenty minutes had been played.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================== their lines, from the plays
sub("""  const setLineFields = (playerId, fields) =>""",
    """  /**
   * Their half of the same sheet.
   *
   * Nothing on this console has ever written an away line, so everything
   * recorded against them lived in the play-by-play and nowhere a reader
   * would look for it. Counted the same way ours are, from the plays, so
   * both halves of one box score are built by one rule.
   *
   * Matched on the row id when the play carries one and on the name when it
   * does not: a play entered before ids were written has only a name.
   */
  const writeTheirCounts = (nextPlays) => {
    if (retro) return;
    setDraft((st) => {
      const all = st.opponentStats || {};
      const rows = all[game.id] || [];
      if (!rows.length) return st;
      const byId = new Map(rows.map((r) => [r.id, r]));
      const byName = new Map(rows.map((r) => [String(r.name || "").toLowerCase(), r]));
      const find = (id, name) => (id && byId.get(id))
        || (name && byName.get(String(name).toLowerCase())) || null;

      const t = new Map();
      const add = (row, key, n = 1) => {
        if (!row || !n) return;
        const c = t.get(row.id) || {};
        c[key] = (c[key] || 0) + n;
        t.set(row.id, c);
      };
      for (const x of nextPlays || []) {
        if (x.team === "them") {
          if (x.kind === "goal" && x.period !== "SO") {
            const sc = find(x.scorerId, x.scorer);
            add(sc, "g"); add(sc, "shots");
            (x.assists || []).forEach((nm, i) => add(find((x.assistIds || [])[i], nm), "a"));
          } else if (x.kind === "penalty") {
            add(find(x.playerId, x.player), "pim", Number(x.minutes) || 0);
          } else if (x.kind === "shot") {
            add(find(x.shooterId, x.shooter), "shots");
          } else if (x.kind === "faceoff") {
            add(find(x.winnerId, x.winner), "fow");
          }
        } else if (x.kind === "faceoff" && x.team === "us") {
          /* Our draw, so theirs is the one who lost it. */
          add(find(x.loserId, x.loser), "fol");
        }
      }

      let touched = false;
      const next = rows.map((r) => {
        const c = t.get(r.id) || {};
        const m = {
          ...r, g: c.g || 0, a: c.a || 0, pim: c.pim || 0,
          shots: c.shots || 0, fow: c.fow || 0, fol: c.fol || 0,
        };
        if (m.g !== r.g || m.a !== r.a || m.pim !== r.pim
          || m.shots !== r.shots || m.fow !== r.fow || m.fol !== r.fol) touched = true;
        return m;
      });
      return touched ? { ...st, opponentStats: { ...all, [game.id]: next } } : st;
    });
  };

  const setLineFields = (playerId, fields) =>""")

sub("""    if (patch.plays) writeCounts(patch.plays);""",
    """    if (patch.plays) { writeCounts(patch.plays); writeTheirCounts(patch.plays); }""")

# ================================================ a period ends when it ends
sub("""  /* ---- The goaltender's line, derived from shots and goals ----""",
    """  /* The period is over when the clock says so.
   *
   * The end was only ever written when somebody changed the period, so a
   * period that simply ran out sat unmarked and the sheet went from the last
   * whistle of the first to the opening face-off of the second with nothing
   * between them saying twenty minutes had been played. */
  useEffect(() => {
    if (retro || !live.running || left > 0) return;
    if (hasPeriodMark("end", curPeriod)) {
      setLive({ running: false, clockMs: 0, startedAt: null });
      return;
    }
    push({
      plays: [...plays, {
        id: uid(), kind: "period", phase: "end", period: curPeriod, clock: "0:00",
      }],
      live: { ...live, running: false, clockMs: 0, startedAt: null },
    });
  }, [left <= 0, live.running, curPeriod, retro]);

  /* ---- The goaltender's line, derived from shots and goals ----""")

io.open(p, 'w', encoding='utf-8').write(s)
print('their box score and the end of a period')
