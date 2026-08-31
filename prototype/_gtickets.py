# -*- coding: utf-8 -*-
"""A ticket link on the game, not only on the club.

One address for the whole season is right until it isn't: an alumni night
sells through a different page, a tournament through the host's, a rivalry
game through its own event listing. So a game can carry its own link, and
every place that offers a seat asks the game first and the club second.

Blank is the normal state and means what it meant before - use the club's
address.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)


# ------------------------------------------------------------------ helper
sub("""function watchRows(game) {""",
    """/** Where to buy a seat for this game: its own link, else the club's. */
function ticketsFor(game, site) {
  const own = (game || {}).ticketsUrl;
  if (own && /^https?:\\/\\//i.test(own)) return own;
  return ((site || {}).settings || {}).ticketsUrl || "";
}

function watchRows(game) {""")

# --------------------------------------------------------- the game preview
sub("""  const ticketsUrl = (site.settings || {}).ticketsUrl;
  const stream = /^https?:\\/\\//i.test(game.streamUrl || "") ? game.streamUrl : "";""",
    """  const ticketsUrl = ticketsFor(game, site);
  const stream = /^https?:\\/\\//i.test(game.streamUrl || "") ? game.streamUrl : "";""")

# ------------------------------------------------------------- the calendar
sub("""                      {!r && g.homeAway === "H" && ticketsUrl && (
                        <a className="calact" href={ticketsUrl}""",
    """                      {!r && g.homeAway === "H" && (g.ticketsUrl || ticketsUrl) && (
                        <a className="calact" href={g.ticketsUrl || ticketsUrl}""")

# ------------------------------------------------------------ the home page
sub("""                {featureState === "scheduled" && feature.homeAway === "H" && (
                  ticketsUrl
                    ? <a className="btn bGold bSm" href={ticketsUrl} target="_blank" rel="noreferrer">""",
    """                {featureState === "scheduled" && feature.homeAway === "H" && (
                  ticketsFor(feature, site)
                    ? <a className="btn bGold bSm" href={ticketsFor(feature, site)}
                        target="_blank" rel="noreferrer">""")

# ------------------------------------------------------------ console field
sub("""                <div className="field">
                  <label className="h6">Live stream</label>
                  <UrlField value={g.streamUrl || ""}""",
    """                <div className="field">
                  <label className="h6">Tickets</label>
                  <UrlField value={g.ticketsUrl || ""}
                    placeholder="https://…"
                    onChange={(v) => setGame(g.id, { ticketsUrl: v })} />
                  <p className="bsm" style={{ color: "var(--au-faint)", marginTop: 5 }}>
                    Only for a game that sells somewhere other than the usual
                    place. Leave it blank and this game uses the club's tickets
                    address from Settings.
                  </p>
                </div>
                <div className="field">
                  <label className="h6">Live stream</label>
                  <UrlField value={g.streamUrl || ""}""")

# A new game carries the field, empty, like the other two links.
sub("""            gameType: "regular", roundLabel: "", streamUrl: "", replayUrl: "", result: null,""",
    """            gameType: "regular", roundLabel: "", ticketsUrl: "", streamUrl: "", replayUrl: "",
            result: null,""")

io.open(p, 'w', encoding='utf-8').write(s)
print('per-game tickets wired')
