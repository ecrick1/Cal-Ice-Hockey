# -*- coding: utf-8 -*-
"""The pages we built come out of Settings and into the sidebar.

Three public pages were being edited from inside Settings: the venue page,
the three footer pages, and the interest form. They ended up there because
each started as a field or two, and a field or two is what a settings screen
is for. They are not that any more - the venue page has an address, hours,
parking and four sets of directions - and finding them meant knowing they
were three cards down inside a tab named after something else.

They are pages. The sidebar lists pages. So they are in the sidebar, in a
group named Pages, next to the other things that put words on the public
site rather than under the tab where the tickets URL lives.

Settings keeps what a settings screen is actually for: who the club is,
where the site points, what the console looks like, and who you are.

The editors themselves did not move. Each was already a self-contained card
reading from the same handful of setters, so the change is which section
name draws which card - and the sub-nav across the top hides when one of
these is opened from the sidebar, because a page reached directly does not
need a row of tabs telling it where else it could have been.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ======================================================== the sidebar group
sub("""  ["Library", [["opponents", "Opponents"], ["news", "News"], ["sponsors", "Sponsors"]]],""",
    """  ["Library", [["opponents", "Opponents"], ["news", "News"], ["sponsors", "Sponsors"]]],
  /* Pages that put words on the public site. They were cards inside Settings
     until each grew past the field or two a settings screen is for. */
  ["Pages", [["venue", "Venue page"], ["legal", "Footer pages"],
    ["form", "Interest form"]]],""")

# ============================================ they are their own destinations
sub("""const SETTINGS_SECTIONS = [
  ["organization", "Organization", "Shared by everyone at your school"],
  ["appearance", "Appearance", "Only affects your view"],
  ["account", "Account", "Only affects you"],
];""",
    """const SETTINGS_SECTIONS = [
  ["organization", "Organization", "Shared by everyone at your school"],
  ["appearance", "Appearance", "Only affects your view"],
  ["account", "Account", "Only affects you"],
];

/* Sections of this editor that are reached from the sidebar as pages in their
   own right. They render the one card they are about and no sub-nav: a page
   opened directly does not need a row of tabs saying where else it could
   have been. */
const PAGE_SECTIONS = ["venue", "legal", "form"];""")

sub("""    <div className="ausettings">
      <nav className="ausubnav" aria-label="Settings sections">
        {SETTINGS_SECTIONS.map(([k, label, hint]) => (
          <button key={k} className={"ausubitem " + (section === k ? "on" : "")}
            onClick={() => setSection(k)}>
            <span className="ausubname">{label}</span>
            <span className="ausubhint">{hint}</span>
          </button>
        ))}
      </nav>""",
    """    <div className="ausettings">
      {!PAGE_SECTIONS.includes(section) && (
        <nav className="ausubnav" aria-label="Settings sections">
          {SETTINGS_SECTIONS.map(([k, label, hint]) => (
            <button key={k} className={"ausubitem " + (section === k ? "on" : "")}
              onClick={() => setSection(k)}>
              <span className="ausubname">{label}</span>
              <span className="ausubhint">{hint}</span>
            </button>
          ))}
        </nav>
      )}""")

# ------------------------------------- close Organization before the pages
sub("""                Prefilled on new home games. Away games take the opponent's rink and city.
              </p>
            </section>

            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Footer pages</p>""",
    """                Prefilled on new home games. Away games take the opponent's rink and city.
              </p>
            </section>
          </div>
        )}

        {/* ================= FOOTER PAGES ================= */}
        {section === "legal" && (
          <div style={{ display: "grid", gap: 18, maxWidth: 620 }}>
            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Footer pages</p>""")

sub("""            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Venue page</p>""",
    """          </div>
        )}

        {/* ================= VENUE PAGE ================= */}
        {section === "venue" && (
          <div style={{ display: "grid", gap: 18, maxWidth: 620 }}>
            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Venue page</p>""")

sub("""            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Interest form</p>""",
    """          </div>
        )}

        {/* ================= INTEREST FORM ================= */}
        {section === "form" && (
          <div style={{ display: "grid", gap: 18, maxWidth: 620 }}>
            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Interest form</p>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the pages are in the sidebar')
