# -*- coding: utf-8 -*-
"""A standing address for the live broadcast.

Watch Live pointed at whichever game happened to be nearest with a link on
it, which meant it went dark in the gaps and, once a game finished, quietly
became a replay button that still said Live. The club's broadcaster gives it
one permanent channel, so that is what the pill is for: a setting, editable
in the console, that wins over any single game's link.

A game's own stream and replay fields are untouched - those are still what
the game center and the schedule read.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)


LIVE = ("https://www.bdehockey.com/free-live.php?con=watchCAL&type=l"
        "&desc=CAL%20Hockey%20-%20University%20of%20California%20Berkeley%20FREE")

# ------------------------------------------------------------------ setting
sub("""    /* The university's own giving page, with the fund already selected. */
    donateUrl: "https://give.berkeley.edu/giftdetails?fund1=FU0852000",""",
    """    /* The university's own giving page, with the fund already selected. */
    donateUrl: "https://give.berkeley.edu/giftdetails?fund1=FU0852000",
    /* The club's channel on its broadcaster, which does not change from
       game to game. Blank falls back to whichever game has a link on it. */
    watchUrl: \"""" + LIVE + """\",""")

# --------------------------------------------------------------- the header
sub("""  const donateUrl = ((site && site.settings) || {}).donateUrl || "";""",
    """  const donateUrl = ((site && site.settings) || {}).donateUrl || "";
  /* The standing channel first. A single game's link is the fallback, and
     only then because a program without a channel still has games. */
  const watchUrl = ((site && site.settings) || {}).watchUrl || "";""")

sub("""            {watchGame
              ? <a className="goldpill navcta" href={watchGame.result ? watchGame.replayUrl : watchGame.streamUrl}
                  target="_blank" rel="noreferrer noopener">Watch Live</a>
              : <button className="goldpill navcta" onClick={() => setView("schedule")}>Watch Live</button>}""",
    """            {watchUrl || watchGame
              ? <a className="goldpill navcta"
                  href={watchUrl || (watchGame.result ? watchGame.replayUrl : watchGame.streamUrl)}
                  target="_blank" rel="noreferrer noopener">Watch Live</a>
              : <button className="goldpill navcta" onClick={() => setView("schedule")}>Watch Live</button>}""")

sub("""              {watchGame
                ? <a className="goldpill" href={watchGame.result ? watchGame.replayUrl : watchGame.streamUrl}
                    target="_blank" rel="noreferrer noopener"
                    onClick={() => setNavOpen(false)}>Watch Live</a>
                : <button className="goldpill" onClick={() => goNav("schedule")}>Watch Live</button>}""",
    """              {watchUrl || watchGame
                ? <a className="goldpill"
                    href={watchUrl || (watchGame.result ? watchGame.replayUrl : watchGame.streamUrl)}
                    target="_blank" rel="noreferrer noopener"
                    onClick={() => setNavOpen(false)}>Watch Live</a>
                : <button className="goldpill" onClick={() => goNav("schedule")}>Watch Live</button>}""")

# ------------------------------------------------------------ console field
sub("""              <div className="field" style={{ marginTop: 16 }}>
                <label className="h6">Public site address</label>""",
    """              <div className="field" style={{ marginTop: 16 }}>
                <label className="h6">Watch live URL</label>
                <input value={st.watchUrl || ""} placeholder="https://…" onChange={setSetting("watchUrl")} />
                <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                  The broadcaster's channel for this club. The Watch Live button goes
                  here whenever it is set; leave it blank and the button falls back to
                  the nearest game with a stream or replay link.
                </p>
              </div>
              <div className="field" style={{ marginTop: 16 }}>
                <label className="h6">Public site address</label>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('watch channel wired')
