# -*- coding: utf-8 -*-
"""The sidebar grows the pages you build, and a New page button.

The Pages group was three fixed entries. It now also lists every page built
in the console and ends with the button that makes another - so a page you
made is a place in the sidebar like anything else, rather than something
reached through a list inside a screen.

Menu bar joins them at the top of the group, because arranging the bar is
what turns a built page into a page anybody can find.

A new page opens straight into its own editor. There is no naming dialog
first: a page called "Untitled" that exists is easier to name than a name
that has to be decided before anything exists.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# =================================================== the group and its titles
sub("""  ["Pages", [["venue", "Venue page"], ["legal", "Footer pages"],
    ["form", "Interest form"]]],""",
    """  ["Pages", [["menubar", "Menu bar"], ["venue", "Venue page"],
    ["legal", "Footer pages"], ["form", "Interest form"]]],""")

sub("""  venue: "Venue page",
  legal: "Footer pages",
  form: "Interest form",
};""",
    """  venue: "Venue page",
  legal: "Footer pages",
  form: "Interest form",
  menubar: "Menu bar",
};""")

# ======================================= built pages listed under the group
sub("""                {items.map(([k, label]) => (
                  <button key={k} className={"aulink " + (tab === k ? "on" : "")}
                    onClick={() => setTab(k)}>
                    <span className="audot" />
                    {label}
                    {k === "inbox" && unread > 0 && <span className="aubadge">{unread}</span>}
                    {k === "alumni" && alumniUnread > 0 && <span className="aubadge">{alumniUnread}</span>}
                  </button>
                ))}
              </div>""",
    """                {items.map(([k, label]) => (
                  <button key={k} className={"aulink " + (tab === k ? "on" : "")}
                    onClick={() => setTab(k)}>
                    <span className="audot" />
                    {label}
                    {k === "inbox" && unread > 0 && <span className="aubadge">{unread}</span>}
                    {k === "alumni" && alumniUnread > 0 && <span className="aubadge">{alumniUnread}</span>}
                  </button>
                ))}
                {/* Pages built in the console sit with the ones that ship, and
                    the button that makes another closes the group. */}
                {group === "Pages" && (
                  <>
                    {(draft.pages || []).map((pg) => (
                      <button key={pg.id} className={"aulink " + (tab === pageView(pg.id) ? "on" : "")}
                        onClick={() => setTab(pageView(pg.id))}>
                        <span className="audot" />
                        {pg.title || "Untitled"}
                      </button>
                    ))}
                    <button className="aulink aunewpage" onClick={newPage}>
                      <span className="audot" />+ New page
                    </button>
                  </>
                )}
              </div>""")

# ============================================================= making one
sub("""  const [settingsSection, setSettingsSection] = useState("organization");""",
    """  const [settingsSection, setSettingsSection] = useState("organization");

  /* Straight into the editor with a working title. A page called Untitled
     that exists is easier to name than a name decided before anything does. */
  const newPage = () => {
    const id = uid();
    setDraft((st) => ({
      ...st,
      pages: [...(st.pages || []), { id, title: "Untitled page", blocks: [] }],
    }));
    setTab(pageView(id));
  };""")

# ================================================================ the routes
sub("""            {(tab === "settings" || PAGE_SECTIONS.includes(tab)) && (""",
    """            {tab === "menubar" && <NavEditor site={draft} setDraft={setDraft} />}
            {viewPageId(tab) && (
              <PageBuilder site={draft} setDraft={setDraft} pageId={viewPageId(tab)}
                onGone={() => setTab("menubar")} />
            )}
            {(tab === "settings" || PAGE_SECTIONS.includes(tab)) && (""")

# ------------------------------------------------------------------- title
sub("""const ADMIN_TITLES = {""",
    """/* A built page is titled by its own name rather than by a fixed string. */
const adminTitle = (tab, site) => {
  const pid = viewPageId(tab);
  if (!pid) return ADMIN_TITLES[tab] || "";
  const pg = ((site && site.pages) || []).find((p) => p.id === pid);
  return (pg && pg.title) || "Untitled page";
};

const ADMIN_TITLES = {""")

io.open(p, 'w', encoding='utf-8').write(s)
print('sidebar lists built pages; routes wired')
