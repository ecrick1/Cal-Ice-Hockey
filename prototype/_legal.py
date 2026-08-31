"""Legal pages, and a Get tickets button on the next-home-game banner."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------- Get tickets, on the banner
sub("""                {featureState === "scheduled" && ticketsUrl && (
                  <a className="btn bGold bSm" href={ticketsUrl} target="_blank" rel="noreferrer">Tickets</a>
                )}""",
    """                {/* Always offered on a home game, the way the nav pill is:
                    straight to the seller when one is set, otherwise to the
                    tickets page, which carries the door prices. */}
                {featureState === "scheduled" && feature.homeAway === "H" && (
                  ticketsUrl
                    ? <a className="btn bGold bSm" href={ticketsUrl} target="_blank" rel="noreferrer">
                        <IcTicket size={15} /> Get tickets
                      </a>
                    : <button className="btn bGold bSm" onClick={() => goto("tickets")}>
                        <IcTicket size={15} /> Get tickets
                      </button>
                )}""")

# ---------------------------------------------------------- the legal pages
sub("""const LEGAL_PAGES = null;""", "", 0)  # no-op guard

sub("""    /* The home rink, for the Venue page.""",
    """    /* The three pages linked at the very bottom. Drafts describing what this
     * site actually does - a club is not a law firm, and boilerplate copied
     * from somewhere else would be describing somebody else's data handling.
     * Editable under Settings, and worth a read by the university before this
     * goes public. */
    legal: {
      terms:
        "# Using this site\\n" +
        "This site is published by the Cal Ice Hockey club, a student-run team at " +
        "the University of California, Berkeley. It is not an official University " +
        "publication and the club is not part of Cal Athletics.\\n\\n" +
        "# What is here\\n" +
        "Schedules, results, statistics and rosters are published in good faith and " +
        "corrected when we find a mistake. Historical records are compiled from " +
        "league and third-party sources and may be incomplete.\\n\\n" +
        "# Getting in touch\\n" +
        "If something on this site is wrong, or should not be here, write to the " +
        "program and we will look at it.",
      privacy:
        "# What this site collects\\n" +
        "Nothing, unless you send it. There are two forms: the recruit interest " +
        "form and the alumni list. Both ask for a name and an email address, and " +
        "for whatever else you choose to fill in.\\n\\n" +
        "# What happens to it\\n" +
        "Submissions go to the program's own inbox. They are not published on this " +
        "site, not sold, and not passed to anybody outside the club.\\n\\n" +
        "# Removing your details\\n" +
        "Ask, and we will delete them.\\n\\n" +
        "# Elsewhere\\n" +
        "Links to ticketing, streaming, giving and league sites lead off this site, " +
        "and what those services collect is up to them.",
      accessibility:
        "# What we are aiming for\\n" +
        "This site is built to be usable with a keyboard and with a screen reader: " +
        "text over solid backgrounds, real headings, labelled controls, and images " +
        "that carry a description where one helps.\\n\\n" +
        "# Where it falls short\\n" +
        "Some of it is not there yet. Statistics tables are dense, and archive " +
        "material inherited from elsewhere may be missing descriptions.\\n\\n" +
        "# Tell us\\n" +
        "If any part of this site is hard to use, write to the program and say " +
        "which part. That is the fastest way to get it fixed.",
    },
    /* The home rink, for the Venue page.""")

sub("""const EMPTY_ALUMNI = {""",
    """/* The three footer pages, and the copy that drives each. */
const LEGAL = [
  ["terms", "Terms of Service"],
  ["privacy", "Privacy Policy"],
  ["accessibility", "Accessibility"],
];

/** One of the footer pages. All three are the same page with different copy. */
function LegalPage({ site, which }) {
  const entry = LEGAL.find(([k]) => k === which) || LEGAL[0];
  const body = ((site.settings || {}).legal || {})[entry[0]] || "";
  return (
    <main style={{ background: "var(--page)", minHeight: "50vh" }}>
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="wrap" style={{ maxWidth: 760 }}>
          <h1 className="stitle">{entry[1]}</h1>
          {body
            ? <div className="legalbody">{renderArticle(body, () => {})}</div>
            : (
              <div className="emptybox">
                <p style={{ margin: 0, fontWeight: 700, color: "var(--ink)" }}>Nothing here yet</p>
                <p className="bsm" style={{ margin: "6px 0 0", color: "var(--muted)" }}>
                  This page is written under Settings.
                </p>
              </div>
            )}
        </div>
      </section>
    </main>
  );
}

const EMPTY_ALUMNI = {""")

# ------------------------------------------------------------------ routing
sub("""      {view === "venue" && <VenuePage site={pub} />}""",
    """      {view === "venue" && <VenuePage site={pub} />}
      {LEGAL.some(([k]) => k === view) && <LegalPage site={pub} which={view} />}""")

# --------------------------------------------------------- the footer links
sub("""            {["Terms of Service", "Privacy Policy", "Accessibility"].map((l, i) => (
              <span key={l} className="flegalitem">
                {i > 0 && <span className="fsep" aria-hidden="true">|</span>}
                <span className="flegallink">{l}</span>
              </span>
            ))}""",
    """            {LEGAL.map(([k, label], i) => (
              <span key={k} className="flegalitem">
                {i > 0 && <span className="fsep" aria-hidden="true">|</span>}
                <button className="bsm flegallink flegalbtn" onClick={() => setView(k)}>{label}</button>
              </span>
            ))}""")

# ------------------------------------------------------------------- styling
sub("""/* Console: the logo preview beside a sponsor's fields.""",
    """/* The footer pages: a column of plain prose, nothing else on the screen. */
.legalbody { margin-top: 18px; }
.legalbody h1 { font-family: var(--disp); font-weight: 700; font-size: 21px;
  color: var(--ink); margin: 30px 0 8px; }
.legalbody h1:first-child { margin-top: 0; }
.legalbody p { color: var(--ink); line-height: 1.75; margin: 0 0 14px; }

/* Console: the logo preview beside a sponsor's fields.""")

io.open(p, 'w', encoding='utf-8').write(s)
print('legal + tickets done')
