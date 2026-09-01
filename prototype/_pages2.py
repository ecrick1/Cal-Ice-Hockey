# -*- coding: utf-8 -*-
"""The nav bar becomes a list, and a built page becomes somewhere to go.

The bar was written twice - once as a row of buttons for the desktop and
once as an accordion for the phone - with the two submenus shared between
them and everything else duplicated. Rearranging it meant editing both and
hoping. It is one list now, rendered twice, so an item moved moves in both.

The default is the bar exactly as it was written, so nothing changes until
somebody changes it. Dropdowns keep the tuple shape NavMenu already took,
which is why that component is untouched.

Donate keeps its habit of appending itself to the More menu when a donate
link is set. It is attached to whichever group is still called "more"
rather than to a position, so the group can be moved or renamed and the
link follows or drops out honestly.

And a page built from blocks is reachable: its view is "page:" and its id,
which the switch renders through CustomPage and the nav can point at like
any other destination.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ==================================================== the list, and its default
sub("""/* Everything that matters to somebody around the program rather than
   following the team week to week. Last in the bar, for the same reason. */
const NAV_MORE = [
  ["venue", "Venue"],
  ["alumni", "Alumni"],
];""",
    """/* Everything that matters to somebody around the program rather than
   following the team week to week. Last in the bar, for the same reason. */
const NAV_MORE = [
  ["venue", "Venue"],
  ["alumni", "Alumni"],
];

/* ---------------- The nav bar, as data ----------------
 *
 * The bar used to be written twice - a row of buttons for the desktop and an
 * accordion for the phone - so moving an item meant editing both. One list
 * now, rendered twice.
 *
 * An item is a destination or a group of them:
 *   { id, label, view }   a page of the site
 *   { id, label, href }   a link out
 *   { id, label, items }  a dropdown of the above
 *
 * A page built from blocks is a view like any other: "page:" and its id.
 */
const DEFAULT_NAV = [
  { id: "home", label: "Home", view: "home" },
  { id: "schedule", label: "Schedule", view: "schedule" },
  { id: "team", label: "Team", items: NAV_TEAM.map(([view, label]) => ({ id: view, label, view })) },
  { id: "stats", label: "Stats", view: "stats" },
  { id: "news", label: "News", view: "newsindex" },
  { id: "more", label: "More", items: NAV_MORE.map(([view, label]) => ({ id: view, label, view })) },
];

const pageView = (id) => "page:" + id;
const viewPageId = (view) => (String(view || "").startsWith("page:") ? view.slice(5) : null);

/* The bar to draw: what has been arranged, or the default if nothing has.
   Items pointing at a page that no longer exists are dropped rather than
   left as a link to nowhere. */
function navFor(site, donateUrl) {
  const pages = site.pages || [];
  const alive = (it) => {
    const pid = viewPageId(it.view);
    return !pid || pages.some((pg) => pg.id === pid);
  };
  const raw = Array.isArray(site.nav) && site.nav.length ? site.nav : DEFAULT_NAV;
  return raw
    .map((it) => (it.items
      ? { ...it, items: it.items.filter(alive)
          /* Donate has always appended itself to More when a link is set. It
             follows the group rather than the position, so the group can be
             moved or renamed and the link goes with it. */
          .concat(it.id === "more" && donateUrl
            ? [{ id: "donate", label: "Donate", href: donateUrl }] : []) }
      : it))
    .filter((it) => (it.items ? it.items.length : alive(it)));
}

/* NavMenu and the mobile accordion both read [key, label, href] tuples. */
const navTuples = (item) => (item.items || [])
  .map((c) => [c.view || c.id, c.label, c.href]);

/* Is this item the page being looked at? */
const navOn = (item, view) => (item.items
  ? (item.items || []).some((c) => c.view === view)
  : item.view === view || (item.view === "newsindex" && view === "news"));""")

# ================================================= the desktop bar
sub("""            <button className={`navlink ${view === "home" ? "on" : ""}`} onClick={() => setView("home")}>Home</button>
            <button className={`navlink ${view === "schedule" ? "on" : ""}`} onClick={() => setView("schedule")}>Schedule</button>
            <NavMenu label="Team" view={view} setView={setView} items={NAV_TEAM} />
            <button className={`navlink ${view === "stats" ? "on" : ""}`} onClick={() => setView("stats")}>Stats</button>
            <button className={`navlink ${view === "news" || view === "newsindex" ? "on" : ""}`} onClick={() => setView("newsindex")}>News</button>
            <NavMenu label="More" view={view} setView={setView} items={moreItems} />""",
    """            {navBar.map((it) => (it.items ? (
              <NavMenu key={it.id} label={it.label} view={view} setView={setView}
                items={navTuples(it)} />
            ) : it.href ? (
              <a key={it.id} className="navlink" href={it.href}
                target="_blank" rel="noreferrer noopener">{it.label}</a>
            ) : (
              <button key={it.id} className={"navlink " + (navOn(it, view) ? "on" : "")}
                onClick={() => setView(it.view)}>{it.label}</button>
            )))}""")

# ================================================= the phone accordion
sub("""            <button className={"navpanelitem" + (view === "home" ? " on" : "")}
              onClick={() => goNav("home")}>Home</button>
            <button className={"navpanelitem" + (view === "schedule" ? " on" : "")}
              onClick={() => goNav("schedule")}>Schedule</button>

            <button className={"navpanelitem group" + (navGroup === "team" ? " open" : "")
                + (NAV_TEAM.some(([k]) => k === view) ? " on" : "")}
              aria-expanded={navGroup === "team"}
              onClick={() => setNavGroup((g) => (g === "team" ? null : "team"))}>
              Team <IcChevD size={17} />
            </button>
            {navGroup === "team" && (
              <div className="navpanelsub">
                {NAV_TEAM.map(([k, text]) => (
                  <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                    onClick={() => goNav(k)}>{text}</button>
                ))}
              </div>
            )}

            <button className={"navpanelitem" + (view === "stats" ? " on" : "")}
              onClick={() => goNav("stats")}>Stats</button>
            <button className={"navpanelitem" + (view === "news" || view === "newsindex" ? " on" : "")}
              onClick={() => goNav("newsindex")}>News</button>

            <button className={"navpanelitem group" + (navGroup === "more" ? " open" : "")
                + (NAV_MORE.some(([k]) => k === view) ? " on" : "")}
              aria-expanded={navGroup === "more"}
              onClick={() => setNavGroup((g) => (g === "more" ? null : "more"))}>
              More <IcChevD size={17} />
            </button>
            {navGroup === "more" && (
              <div className="navpanelsub">
                {moreItems.map(([k, text, href]) => (href ? (
                  <a key={k} className="navpanelitem child" href={href}
                    target="_blank" rel="noreferrer noopener"
                    onClick={() => setNavOpen(false)}>{text}</a>
                ) : (
                  <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                    onClick={() => goNav(k)}>{text}</button>
                )))}""",
    """            {navBar.map((it) => (it.items ? (
              <div key={it.id}>
                <button className={"navpanelitem group" + (navGroup === it.id ? " open" : "")
                    + (navOn(it, view) ? " on" : "")}
                  aria-expanded={navGroup === it.id}
                  onClick={() => setNavGroup((g) => (g === it.id ? null : it.id))}>
                  {it.label} <IcChevD size={17} />
                </button>
                {navGroup === it.id && (
                  <div className="navpanelsub">
                    {navTuples(it).map(([k, text, href]) => (href ? (
                      <a key={k} className="navpanelitem child" href={href}
                        target="_blank" rel="noreferrer noopener"
                        onClick={() => setNavOpen(false)}>{text}</a>
                    ) : (
                      <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                        onClick={() => goNav(k)}>{text}</button>
                    )))}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('one nav list, rendered twice')
