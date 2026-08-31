"""Neutral-site games, and the plumbing that has to know about them."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ---------------------------------------------------------------- vsAt
sub("""/**
 * "vs" or "at" for a game, and neither when nobody recorded which it was.
 *
 * A schedule reconstructed from a third party can carry the date, the
 * opponent and the score without saying whose rink it was played on. Reading
 * "not home" as "away" would put fifty road games on the record that nobody
 * ever claimed, so an unset venue prints as nothing at all.
 */
const vsAt = (g) => (g.homeAway === "H" ? "vs" : g.homeAway === "A" ? "at" : "");""",
    """/**
 * "vs" or "at" for a game, and neither when nobody recorded which it was.
 *
 * Four states, not two. A schedule reconstructed from a third party can carry
 * the date, the opponent and the score without saying whose rink it was
 * played on; reading "not home" as "away" would put fifty road games on the
 * record that nobody ever claimed, so an unset venue prints as nothing at
 * all. A neutral site takes "vs" - nobody is the visitor at a showcase.
 */
const vsAt = (g) => (g.homeAway === "A" ? "at"
  : g.homeAway === "H" || g.homeAway === "N" ? "vs" : "");
const SIDE_LABEL = { H: "Home", A: "Away", N: "Neutral" };""")

# ------------------------------------------------------------ the badge
sub(""".vsbadge.home { background: var(--blue); color: #FFFFFF; }
.vsbadge.away { background: #DBE0E6; color: #46505A; }""",
    """.vsbadge.home { background: var(--blue); color: #FFFFFF; }
.vsbadge.away { background: #DBE0E6; color: #46505A; }
/* Neither team's building: gold, so a tournament weekend reads as its own
   thing rather than as a run of home games. */
.vsbadge.neutral { background: var(--gold); color: var(--deep); }""")

# The two places that pick the badge class.
sub("""                  {vsAt(g) && <span className={`vsbadge ${g.homeAway === "H" ? "home" : "away"}`}>{vsAt(g)}</span>}""",
    """                  {vsAt(g) && <span className={"vsbadge " + sideClass(g)}>{vsAt(g)}</span>}""")

sub("""                        {vsAt(g) && (
                          <span className={`vsbadge ${g.homeAway === "H" ? "home" : "away"}`}
                            style={{ position: "absolute", right: -8, bottom: -4, width: 22, height: 22, fontSize: 10, border: "2px solid #fff" }}>
                            {vsAt(g)}
                          </span>
                        )}""",
    """                        {vsAt(g) && (
                          <span className={"vsbadge " + sideClass(g)}
                            style={{ position: "absolute", right: -8, bottom: -4, width: 22, height: 22, fontSize: 10, border: "2px solid #fff" }}>
                            {vsAt(g)}
                          </span>
                        )}""")

sub("""const SIDE_LABEL = { H: "Home", A: "Away", N: "Neutral" };""",
    """const SIDE_LABEL = { H: "Home", A: "Away", N: "Neutral" };
const sideClass = (g) => (g.homeAway === "H" ? "home" : g.homeAway === "N" ? "neutral" : "away");""")

# ---------------------------------------------------- the record splits
sub("""  /* A reconstructed schedule can know the score without knowing whose rink it
     was. Those games count toward the record and toward neither split - the
     alternative reads every one of them as a road game. */
  let noVenue = 0;""",
    """  /* Only a home game and a road game belong in the splits. A neutral-site
     game has no rink to credit, and a reconstructed one has no rink recorded -
     both count toward the record and toward neither side. */
  let unsided = 0;""")

sub("""    if (!home && !away) noVenue++;""",
    """    if (!home && !away) unsided++;""")

sub("""    /* Nothing split at all means nobody recorded a venue for any of them, so
       there is no home record to show rather than a run of noughts. */
    home: noVenue === played ? "—" : `${hw}-${hl}${ht ? `-${ht}` : ""}`,
    away: noVenue === played ? "—" : `${aw}-${al}${at ? `-${at}` : ""}`,
    noVenue };""",
    """    /* Every game unsided means there is no home record to show, rather than
       a run of noughts. */
    home: unsided === played ? "—" : `${hw}-${hl}${ht ? `-${ht}` : ""}`,
    away: unsided === played ? "—" : `${aw}-${al}${at ? `-${at}` : ""}`,
    unsided };""")

# ------------------------------------------------------- the table view
sub("""                        <td>{g.homeAway === "H" ? "Home" : g.homeAway === "A" ? "Away" : "—"}</td>""",
    """                        <td>{SIDE_LABEL[g.homeAway] || "—"}</td>""")

# ------------------------------------------------------ the admin select
sub("""              <select value={g.homeAway} onChange={(e) => setGameVenueAware(g, { homeAway: e.target.value })}>
                <option value="H">H</option><option value="A">A</option>""",
    """              <select value={g.homeAway} onChange={(e) => setGameVenueAware(g, { homeAway: e.target.value })}>
                <option value="H">H</option><option value="A">A</option>
                {/* A showcase or a regional: neither team's rink. */}
                <option value="N">N</option>""")

# ------------------------------------------- venue prefill knows nothing
sub("""  const venueFor = (opponentId, homeAway) => {
    if (homeAway === "H") return (site.settings || {}).homeVenue || "";
    const o = (site.opponents || []).find((x) => x.id === opponentId);
    return (o && o.homeVenue) || "";
  };
  const locationFor = (opponentId, homeAway) => {
    if (homeAway === "H") return (site.settings || {}).homeCity || "";
    const o = (site.opponents || []).find((x) => x.id === opponentId);
    return (o && o.homeCity) || "";
  };""",
    """  /* A neutral site is by definition nobody's rink, so there is nothing to
     prefill - it gets typed in. */
  const venueFor = (opponentId, homeAway) => {
    if (homeAway === "N") return "";
    if (homeAway === "H") return (site.settings || {}).homeVenue || "";
    const o = (site.opponents || []).find((x) => x.id === opponentId);
    return (o && o.homeVenue) || "";
  };
  const locationFor = (opponentId, homeAway) => {
    if (homeAway === "N") return "";
    if (homeAway === "H") return (site.settings || {}).homeCity || "";
    const o = (site.opponents || []).find((x) => x.id === opponentId);
    return (o && o.homeCity) || "";
  };""")

# --------------------------------------------------- the schedule filter
sub("""    if (filter === "home") r = r.filter((g) => g.homeAway === "H");""",
    """    if (filter === "neutral") r = r.filter((g) => g.homeAway === "N");
    if (filter === "home") r = r.filter((g) => g.homeAway === "H");""")

sub("""              <option value="all">All Games</option>
              <option value="home">Home</option>
              <option value="away">Away</option>""",
    """              <option value="all">All Games</option>
              <option value="home">Home</option>
              <option value="away">Away</option>
              {/* Only offered when the season actually has one. */}
              {games.some((g) => g.homeAway === "N") && <option value="neutral">Neutral site</option>}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('neutral done')
