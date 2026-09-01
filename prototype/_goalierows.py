# -*- coding: utf-8 -*-
"""Goaltenders get goaltending numbers in the preview roster.

The block was there - Forwards, Defense, Goaltenders - but every keeper was
being run through the skater columns, so the three of them sat under G, A, P
and PIM reading nought, nought, nought, nought. That is not a quiet season;
it is the wrong four questions.

They take GP, GAA, SV% and SO instead, in the same four column positions,
under a small header of their own so nobody has to guess which is which. It
is the same line the Goaltending card above prints, from the same source:
ours from the box scores, theirs from the league's aggregate, matched by
name the way the skater rows already are.

Sorted by appearances rather than by the table's current column, because
the column headings above them are asking about goals.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------- a line for a keeper
sub("""  /* Click a column to sort by it, inside each block rather than across the
     three: a roster is read position by position.""",
    """  /* A goaltender's four numbers, from whichever side of the sheet they are
     on. Ours are summed from the box scores we hold; theirs come from the
     league's season aggregate, matched on name - the same join the skater
     rows use, and it returns nulls rather than zeroes when it misses, so an
     unmatched keeper shows dashes instead of a shutout season. */
  const keeperFor = (row) => {
    if (row.mine) {
      const k = keeperLine(row.t || {});
      return { gp: k.gp, gaa: k.gaa == null ? null : k.gaa.toFixed(2),
        svpct: pctText(k.svpct), so: k.so };
    }
    const norm = (x) => String(x || "").toLowerCase().replace(/[^a-z ]/g, "").trim();
    const g = ((theirStats && theirStats.goalies) || [])
      .find((x) => norm(x.name) === norm(row.p.name));
    if (!g) return null;
    const faced = (g.saves || 0) + (g.ga || 0);
    return {
      gp: g.gp == null ? null : g.gp,
      gaa: g.gaa != null ? g.gaa : (g.gp ? ((g.ga || 0) / g.gp).toFixed(2) : null),
      svpct: g.svpct != null ? String(g.svpct).replace(/^0/, "") : (faced ? pct3(g.saves, faced) : null),
      so: g.so == null ? null : g.so,
    };
  };

  /* Click a column to sort by it, inside each block rather than across the
     three: a roster is read position by position.""")

# -------------------------------------------------------------- the rendering
sub("""            {ROSTER_GROUPS.map(([g, title]) => {
              const rows = sortRoster(rosterRows.filter((r) => groupOf(r.p) === g));
              if (!rows.length) return null;
              return (
                <tbody key={g}>
                  <tr className="gcbtgroup">
                    <th colSpan={ROSTER_COLS.length} scope="colgroup">{title}</th>
                  </tr>
                  {rows.map(({ p, t, mine }) => (
                    <tr key={p.id}>
                      <td>{p.number}</td>
                      <td className="gcbtname">
                        {mine
                          ? <button className="pboxname" onClick={() => onPlayer(p.id)}>{p.name}</button>
                          : p.name}
                      </td>
                      <td className="gcbtspot">{posOf(p)}</td>
                      <td>{t ? (t.gp || 0) : "\\u2014"}</td>
                      <td>{t ? (t.g || 0) : "\\u2014"}</td>
                      <td>{t ? (t.a || 0) : "\\u2014"}</td>
                      <td className="gcbtpts">{t ? (t.g || 0) + (t.a || 0) : "\\u2014"}</td>
                      <td>{t ? (t.pim || 0) : "\\u2014"}</td>
                    </tr>
                  ))}
                </tbody>
              );
            })}""",
    """            {ROSTER_GROUPS.map(([g, title]) => {
              const keepers = g === "G";
              const pool = rosterRows.filter((r) => groupOf(r.p) === g);
              /* Keepers by appearances: the column the table is sorted on is
                 asking about goals, which is not a question about them. */
              const rows = keepers
                ? [...pool].sort((a, b) => ((keeperFor(b) || {}).gp || 0) - ((keeperFor(a) || {}).gp || 0)
                    || (Number(a.p.number) || 0) - (Number(b.p.number) || 0))
                : sortRoster(pool);
              if (!rows.length) return null;
              return (
                <tbody key={g}>
                  <tr className="gcbtgroup">
                    <th colSpan={ROSTER_COLS.length} scope="colgroup">{title}</th>
                  </tr>
                  {keepers && (
                    <tr className="gcbtsub">
                      <td /><td /><td />
                      <td>GP</td><td>GAA</td><td>SV%</td><td>SO</td><td />
                    </tr>
                  )}
                  {rows.map((row) => {
                    const { p, t, mine } = row;
                    const k = keepers ? keeperFor(row) : null;
                    const dash = "\\u2014";
                    return (
                      <tr key={p.id}>
                        <td>{p.number}</td>
                        <td className="gcbtname">
                          {mine
                            ? <button className="pboxname" onClick={() => onPlayer(p.id)}>{p.name}</button>
                            : p.name}
                        </td>
                        <td className="gcbtspot">{posOf(p)}</td>
                        {keepers ? (
                          <>
                            <td>{k && k.gp != null ? k.gp : dash}</td>
                            <td>{k && k.gaa != null ? k.gaa : dash}</td>
                            <td>{k && k.svpct ? k.svpct : dash}</td>
                            <td>{k && k.so != null ? k.so : dash}</td>
                            <td />
                          </>
                        ) : (
                          <>
                            <td>{t ? (t.gp || 0) : dash}</td>
                            <td>{t ? (t.g || 0) : dash}</td>
                            <td>{t ? (t.a || 0) : dash}</td>
                            <td className="gcbtpts">{t ? (t.g || 0) + (t.a || 0) : dash}</td>
                            <td>{t ? (t.pim || 0) : dash}</td>
                          </>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              );
            })}""")

# -------------------------------------------------------------------- CSS
sub("""table.stats.sortable .gcbtgroup th { padding: 9px 16px; font-size: 11.5px;
  background: #EEF2F6; border-top: 1px solid #E3E9EF; }""",
    """table.stats.sortable .gcbtgroup th { padding: 9px 16px; font-size: 11.5px;
  background: #EEF2F6; border-top: 1px solid #E3E9EF; }
/* The keepers' four columns are not the four above them, so they are
   labelled where they start rather than left to be inferred. */
.gcbt tbody .gcbtsub td { padding-top: 8px; padding-bottom: 2px; border-top: 0;
  font-size: 10px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--muted); }
.gcbt tbody .gcbtsub { background: none; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('goalie rows use goalie columns')
