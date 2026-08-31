"""Add the Venue page: seed data, icons, the page, the nav entries and the
admin fields that make it editable.

The facts are real and sourced: oaklandice.com for the address, phone, sheets
and parking rules; BART for the ride from campus. Nothing about the building
is invented, and anything the club has not said is simply absent.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90])
    s = s.replace(old, new)


# ---------------------------------------------------------------- seed data
sub(
    """    ticketsUrl: "", contactEmail: "", homeVenue: "Oakland Ice Center", siteUrl: "",""",
    """    ticketsUrl: "", contactEmail: "", homeVenue: "Oakland Ice Center", siteUrl: "",
    /* The home rink, for the Venue page. Everything here is published by the
     * rink or by BART - a club site should not be guessing at somebody's
     * opening hours or fares, so what is not known is left out. */
    venue: {
      name: "Oakland Ice Center",
      address: "519 18th Street, Oakland, CA 94612",
      phone: "(510) 268-9000",
      website: "https://www.oaklandice.com",
      mapUrl: "https://www.google.com/maps/dir/?api=1&destination=519+18th+Street,+Oakland,+CA+94612",
      about:
        "Cal plays its home games at the Oakland Ice Center, a two-sheet rink in "
        "downtown Oakland run by Sharks Sports & Entertainment, the company behind "
        "the San Jose Sharks. It opened in 1995 and has an NHL-size sheet at "
        "200 by 85 feet and an Olympic sheet at 200 by 100.\\n\\n"
        "It is a public rink the rest of the week, so the building is shared with "
        "figure skating, broomball, curling and open skate sessions.",
      directions: [
        { mode: "BART", icon: "train",
          body:
            "The 19th Street Oakland station is less than a block from the door, "
            "which makes this the easy way in from campus.\\n\\n"
            "From Downtown Berkeley take a Richmond-line train toward Oakland and "
            "get off at 19th Street - three stops, no transfer, about nine minutes. "
            "Trains run roughly every fifteen minutes." },
        { mode: "AC Transit", icon: "bus",
          body:
            "The rink sits among the downtown Oakland bus stops. Routes and times "
            "are on the AC Transit site; the useful stop is whichever one puts you "
            "on Broadway around 19th." },
        { mode: "Driving and parking", icon: "car",
          body:
            "Park at the Dalziel Garage on 16th Street between Clay and San Pablo. "
            "Pay through the ParkMobile app and get it validated inside - "
            "validation is free on weekday evenings from 4pm and on Saturdays from "
            "8am, both until 1am.\\n\\n"
            "The garage is closed on Sundays. Street parking and the 18th Street "
            "Uptown lot are free that day." },
      ],
    },""")

# ------------------------------------------------------------------- icons
sub(
    """const IcPin = (p) => <Ic {...p} d={<><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" /></>} />;""",
    """const IcPin = (p) => <Ic {...p} d={<><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" /></>} />;
/* Ways of getting to the rink. Flat strokes in the house style, drawn here
   rather than lifted from a transit agency's own icon set. */
const IcTrain = (p) => <Ic {...p} d={<><rect x="6" y="3" width="12" height="13" rx="3" /><path d="M6 10h12M9 20l-2 2M15 20l2 2M8 16h.01M16 16h.01" /></>} />;
const IcBus = (p) => <Ic {...p} d={<><rect x="4" y="4" width="16" height="12" rx="2" /><path d="M4 11h16M7 20v-2M17 20v-2M8 16h.01M16 16h.01" /></>} />;
const IcCar = (p) => <Ic {...p} d={<><path d="M4 15h16M5 15l1.6-5.2A2 2 0 0 1 8.5 8.4h7a2 2 0 0 1 1.9 1.4L19 15v3.5h-3V17H8v1.5H5Z" /><path d="M7.5 12.5h9" /></>} />;""")

# -------------------------------------------------------------- the page
sub(
    """/* Before the puck drops there is no game to report, so the page offers what
   is useful instead: the two teams' form and who has been scoring. */""",
    """/**
 * The home rink, and how to get to it from campus.
 *
 * Everything comes off `settings.venue` rather than being written into the
 * page, so the club can correct a parking rule without a deploy - and so a
 * field nobody has filled in renders as nothing at all instead of a heading
 * over an empty box.
 */
function VenuePage({ site }) {
  const v = (site.settings || {}).venue || {};
  const icons = { train: IcTrain, bus: IcBus, car: IcCar };
  const ways = (v.directions || []).filter((d) => d && (d.mode || d.body));

  if (!v.name && !v.address && !ways.length) {
    return (
      <main style={{ background: "var(--page)", minHeight: "50vh" }}>
        <section className="section" style={{ paddingTop: 40 }}>
          <div className="wrap" style={{ maxWidth: 900 }}>
            <h1 className="stitle">Venue</h1>
            <div className="emptybox">
              <p style={{ margin: 0, fontWeight: 700, color: "var(--ink)" }}>Nothing here yet</p>
              <p className="bsm" style={{ margin: "6px 0 0", color: "var(--muted)" }}>
                The home rink and how to reach it are set under Settings.
              </p>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main style={{ background: "var(--page)" }}>
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="wrap" style={{ maxWidth: 900 }}>
          <p className="veneyebrow">Home rink</p>
          <h1 className="stitle">{v.name || "Venue"}</h1>

          <div className="venfacts">
            {v.address && (
              <a className="venfact" href={v.mapUrl || undefined}
                target={v.mapUrl ? "_blank" : undefined} rel="noreferrer">
                <IcPin size={17} />
                <span>{v.address}</span>
              </a>
            )}
            {v.phone && (
              <a className="venfact" href={"tel:" + v.phone.replace(/[^\\d+]/g, "")}>
                <IcClock size={17} />
                <span>{v.phone}</span>
              </a>
            )}
            {v.website && (
              <a className="venfact" href={v.website} target="_blank" rel="noreferrer">
                <IcLink size={17} />
                <span>{v.website.replace(/^https?:\\/\\//, "")}</span>
              </a>
            )}
          </div>

          {v.about && <div className="venabout">{renderArticle(v.about, () => {})}</div>}

          {!!ways.length && (
            <>
              <h2 className="venhead">Getting there from campus</h2>
              <div className="vengrid">
                {ways.map((d, i) => {
                  const Icon = icons[d.icon] || IcPin;
                  return (
                    <article className="vencard" key={d.mode || i}>
                      <div className="venmode">
                        <span className="venicon"><Icon size={18} /></span>
                        <h3 className="venmodename">{d.mode}</h3>
                      </div>
                      {d.body && <div className="venbody">{renderArticle(d.body, () => {})}</div>}
                    </article>
                  );
                })}
              </div>
            </>
          )}

          {v.mapUrl && (
            <a className="btn bNavy venmapbtn" href={v.mapUrl} target="_blank" rel="noreferrer">
              <IcPin size={16} /> Directions
            </a>
          )}
        </div>
      </section>
    </main>
  );
}

/* Before the puck drops there is no game to report, so the page offers what
   is useful instead: the two teams' form and who has been scoring. */""")

# ---------------------------------------------------------------- routing
sub(
    """      {view === "recruit" && <RecruitPage""",
    """      {view === "venue" && <VenuePage site={pub} />}
      {view === "recruit" && <RecruitPage""")

# ------------------------------------------------------------ desktop nav
sub(
    """            <button className={`navlink ${view === "schedule" ? "on" : ""}`} onClick={() => setView("schedule")}>Schedule</button>
            <NavMenu label="Team" view={view} setView={setView} items={NAV_TEAM} />""",
    """            <button className={`navlink ${view === "schedule" ? "on" : ""}`} onClick={() => setView("schedule")}>Schedule</button>
            <button className={`navlink ${view === "venue" ? "on" : ""}`} onClick={() => setView("venue")}>Venue</button>
            <NavMenu label="Team" view={view} setView={setView} items={NAV_TEAM} />""")

# ------------------------------------------------------------- mobile nav
sub(
    """            <button className={"navpanelitem" + (view === "schedule" ? " on" : "")}
              onClick={() => goNav("schedule")}>Schedule</button>
""",
    """            <button className={"navpanelitem" + (view === "schedule" ? " on" : "")}
              onClick={() => goNav("schedule")}>Schedule</button>
            <button className={"navpanelitem" + (view === "venue" ? " on" : "")}
              onClick={() => goNav("venue")}>Venue</button>
""")

io.open(p, 'w', encoding='utf-8').write(s)
print('page, icons, seed and nav done')
