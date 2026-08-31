"""Link the footer marks out, and add a sponsors band with a console to fill it."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------------- seed: sponsors
sub("""  staff: [],
  settings: {""",
    """  staff: [],
  /* Filled from the console. Nothing is seeded - inventing a sponsor would be
     putting a real company's name on a claim it never made. */
  sponsors: [],
  settings: {""")

# ------------------------------------------------- the affiliate row list
sub("""const NAV_MORE = [
  ["venue", "Venue"],
  ["alumni", "Alumni"],
];""",
    """const NAV_MORE = [
  ["venue", "Venue"],
  ["alumni", "Alumni"],
];

/* The footer's affiliate marks. Pac-8 has no site of its own yet - the domain
   does not resolve - so it stays an unlinked mark rather than a dead link. */
const AFFILIATES = [
  { src: "/logos/footer-berkeley.svg", alt: "UC Berkeley", href: "https://www.berkeley.edu" },
  { src: "/logos/footer-acha.svg", alt: "ACHA", href: "https://www.achahockey.org", tall: true },
  { mark: "pac8", alt: "Pac-8 Conference" },
  { src: "/logos/footer-nike.svg", alt: "Nike", href: "https://www.nike.com", short: true },
];""")

# ------------------------------------------------------ the footer bands
sub("""        <div className="fband-gold">
          <p className="fcopy">
            © Cal Ice Hockey. All rights reserved.
          </p>
        </div>""",
    """        {!!(pub.sponsors || []).length && (
          <div className="fband-sponsors">
            <div className="wrap">
              <p className="fsponsorlead">Supported by</p>
              <div className="fsponsors">
                {(pub.sponsors || []).map((sp) => {
                  const mark = sp.logo
                    ? <img className="fsponsormark" src={sp.logo} alt={sp.name || "Sponsor"} />
                    : <span className="fsponsorname">{sp.name}</span>;
                  return sp.url ? (
                    <a className="fsponsor" key={sp.id} href={sp.url}
                      target="_blank" rel="noreferrer noopener"
                      title={sp.name || undefined}>{mark}</a>
                  ) : (
                    <span className="fsponsor" key={sp.id} title={sp.name || undefined}>{mark}</span>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        <div className="fband-gold">
          <p className="fcopy">
            © Cal Ice Hockey. All rights reserved.
          </p>
        </div>""")

sub("""        <div className="fband-gray">
          {/* Wordmarks where the club has the asset. The row keeps its own
              muted, desaturated treatment so four marks drawn to four
              different briefs still read as one line. */}
          <span className="faffil">
            <img className="faffilmark" src="/logos/footer-berkeley.svg" alt="UC Berkeley" />
          </span>
          <span className="faffil">
            <img className="faffilmark tall" src="/logos/footer-acha.svg" alt="ACHA" />
          </span>
          <span className="faffil"><Pac8Mark /></span>
          {/* The outfitter sits last, the way a kit supplier's mark does. */}
          <span className="faffil">
            <img className="faffilmark short" src="/logos/footer-nike.svg" alt="Nike" />
          </span>
        </div>""",
    """        <div className="fband-gray">
          {/* Wordmarks where the club has the asset. The row keeps its own
              muted, desaturated treatment so four marks drawn to four
              different briefs still read as one line. */}
          {AFFILIATES.map((a) => {
            const mark = a.mark === "pac8" ? <Pac8Mark /> : (
              <img className={"faffilmark" + (a.tall ? " tall" : "") + (a.short ? " short" : "")}
                src={a.src} alt={a.alt} />
            );
            return a.href ? (
              <a className="faffil" key={a.alt} href={a.href} target="_blank" rel="noreferrer noopener"
                aria-label={a.alt}>{mark}</a>
            ) : (
              <span className="faffil" key={a.alt}>{mark}</span>
            );
          })}
        </div>""")

# ------------------------------------------------------------------ CSS
sub("""/* Footer — Sidearm band stack */""",
    """/* Sponsors — their own band, directly above the copyright line. Paler than
   the affiliate row below it so the two do not read as one long list of
   logos, and each mark keeps its own colour: a sponsor pays to be seen. */
.fband-sponsors { background: #fff; border-top: 1px solid var(--border);
  padding: 24px 24px 26px; }
.fsponsorlead { margin: 0 0 14px; text-align: center; font-family: var(--body);
  font-weight: 700; font-size: 12px; color: var(--muted); }
.fsponsors { display: flex; flex-wrap: wrap; align-items: center;
  justify-content: center; gap: 18px 40px; }
.fsponsor { display: inline-flex; align-items: center; text-decoration: none; }
.fsponsormark { display: block; height: 38px; width: auto; max-width: 190px;
  object-fit: contain; }
.fsponsorname { font-family: var(--body); font-weight: 800; font-size: 16px;
  color: var(--ink); }
a.fsponsor:hover { opacity: 0.75; }
@media (max-width: 640px) {
  .fband-sponsors { padding: 20px 16px; }
  .fsponsors { gap: 16px 26px; }
  .fsponsormark { height: 30px; max-width: 140px; }
}

/* Footer — Sidearm band stack */""")

# The affiliate cells are links now, so they need the box a span had.
sub(""".faffil { color: #8A94A0; font-family: var(--body); font-weight: 700; font-size: 15px;
  padding: 34px 30px; border-left: 1px solid var(--border); filter: grayscale(1);
  display: inline-flex; align-items: center; }""",
    """.faffil { color: #8A94A0; font-family: var(--body); font-weight: 700; font-size: 15px;
  padding: 34px 30px; border-left: 1px solid var(--border); filter: grayscale(1);
  display: inline-flex; align-items: center; text-decoration: none; }
a.faffil:hover { filter: grayscale(0); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('footer done')
