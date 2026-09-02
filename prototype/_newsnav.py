# -*- coding: utf-8 -*-
"""Five across at the bottom, and a way to ask for one kind of story.

The archive is thirty-seven recaps, three previews, a feature and a notice.
Reading it meant scrolling past every game of the season to find the one
piece that was not a scoreline.

So the page opens with the kinds of story it holds. Built from the tags
actually on the stories rather than from a list written here: the console
lets staff invent a tag, so a hard-coded row of tabs would have an empty
Press Releases sitting there for ever and would never show whatever they
name next. A tag nobody has used does not appear; one used tomorrow does.

The names are friendlier than the tags - RECAP is filed as Game Recaps -
with a fallback for anything not in the list, so a new tag reads as a
capitalised word rather than as shouting. Counts, because "3" beside
Previews is the difference between a section worth opening and one that is
not.

And the bottom grid is five across rather than six. Six was two more than
the tier above it and the headlines were running to the ellipsis on almost
every card.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ the filter
sub("""function NewsIndexPage({ site, openPost }) {
  const posts = (site.news || [])
    .filter(isLive)
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""));
""",
    """/* Friendlier than the tag itself. Anything not here is title-cased rather
   than left shouting, so a tag invented next week still reads as a word. */
const TAG_LABEL = {
  RECAP: "Game Recaps", PREVIEW: "Game Previews", FEATURE: "Features",
  NEWS: "Team News", PRESS: "Press Releases", RELEASE: "Press Releases",
  ROSTER: "Roster News", AWARD: "Awards", ALUMNI: "Alumni",
};
const tagLabel = (t) => TAG_LABEL[t]
  || String(t || "").charAt(0) + String(t || "").slice(1).toLowerCase();

/* The order they read in when they exist. Everything else follows, so a tag
   nobody thought of still gets a place rather than being dropped. */
const TAG_ORDER = ["NEWS", "PREVIEW", "RECAP", "FEATURE", "PRESS", "RELEASE"];

function NewsIndexPage({ site, openPost }) {
  const live = (site.news || [])
    .filter(isLive)
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""));

  /* Built from the stories rather than from a list written here: the console
     lets staff invent a tag, so a fixed row of tabs would hold an empty
     section for ever and never show whatever they name next. */
  const kinds = useMemo(() => {
    const n = {};
    for (const p of live) {
      const t = String(p.tag || "").trim().toUpperCase();
      if (t) n[t] = (n[t] || 0) + 1;
    }
    return Object.keys(n)
      .sort((a, b) => {
        const ia = TAG_ORDER.indexOf(a), ib = TAG_ORDER.indexOf(b);
        if (ia !== ib) return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
        return a.localeCompare(b);
      })
      .map((t) => [t, tagLabel(t), n[t]]);
  }, [live]);

  const [kind, setKind] = useSticky("news.kind", "all");
  /* A tag can stop existing - the last story carrying it is edited or taken
     down - and a filter for it would then show an empty page with no way to
     tell why. */
  const active = kind !== "all" && kinds.some(([t]) => t === kind) ? kind : "all";
  const posts = active === "all"
    ? live
    : live.filter((p) => String(p.tag || "").trim().toUpperCase() === active);
""")

sub("""          <h1 className="stitle">News</h1>

          {!posts.length && (""",
    """          <h1 className="stitle">News</h1>

          {kinds.length > 1 && (
            <div className="gpsides newskinds">
              <button className={"gpside " + (active === "all" ? "on" : "")}
                onClick={() => setKind("all")}>
                Latest <span className="newskindn">{live.length}</span>
              </button>
              {kinds.map(([t, label, n]) => (
                <button key={t} className={"gpside " + (active === t ? "on" : "")}
                  onClick={() => setKind(t)}>
                  {label} <span className="newskindn">{n}</span>
                </button>
              ))}
            </div>
          )}

          {!posts.length && (""")

# ---------------------------------------------------------- five across
sub(""".newstier.rest { grid-template-columns: repeat(6, 1fr); gap: 13px; }""",
    """.newstier.rest { grid-template-columns: repeat(5, 1fr); gap: 15px; }""")

sub("""@media (max-width: 1100px) {
  .newstier.rest { grid-template-columns: repeat(4, 1fr); }
}""",
    """@media (max-width: 1100px) {
  .newstier.rest { grid-template-columns: repeat(4, 1fr); }
}
/* The kinds of story, in the segmented control the rest of the site uses for
   the same job. It wraps rather than scrolling: a tag invented later should
   push the row taller, not off the side of the page. */
.newskinds { flex-wrap: wrap; margin-bottom: 4px; }
.newskindn { font-size: 11px; font-weight: 800; opacity: 0.6; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('five across, and a nav built from the tags')
