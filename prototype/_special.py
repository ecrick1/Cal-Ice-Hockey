"""Specialty games: a name a fixture is known by.

Two sources. An opponent can carry a rivalry name, which applies to every game
against them - Stanford is always the Big Freeze. A single game can carry its
own, for the ones that move: Senior Night, an alumni game, a teddy bear toss.
A game can have both.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------------------- hydrate
sub("""        opponentLogo: o ? oppLogo(o, "light") : null,
        opponentLogoDark: o ? oppLogo(o, "dark") : null,
      };""",
    """        opponentLogo: o ? oppLogo(o, "light") : null,
        opponentLogoDark: o ? oppLogo(o, "dark") : null,
        /* What this fixture is known as. The opponent's standing name first,
           then anything this one game carries - a Senior Night against
           Stanford is both. */
        specials: [...new Set([(o && o.rivalry) || "", g.special || ""].filter(Boolean))],
      };""")

# ---------------------------------------------------------------- styling
sub("""/* The footer pages: a column of plain prose, nothing else on the screen. */""",
    """/* A game that goes by a name. Gold, because it is the thing on the schedule
   worth spotting from across the page. */
.spectag { display: inline-flex; align-items: center; gap: 5px; border-radius: 999px;
  background: var(--gold); color: var(--deep); padding: 2px 10px;
  font-family: var(--body); font-weight: 800; font-size: 11.5px;
  letter-spacing: 0; white-space: nowrap; }
.spectags { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 5px; }
/* On navy the gold would shout over the score, so it outlines instead. */
.hnext .spectag, .sboard .spectag { background: transparent; color: var(--gold);
  box-shadow: inset 0 0 0 1.5px var(--gold); }

/* The footer pages: a column of plain prose, nothing else on the screen. */""")

# ------------------------------------------------------ the schedule row
sub("""                        <p style={{ margin: 0, fontWeight: 700, fontSize: 17, color: "var(--ink)" }}>{g.opponent}</p>""",
    """                        {!!(g.specials || []).length && (
                          <div className="spectags">
                            {g.specials.map((n) => <span className="spectag" key={n}>{n}</span>)}
                          </div>
                        )}
                        <p style={{ margin: 0, fontWeight: 700, fontSize: 17, color: "var(--ink)" }}>{g.opponent}</p>""")

# ------------------------------------------------------- the home banner
sub("""                <span className="hnextlabel">""",
    """                {!!(feature.specials || []).length && (
                  <div className="spectags">
                    {feature.specials.map((n) => <span className="spectag" key={n}>{n}</span>)}
                  </div>
                )}
                <span className="hnextlabel">""")

# --------------------------------------------------------- the game page
sub("""                <span className="gctag">{game.roundLabel || gameType(game)}</span>""",
    """                <span className="gctag">{game.roundLabel || gameType(game)}</span>
                {(game.specials || []).map((n) => <span className="spectag" key={n}>{n}</span>)}""")

# ------------------------------------------------------ the calendar cell
sub("""                    {g.gameType && g.gameType !== "regular" && (
                      <span className="caltag">{g.roundLabel || gameType(g)}</span>
                    )}""",
    """                    {(g.specials || []).length
                      ? <span className="caltag spec">{g.specials[0]}</span>
                      : g.gameType && g.gameType !== "regular" && (
                        <span className="caltag">{g.roundLabel || gameType(g)}</span>
                      )}""")

sub(""".spectags { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 5px; }""",
    """.spectags { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 5px; }
.caltag.spec { background: var(--gold); color: var(--deep); }""")

# ------------------------------------------------- console: the game field
sub("""                <div className="field">
                  <label className="h6">Officials</label>""",
    """                <div className="field">
                  <label className="h6">Special game</label>
                  <input value={g.special || ""} placeholder="Senior Night · Alumni Game"
                    onChange={(e) => setGame(g.id, { special: e.target.value })} />
                  <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                    Shown as a gold tag on the schedule, the game page and the home
                    page. For a name that applies every year, set it on the opponent
                    instead — both show if a game has both.
                  </p>
                </div>
                <div className="field">
                  <label className="h6">Officials</label>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('special done')
