# -*- coding: utf-8 -*-
"""The console offers the links and waits to be told.

Finding a returning player is the console's job; deciding they are the same
person is not. So the panel says who it thinks came back and from which
years, and links only what is confirmed - one at a time, or all of them in
one go after reading the list.

It never links on its own. The case this exists for is two people who share
a name, and an automatic pass would join exactly those two.

The panel is only there while there is something to offer. Once a roster is
linked it disappears rather than sitting at the top of the tab as a control
nobody needs again, and it stays away for a locked season, where every other
write is refused too.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""  /* Totals come from box scores once any exist; the typed numbers are only a
   * fallback for seasons with no game log. Showing which is which stops
   * someone typing into a field that will be overwritten by the next game. */
  const derived = (p) => boxScoreTotals(site, season, p);""",
    """  /* Totals come from box scores once any exist; the typed numbers are only a
   * fallback for seasons with no game log. Showing which is which stops
   * someone typing into a field that will be overwritten by the next game. */
  const derived = (p) => boxScoreTotals(site, season, p);

  /* ---- Linking a player to the seasons they already played ----
   *
   * A career is assembled by matching names, which is right until somebody
   * changes what they go by or two people share one. A personId settles it,
   * and this is where one gets attached.
   *
   * Only rows with no id yet are offered: once a player is linked the
   * question has been answered and re-asking it is noise. Matching for the
   * suggestion ignores case, punctuation and accents, which is right for a
   * suggestion and would be wrong for a decision - so a person makes the
   * decision. */
  const linkable = useMemo(() => {
    if (lock.locked) return [];
    const others = Object.entries(site.seasons || {}).filter(([sn]) => sn !== sel);
    return roster
      .filter((p) => !p.personId && String(p.name || "").trim())
      .map((p) => {
        const hits = others
          .map(([sn, se]) => ({
            sn,
            row: (se.roster || []).find((x) => nameKey(x.name) === nameKey(p.name)),
          }))
          .filter((h) => h.row);
        return { p, hits };
      })
      .filter((c) => c.hits.length)
      /* The most seasons first: the longest careers are the ones worth
         getting right, and the ones a reader is most likely to notice. */
      .sort((a, b) => b.hits.length - a.hits.length
        || (a.p.name || "").localeCompare(b.p.name || ""));
  }, [site.seasons, sel, roster, lock.locked]);

  /* One id shared by every row that is this person - adopting an id already
     on one of them if there is one, so linking twice from different seasons
     does not produce two people. */
  const linkOne = (c) => {
    const id = c.p.personId || (c.hits.find((h) => h.row.personId) || {}).row?.personId || uid();
    updateSeason(sel, {
      roster: roster.map((x) => (x.id === c.p.id ? { ...x, personId: id } : x)),
    });
    for (const h of c.hits) {
      const se = site.seasons[h.sn];
      updateSeasonProp(h.sn, {
        roster: (se.roster || []).map((x) => (x.id === h.row.id ? { ...x, personId: id } : x)),
      });
    }
  };

  const confirmLink = async (c) => {
    const years = c.hits.map((h) => h.sn).sort().join(", ");
    const ok = await ask({
      title: "Same player?",
      message: c.p.name + " also appears in " + years + ".",
      detail: "Linking joins those seasons into one career. Do it only if it is "
        + "the same person - two players who share a name are two careers.",
      confirmLabel: "Link",
    });
    if (ok) linkOne(c);
  };

  const confirmLinkAll = async () => {
    const ok = await ask({
      title: "Link " + linkable.length + " player"
        + (linkable.length === 1 ? "" : "s") + "?",
      message: "Each is joined to the earlier seasons listed beside them.",
      list: linkable.map((c) => ({
        label: c.p.name,
        note: c.hits.map((h) => h.sn).sort().join(", "),
      })),
      detail: "Check the list first: two people who share a name would be "
        + "joined into one career.",
      confirmLabel: "Link them",
    });
    if (ok) linkable.forEach(linkOne);
  };""")

# ------------------------------------------------------------- the panel
sub("""  const removePlayer = async (p) => {
    const played = derived(p);""",
    """  const LinkPanel = () => (linkable.length ? (
    <section className="card aulinkcard">
      <div className="boxhead">
        <p className="h6" style={{ margin: 0 }}>Played here before</p>
        <span className="bsm" style={{ color: "var(--au-faint)", marginLeft: "auto" }}>
          {linkable.length} to check
        </span>
      </div>
      <p className="auhint" style={{ marginTop: 8, maxWidth: 640 }}>
        These names also appear in earlier seasons. Linking joins them into one
        career on the player's page. Nothing is linked until you say so — two
        players who happen to share a name are two careers, and only you can
        tell which this is.
      </p>
      <div className="aulinklist">
        {linkable.map((c) => (
          <div className="aulinkrow" key={c.p.id}>
            <span className="aulinkname">
              {c.p.number ? "#" + c.p.number + " " : ""}{c.p.name}
            </span>
            <span className="aulinkyears">
              {c.hits.map((h) => h.sn).sort().join(", ")}
            </span>
            <button className="btn bGhost bSm" onClick={() => confirmLink(c)}>Link</button>
          </div>
        ))}
      </div>
      {linkable.length > 1 && (
        <button className="btn bNavy bSm" style={{ marginTop: 12 }}
          onClick={confirmLinkAll}>Link all {linkable.length}</button>
      )}
    </section>
  ) : null);

  const removePlayer = async (p) => {
    const played = derived(p);""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }

/* Players who may have played here before: a name, the years, and the one
   button that answers it. */
.adminui .aulinkcard { margin-bottom: 18px; border-color: var(--au-primary); }
.adminui .aulinklist { display: grid; gap: 6px; margin-top: 12px; }
.adminui .aulinkrow { display: flex; align-items: center; gap: 12px; padding: 7px 10px;
  background: var(--au-raised); border: 1px solid var(--au-line); border-radius: 8px; }
.adminui .aulinkname { font-size: 13.5px; font-weight: 700; color: var(--au-text); }
.adminui .aulinkyears { font-size: 12px; color: var(--au-faint); margin-left: auto; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the console offers, the user decides')
