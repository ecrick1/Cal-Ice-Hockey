# -*- coding: utf-8 -*-
"""News in tiers, a roster you sort by its headings, and four staff across.

Three pages, three different complaints, one shape underneath: the page was
treating every item as equally important when it is not.

News was a single column of wide rows, so the story from this morning and
the one from last February were the same size and the page was as long as
the archive. It reads in tiers now - two across for the two most recent,
four for the next four, six for everything after. Descending prominence,
which is what a news index is for, and it fits the whole archive on a screen
instead of a mile of identical rows.

The roster table had headings that were labels. Every other table on the
site sorts by clicking its headings, and this one made you go back up to a
dropdown to do the same thing. Now the headings do it, including the four
columns the dropdown never offered - height, weight, shoots and where
somebody is from. Clicking the column you are already sorted by turns it
round.

And the staff grid filled to whatever fitted, which on a wide screen was
five across and a ragged last row. Four, which is what was asked for, and
what makes the portraits big enough to be portraits.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================================== 1. NEWS
sub("""          <div className="newslist">
            {posts.map((n, i) => (
              <article className={"newsrow" + (i === 0 ? " lead" : "")} key={n.id}
                role="link" tabIndex={0} onClick={() => openPost(n.id)}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), openPost(n.id))}>
                <div className="newsrowart">
                  <img src={n.image || STOCK_IMAGES[i % STOCK_IMAGES.length]} alt="" loading="lazy"
                    onError={(e) => { e.currentTarget.style.visibility = "hidden"; }} />
                  <span className="newstag">{n.tag}</span>
                </div>
                <div className="newsrowbody">
                  <h2 className="newsrowtitle">{n.title}</h2>
                  {n.blurb && <p className="newsrowblurb">{n.blurb}</p>}
                  <p className="newsrowmeta">
                    {n.author ? n.author + " · " : ""}{fmtDate(n.date)}
                  </p>
                </div>
              </article>
            ))}
          </div>""",
    """          {/* Descending prominence: the two most recent, then four, then the
              archive six across. A news index whose every row is the same
              size says this morning and last February matter equally. */}
          {[["lead", posts.slice(0, 2)],
            ["mid", posts.slice(2, 6)],
            ["rest", posts.slice(6)]].map(([tier, items]) => (
            items.length ? (
              <div className={"newstier " + tier} key={tier}>
                {items.map((n, i) => (
                  <article className="newscard" key={n.id}
                    role="link" tabIndex={0} onClick={() => openPost(n.id)}
                    onKeyDown={(e) => (e.key === "Enter" || e.key === " ")
                      && (e.preventDefault(), openPost(n.id))}>
                    <div className="newscardart">
                      <img src={n.image || STOCK_IMAGES[i % STOCK_IMAGES.length]} alt="" loading="lazy"
                        onError={(e) => { e.currentTarget.style.visibility = "hidden"; }} />
                      <span className="newstag">{n.tag}</span>
                    </div>
                    <div className="newscardbody">
                      <h2 className="newscardtitle">{n.title}</h2>
                      {/* The archive gets a headline and a date. A blurb on a
                          card this size is three lines of grey. */}
                      {n.blurb && tier !== "rest" && <p className="newscardblurb">{n.blurb}</p>}
                      <p className="newscardmeta">
                        {n.author ? n.author + " · " : ""}{fmtDate(n.date)}
                      </p>
                    </div>
                  </article>
                ))}
              </div>
            ) : null
          ))}""")

sub(""".newslist { display: grid; gap: 14px; margin-top: 24px; }""",
    """/* Three tiers down the page, each a row of cards rather than a stack of
   wide rows. The column counts are fixed rather than auto-filled: the point
   is that the top two are bigger than the next four, and auto-fill would
   make them all the width of whatever happened to fit. */
.newstier { display: grid; gap: 16px; margin-top: 24px; }
.newstier.lead { grid-template-columns: repeat(2, 1fr); }
.newstier.mid  { grid-template-columns: repeat(4, 1fr); }
.newstier.rest { grid-template-columns: repeat(6, 1fr); gap: 13px; }

.newscard { display: flex; flex-direction: column; background: #fff;
  border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
  cursor: pointer; }
.newscard:hover { border-color: var(--blue); }
.newscardart { position: relative; aspect-ratio: 16 / 9; background: var(--ice); }
.newscardart img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.newscardbody { padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 7px; }
.newscardtitle { font-family: var(--body); font-weight: 800; letter-spacing: -0.018em;
  line-height: 1.24; color: var(--ink); margin: 0; font-size: 1.05rem; }
.newstier.lead .newscardtitle { font-size: 1.5rem; }
.newstier.mid .newscardtitle { font-size: 1.12rem; }
.newstier.rest .newscardtitle { font-size: 0.92rem; }
.newstier.rest .newscardbody { padding: 12px 13px 14px; gap: 5px; }
.newscardblurb { font-size: 14px; line-height: 1.55; color: var(--muted); margin: 0; }
.newscardmeta { font-size: 12px; font-weight: 700; color: var(--muted); margin: 0; }

/* Six across is a large-screen shape. Below that the tiers step down rather
   than shrinking cards until the headlines are two words a line. */
@media (max-width: 1100px) {
  .newstier.rest { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 900px) {
  .newstier.mid { grid-template-columns: repeat(2, 1fr); }
  .newstier.rest { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 620px) {
  .newstier.lead, .newstier.mid { grid-template-columns: 1fr; }
  .newstier.rest { grid-template-columns: repeat(2, 1fr); }
}

.newslist { display: grid; gap: 14px; margin-top: 24px; }""")

# ====================================================== 2. ROSTER SORTING
sub("""  const POS_LABEL = { F: "F", D: "D", G: "G" };
  const POS_FULL = { F: "Forward", D: "Defense", G: "Goaltender" };
  const sorted = useMemo(() => {
    const r = [...season.roster];
    if (sortBy === "number") r.sort((a, b) => (Number(a.number) || 0) - (Number(b.number) || 0));
    if (sortBy === "name") r.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    if (sortBy === "position") r.sort((a, b) => (a.position || "").localeCompare(b.position || "") || (Number(a.number) || 0) - (Number(b.number) || 0));
    if (sortBy === "year") r.sort((a, b) => (a.year || "").localeCompare(b.year || ""));
    return r;
  }, [season.roster, sortBy]);""",
    """  const POS_LABEL = { F: "F", D: "D", G: "G" };
  const POS_FULL = { F: "Forward", D: "Defense", G: "Goaltender" };

  /* The table's columns, each knowing how to read itself. Every other table
     on the site sorts by its headings; this one sent you back up to a
     dropdown, which also only offered four of the nine. */
  const [sortDir, setSortDir] = useSticky("roster.sortdir", "asc");
  const num = (v) => Number(String(v || "").replace(/[^\\d.]/g, "")) || 0;
  const ROSTER_COLS = [
    ["number", "No", (p) => num(p.number), true],
    ["name", "Name", (p) => p.name || "", false],
    ["position", "Pos", (p) => p.position || "", false],
    ["shoots", "Shoots", (p) => p.shoots || "", false],
    ["height", "Ht", (p) => num(p.height) * 12 + num(String(p.height || "").split(/[′']/)[1]), true],
    ["weight", "Wt", (p) => num(p.weight), true],
    ["year", "Class", (p) => p.year || "", false],
    ["hometown", "Hometown / Prior Team", (p) => splitHome(p.hometown).home || "", false],
    ["prior", "Previous School", (p) => splitHome(p.hometown).prev || "", false],
  ];

  const sorted = useMemo(() => {
    const col = ROSTER_COLS.find((c) => c[0] === sortBy) || ROSTER_COLS[0];
    const [, , get, numeric] = col;
    const dir = sortDir === "desc" ? -1 : 1;
    return [...season.roster].sort((a, b) => {
      const x = get(a), y = get(b);
      const by = numeric ? x - y : String(x).localeCompare(String(y));
      /* A settled tie-break, so two players with the same class do not swap
         places every time the page re-renders. */
      return (by || (Number(a.number) || 0) - (Number(b.number) || 0)) * dir;
    });
  }, [season.roster, sortBy, sortDir]);

  const sortByCol = (key) => {
    if (sortBy === key) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else { setSortBy(key); setSortDir("asc"); }
  };""")

sub("""                  <thead><tr><th>No</th><th>Name</th><th>Pos</th><th>Shoots</th><th>Ht</th><th>Wt</th><th>Class</th><th>Hometown / Prior Team</th><th>Previous School</th></tr></thead>""",
    """                  <thead>
                    <tr>
                      {ROSTER_COLS.map(([key, label]) => {
                        const on = sortBy === key;
                        return (
                          <th key={key}
                            aria-sort={on ? (sortDir === "asc" ? "ascending" : "descending") : "none"}>
                            <button className={"sortbtn " + (on ? "on" : "")}
                              onClick={() => sortByCol(key)}
                              title={"Sort by " + label}>
                              {label}
                              <span className="sortcaret" aria-hidden="true">
                                {on ? (sortDir === "asc" ? "\\u25b2" : "\\u25bc") : "\\u25be"}
                              </span>
                            </button>
                          </th>
                        );
                      })}
                    </tr>
                  </thead>""")

sub("""              <div className="twrap">
                <table className="stats">
                  <thead>
                    <tr>
                      {ROSTER_COLS.map(([key, label]) => {""",
    """              <div className="twrap">
                <table className="stats sortable">
                  <thead>
                    <tr>
                      {ROSTER_COLS.map(([key, label]) => {""")

# ==================================================== 3. STAFF, FOUR ACROSS
sub(""".staffgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 18px; }""",
    """/* Four across, rather than as many as happen to fit. Auto-fill gave five on
   a wide screen and a ragged last row; four is what makes a portrait large
   enough to be a portrait. */
.staffgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
@media (max-width: 1040px) { .staffgrid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 760px) { .staffgrid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 460px) { .staffgrid { grid-template-columns: 1fr; } }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('news tiers, sortable roster, four staff across')
