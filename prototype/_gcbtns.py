# -*- coding: utf-8 -*-
"""One rule for the watch button, one shape for the game-centre pair, and a
ticket on the schedule.

The rules for whether to offer a stream lived inside WatchLink, so the game
centre's own bar - which is not WatchLink - never learned them: it showed a
"Watch live" button next to a date three weeks out, and it went on showing
the stream after the final. The decision moves out into watchOffer(), which
both now ask.

The two buttons in that bar were a navy one and a gold one of whatever width
their words happened to need. They are a pair, so they are cut to one size
and one colour.

And the schedule card gains the ticket, on an upcoming home game only - the
only kind of game that is ours to sell a seat to.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------ the shared decision
sub("""function WatchLink({ game, size, upcoming }) {
  const state = gameState(game);
  const isFinal = state === "final";
  const isLive = state === "live";
  const href = isFinal ? (game.replayUrl || game.streamUrl) : game.streamUrl;
  if (!href || !/^https?:\\/\\//i.test(href)) return null;
  /* Nothing to press until there is something on the end of it. The button
     appears an hour before the puck drops - long enough to go and find it,
     late enough that it is plainly about tonight - and a game with no time
     recorded waits until it is actually live, because there is no hour to
     count back from. */
  if (state === "scheduled") {
    if (!upcoming) return null;
    const start = gameInstant(game.date, game.time);
    if (!start || Date.now() < start.getTime() - 60 * 60 * 1000) return null;
  }
  return (
    <a className={"watchbtn" + (size === "sm" ? " sm" : "") + (isLive ? " islive" : "")}
      href={href} target="_blank" rel="noreferrer noopener"
      onClick={(e) => e.stopPropagation()}>
      {isFinal ? "Replay" : "Watch Live"}
      {isFinal ? <IcPlayCircle size={size === "sm" ? 14 : 17} />
        : isLive ? <span className="livedot" aria-hidden="true" />
        : <span className="watchdot" aria-hidden="true" />}
    </a>
  );
}""",
    """/**
 * What a game's watch button should be right now, or null for nothing.
 *
 * One decision, in one place, because two places to decide it is two places
 * to get it wrong - which is exactly what happened while the game centre had
 * a copy of its own.
 *
 * `upcoming` says the caller has room to show the link before the game. Even
 * then it waits until an hour before the puck drops: long enough to go and
 * find it, late enough that it is plainly about tonight. A game with no time
 * recorded waits until it is actually live, because there is no hour to
 * count back from.
 */
function watchOffer(game, upcoming) {
  if (!game) return null;
  const state = gameState(game);
  const isFinal = state === "final";
  const isLive = state === "live";
  /* A stream does not vanish at the final horn - it becomes the recording,
     at the same address - so it stands in until a replay link is set. */
  const href = isFinal ? (game.replayUrl || game.streamUrl) : game.streamUrl;
  if (!href || !/^https?:\\/\\//i.test(href)) return null;
  if (state === "scheduled") {
    if (!upcoming) return null;
    const start = gameInstant(game.date, game.time);
    if (!start || Date.now() < start.getTime() - 60 * 60 * 1000) return null;
  }
  return { href, isFinal, isLive, label: isFinal ? "Replay" : "Watch Live" };
}

/** The mark that goes after the label: pulsing on, still off, play for a replay. */
function WatchMark({ offer, size }) {
  if (offer.isFinal) return <IcPlayCircle size={size || 17} />;
  return <span className={offer.isLive ? "livedot" : "watchdot"} aria-hidden="true" />;
}

function WatchLink({ game, size, upcoming }) {
  const offer = watchOffer(game, upcoming);
  if (!offer) return null;
  return (
    <a className={"watchbtn" + (size === "sm" ? " sm" : "") + (offer.isLive ? " islive" : "")}
      href={offer.href} target="_blank" rel="noreferrer noopener"
      onClick={(e) => e.stopPropagation()}>
      {offer.label}
      <WatchMark offer={offer} size={size === "sm" ? 14 : 17} />
    </a>
  );
}""")

# ------------------------------------------------------- the game-centre bar
sub("""  const ticketsUrl = ticketsFor(game, site);
  const stream = /^https?:\\/\\//i.test(game.streamUrl || "") ? game.streamUrl : "";""",
    """  const ticketsUrl = ticketsFor(game, site);
  const offer = watchOffer(game, true);""")

sub("""      {(stream || isHome) && (
        <div className="gpbar">
          {stream && (
            <a className="btn bNavy" href={stream} target="_blank" rel="noreferrer noopener">
              <span className="livedot" aria-hidden="true" />Watch live
            </a>
          )}
          {/* Only a home game is ours to sell a seat to. */}
          {isHome && (
            ticketsUrl
              ? <a className="btn bGold" href={ticketsUrl} target="_blank" rel="noreferrer noopener">
                  <IcTicket size={16} /> Get tickets
                </a>
              : <button className="btn bGold" onClick={() => onTickets && onTickets()}>
                  <IcTicket size={16} /> Get tickets
                </button>
          )}
        </div>
      )}""",
    """      {(offer || isHome) && (
        <div className="gpbar">
          {offer && (
            <a className="btn bNavy" href={offer.href} target="_blank" rel="noreferrer noopener">
              {offer.label} <WatchMark offer={offer} />
            </a>
          )}
          {/* Only a home game is ours to sell a seat to. */}
          {isHome && (
            ticketsUrl
              ? <a className="btn bNavy" href={ticketsUrl} target="_blank" rel="noreferrer noopener">
                  Get tickets <IcTicket size={16} />
                </a>
              : <button className="btn bNavy" onClick={() => onTickets && onTickets()}>
                  Get tickets <IcTicket size={16} />
                </button>
          )}
        </div>
      )}""")

# ---------------------------------------------------- the ticket on the card
sub("""function SchedulePage({ site, onPlayer, onGame }) {""",
    """function SchedulePage({ site, onPlayer, onGame, goto }) {""")

sub("""      {view === "schedule" && <SchedulePage site={pub} onPlayer={openPlayer} onGame={openGame} />}""",
    """      {view === "schedule" && <SchedulePage site={pub} onPlayer={openPlayer} onGame={openGame}
        goto={setView} />}""")

sub("""                      <div className="gameacts">
                        <WatchLink game={g} upcoming />
                        <button className="watchbtn" onClick={() => onGame && onGame(g.id)}>
                          Game center <IcGameCenter size={17} />
                        </button>
                      </div>""",
    """                      <div className="gameacts">
                        <WatchLink game={g} upcoming />
                        {/* Only a home game still to be played is ours to sell a
                            seat to. Straight to the seller where one is set,
                            otherwise to the tickets page and its door prices -
                            the same way the banner and the nav pill behave. */}
                        {!g.result && g.homeAway === "H" && (
                          ticketsFor(g, site)
                            ? <a className="watchbtn" href={ticketsFor(g, site)}
                                target="_blank" rel="noreferrer noopener">
                                Tickets <IcTicket size={16} />
                              </a>
                            : <button className="watchbtn" onClick={() => goto && goto("tickets")}>
                                Tickets <IcTicket size={16} />
                              </button>
                        )}
                        <button className="watchbtn" onClick={() => onGame && onGame(g.id)}>
                          Game center <IcGameCenter size={17} />
                        </button>
                      </div>""")

# -------------------------------------------------------------------- CSS
sub(""".gpbar { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  padding: 20px 0; margin: 0; }
.gpbar .btn { flex: 0 0 auto; }""",
    """.gpbar { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  padding: 20px 0; margin: 0; }
/* A pair, so they are cut to one size rather than to the width of whatever
   each one happens to say. */
.gpbar .btn { flex: 0 0 auto; display: inline-flex; align-items: center;
  justify-content: center; gap: 9px; min-width: 210px; }
.gpbar .btn .livedot { margin-right: 0; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('game centre bar unified, ticket on the card')
