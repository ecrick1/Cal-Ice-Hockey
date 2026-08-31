"""Move Venue into a "More" menu, add an Alumni sign-up, add a Donate pill."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------------------ storage key
sub("""const RECRUITS_KEY = "cal-hockey-recruits";""",
    """const RECRUITS_KEY = "cal-hockey-recruits";
const ALUMNI_KEY = "cal-hockey-alumni";""")

# ------------------------------------------------------------- seed: URL
sub("""    ticketsUrl: "", contactEmail: "", homeVenue: "Oakland Ice Center", siteUrl: "",""",
    """    ticketsUrl: "", contactEmail: "", homeVenue: "Oakland Ice Center", siteUrl: "",
    /* The university's own giving page, with the fund already selected. */
    donateUrl: "https://give.berkeley.edu/giftdetails?fund1=FU0852000",""")

# ---------------------------------------------------------- the More menu
sub("""const NAV_TEAM = [
  ["roster", "Roster"],
  ["prospects", "Recruits"],
  ["staff", "Hockey Ops Staff"],
  ["volunteers", "Volunteers"],
];""",
    """const NAV_TEAM = [
  ["roster", "Roster"],
  ["prospects", "Recruits"],
  ["staff", "Hockey Ops Staff"],
  ["volunteers", "Volunteers"],
];

/* Everything that matters to somebody around the program rather than
   following the team week to week. Last in the bar, for the same reason. */
const NAV_MORE = [
  ["venue", "Venue"],
  ["alumni", "Alumni"],
];""")

# ------------------------------------------------- desktop nav: drop Venue
sub("""            <button className={`navlink ${view === "venue" ? "on" : ""}`} onClick={() => setView("venue")}>Venue</button>
""", "")

sub("""            <button className={`navlink ${view === "news" || view === "newsindex" ? "on" : ""}`} onClick={() => setView("newsindex")}>News</button>
          </nav>""",
    """            <button className={`navlink ${view === "news" || view === "newsindex" ? "on" : ""}`} onClick={() => setView("newsindex")}>News</button>
            <NavMenu label="More" view={view} setView={setView} items={NAV_MORE} />
          </nav>""")

# ------------------------------------------------- mobile nav: drop Venue
sub("""            <button className={"navpanelitem" + (view === "venue" ? " on" : "")}
              onClick={() => goNav("venue")}>Venue</button>
""", "")

# ------------------------------------------------- mobile nav: More group
sub("""            <button className={"navpanelitem" + (view === "news" || view === "newsindex" ? " on" : "")}
              onClick={() => goNav("newsindex")}>News</button>
""",
    """            <button className={"navpanelitem" + (view === "news" || view === "newsindex" ? " on" : "")}
              onClick={() => goNav("newsindex")}>News</button>

            <button className={"navpanelitem group" + (navGroup === "more" ? " open" : "")
                + (NAV_MORE.some(([k]) => k === view) ? " on" : "")}
              aria-expanded={navGroup === "more"}
              onClick={() => setNavGroup((g) => (g === "more" ? null : "more"))}>
              More <IcChevD size={17} />
            </button>
            {navGroup === "more" && (
              <div className="navpanelsub">
                {NAV_MORE.map(([k, text]) => (
                  <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                    onClick={() => goNav(k)}>{text}</button>
                ))}
              </div>
            )}
""")

# ------------------------------------------------------ donate: desktop
sub("""            <button className="goldpill navcta" onClick={() => setView("tickets")}>Tickets</button>""",
    """            {donateUrl && (
              <a className="navlink navcta donate" href={donateUrl} target="_blank" rel="noreferrer noopener">
                Donate
              </a>
            )}
            <button className="goldpill navcta" onClick={() => setView("tickets")}>Tickets</button>""")

# ------------------------------------------------------- donate: mobile
sub("""              <button className="goldpill" onClick={() => goNav("tickets")}>Tickets</button>""",
    """              <button className="goldpill" onClick={() => goNav("tickets")}>Tickets</button>
              {donateUrl && (
                <a className="goldpill ghost" href={donateUrl} target="_blank" rel="noreferrer noopener"
                  onClick={() => setNavOpen(false)}>Donate</a>
              )}""")

# The value both of those read.
sub("""  // Public pages read the hydrated shape (opponents resolved, stats derived).
  // The admin edits `site` itself.
  const isAdmin = view === "admin";""",
    """  // Public pages read the hydrated shape (opponents resolved, stats derived).
  // The admin edits `site` itself.
  const isAdmin = view === "admin";
  const donateUrl = ((site && site.settings) || {}).donateUrl || "";""")

# --------------------------------------------------------- donate styling
sub(""".navcta { background: var(--gold); color: var(--deep); padding: 10px 18px; border-radius: 999px; }""",
    """.navcta { background: var(--gold); color: var(--deep); padding: 10px 18px; border-radius: 999px; }
/* Giving money is not the same act as buying a ticket, so it does not wear
   the same gold. An outline on the navy reads as a third option rather than a
   third shout. */
.navcta.donate { background: transparent; color: #fff; box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.45);
  text-decoration: none; display: inline-flex; align-items: center; }
.navcta.donate:hover { background: rgba(255,255,255,0.1); color: #fff; }
.goldpill.ghost { background: transparent; color: var(--deep);
  box-shadow: inset 0 0 0 1.5px rgba(4,30,66,0.3); }
.goldpill.ghost:hover { background: rgba(4,30,66,0.06); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('nav + donate done')
