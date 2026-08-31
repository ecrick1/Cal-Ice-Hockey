# -*- coding: utf-8 -*-
"""Group the preview roster, let every column sort it, and move it last
on a phone.

Three changes to the same table:

  * Forwards, defense and goaltenders are read as three groups, not one
    list with the keepers pushed to the bottom by a sort key.
  * Every column is a button. Numbers open high to low, words A to Z, and
    a second click reverses - the same behaviour as the season stats page,
    so the two tables work the same way.
  * The visitors' section titles are kept when their roster is read. The
    feed does publish a position letter, but it is blank often enough that
    the section a player was listed under is the sounder answer.

And the stack order. On a phone the two columns become one and the roster -
by far the longest card - sat third, between the goaltending and everything
worth reading before it. Making the columns transparent to the grid lets
the roster take an order of its own and drop to the foot.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)


# ------------------------------------------- keep the visitors' own grouping
sub("""        for (const sec of secs) {
          if (/coach/i.test(sec.title || "")) continue;
          for (const d of sec.data || []) {
            out.push({
              id: "acha-" + d.row.player_id,""",
    """        for (const sec of secs) {
          if (/coach/i.test(sec.title || "")) continue;
          /* The section a player is listed under, kept because the position
             letter on the row is sometimes blank and this never is. */
          const group = /goal/i.test(sec.title || "") ? "G"
            : /defen/i.test(sec.title || "") ? "D" : "F";
          for (const d of sec.data || []) {
            out.push({
              id: "acha-" + d.row.player_id,
              group,""")

# ------------------------------------------------ grouping, columns, sorting
sub("""  const posOf = (p) => (p.position === "D" || p.position === "G" ? p.position : p.spot || "F");
  const theirGoalies = (theirRoster || []).filter((p) => p.position === "G").slice(0, 2);""",
    """  const posOf = (p) => (p.position === "D" || p.position === "G" ? p.position : p.spot || "F");
  /* Which of the three blocks a player belongs in. Read off whichever of
     the position, the visitors' section or the forward's spot is filled in,
     because no one source has all three sides of it. */
  const groupOf = (p) => {
    const v = String(p.position || p.group || p.spot || "").trim();
    return /^g/i.test(v) ? "G" : /^d/i.test(v) ? "D" : "F";
  };
  const theirGoalies = (theirRoster || []).filter((p) => groupOf(p) === "G").slice(0, 2);""")

sub("""  /* A name reads better broken: the given name light, the surname bold
     under it, the way a team sheet sets one. */""",
    """  /* Click a column to sort by it, inside each block rather than across the
     three: a roster is read position by position. Figures open high to low,
     names and numbers in the order they are written. */
  const ROSTER_COLS = [
    { key: "number", label: "#", numeric: true, first: "asc",
      get: (r) => Number(r.p.number) || 0 },
    { key: "name", label: "Player", numeric: false, first: "asc",
      get: (r) => lastFirst(r.p.name) || "" },
    { key: "pos", label: "Pos", numeric: false, first: "asc", title: "Position",
      get: (r) => posOf(r.p) },
    /* A player with no line in any box score is not a zero, so unknown
       sorts below every recorded figure either way round. */
    { key: "gp", label: "GP", numeric: true, first: "desc", get: (r) => (r.t ? r.t.gp || 0 : -1) },
    { key: "g", label: "G", numeric: true, first: "desc", get: (r) => (r.t ? r.t.g || 0 : -1) },
    { key: "a", label: "A", numeric: true, first: "desc", get: (r) => (r.t ? r.t.a || 0 : -1) },
    { key: "p", label: "P", numeric: true, first: "desc", title: "Points",
      get: (r) => (r.t ? (r.t.g || 0) + (r.t.a || 0) : -1) },
    { key: "pim", label: "PIM", numeric: true, first: "desc", get: (r) => (r.t ? r.t.pim || 0 : -1) },
  ];
  const ROSTER_GROUPS = [["F", "Forwards"], ["D", "Defense"], ["G", "Goaltenders"]];
  const [rSortKey, setRSortKey] = useState("p");
  const [rSortDir, setRSortDir] = useState("desc");
  const sortRoster = (list) => {
    const col = ROSTER_COLS.find((c) => c.key === rSortKey)
      || ROSTER_COLS.find((c) => c.key === "p");
    const dir = rSortDir === "asc" ? 1 : -1;
    return [...list].sort((a, b) => {
      const x = col.get(a);
      const y = col.get(b);
      const cmp = col.numeric ? x - y : String(x).localeCompare(String(y));
      // Jersey number as the tiebreak, so equal rows keep a settled order.
      return cmp * dir || (Number(a.p.number) || 0) - (Number(b.p.number) || 0);
    });
  };

  /* A name reads better broken: the given name light, the surname bold
     under it, the way a team sheet sets one. */""")

# -------------------------------------------------------------- the table
sub("""      {rosterRows.length ? (
        <div className="twrap">
          <table className="stats gcbt">
            <thead>
              <tr>
                <th>#</th><th>Player</th><th>Pos</th>
                <th>GP</th><th>G</th><th>A</th><th>P</th><th>PIM</th>
              </tr>
            </thead>
            <tbody>
              {[...rosterRows]
                /* Their side has stats for some players and not others, so
                   points are read through a guard rather than off `t`. */
                .sort((a, b) => {
                  const pts = (x) => (x.t ? (x.t.g || 0) + (x.t.a || 0) : -1);
                  return (a.p.position === "G") - (b.p.position === "G")
                    || pts(b) - pts(a)
                    || (Number(a.p.number) || 99) - (Number(b.p.number) || 99);
                })
                .map(({ p, t, mine }) => (
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
          </table>
        </div>
      ) : (""",
    """      {rosterRows.length ? (
        <div className="twrap">
          <table className="stats sortable gcbt">
            <thead>
              <tr>
                {ROSTER_COLS.map((col) => {
                  const on = rSortKey === col.key;
                  return (
                    <th key={col.key} title={col.title}
                      aria-sort={on ? (rSortDir === "asc" ? "ascending" : "descending") : "none"}>
                      <button className={"sortbtn " + (on ? "on" : "")}
                        onClick={() => {
                          if (on) setRSortDir((d) => (d === "desc" ? "asc" : "desc"));
                          else { setRSortKey(col.key); setRSortDir(col.first); }
                        }}>
                        {col.label}
                        <span className="sortcaret" aria-hidden="true">
                          {on ? (rSortDir === "asc" ? "\\u25b2" : "\\u25bc") : "\\u25be"}
                        </span>
                      </button>
                    </th>
                  );
                })}
              </tr>
            </thead>
            {ROSTER_GROUPS.map(([g, title]) => {
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
            })}
          </table>
        </div>
      ) : (""")

# the section needs a hook for the stacking order
sub("""      <section className="statcard gcpad">
        <h2 className="statsec">
          Roster
          <span className="gcserieslead">{note}</span>
      </h2>""",
    """      <section className="statcard gcpad gcroster">
        <h2 className="statsec">
          Roster
          <span className="gcserieslead">{note}</span>
      </h2>""")

# -------------------------------------------------------------------- CSS
sub(""".gcgrid { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr); gap: 20px;""",
    """/* A block header inside the roster table: the same bar as a column head,
   set as a label rather than a control. */
.gcbtgroup th { padding: 9px 16px; font-size: 11.5px; background: #EEF2F6; }
.gcbtgroup th, .gcbt tbody .gcbtgroup th { border-top: 1px solid #E3E9EF; }
.gcbt tbody:first-of-type .gcbtgroup th { border-top: 0; }

.gcgrid { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr); gap: 20px;""")

sub("""@media (max-width: 900px) {
  .gcgrid { grid-template-columns: 1fr; }""",
    """@media (max-width: 900px) {
  .gcgrid { grid-template-columns: 1fr; }
  /* One column means one stack, and the columns should stop dividing it -
     transparent to the grid, every card is placed directly and the roster,
     the longest card by a distance, can take an order that puts it last
     instead of third. */
  .gcgrid > .gccol { display: contents; }
  .gcroster { order: 2; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('roster grouped, sortable, and last on a phone')
