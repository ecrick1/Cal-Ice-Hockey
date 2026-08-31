# -*- coding: utf-8 -*-
"""Lay the preview out the way the rest of the game centre already is.

Two columns, the same grid a live or finished game uses, so moving between
the three states of the page does not feel like moving between three pages.
Players to watch takes the comparison bar from Game stats - the same two team
colours meeting on a slant - because it is the same act: setting one side's
number against the other's. Goaltenders get faces.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# --------------------------------------------------------- team colours
sub("""  const isHome = game.homeAway === "H";""",
    """  /* The same two colours the Game stats bars use, so a bar means the same
     thing whichever state of the page it is on. */
  const org = (site.settings && site.settings.org) || {};
  const usColor = org.primary || "#041E42";
  const themColor = (opponentRec && opponentRec.color) || "#5A6473";

  const isHome = game.homeAway === "H";""")

# ------------------------------------------- rebuild the three sections
OLD = """    {!!H2H.length && (
      <section className="statcard gcpad gpwide">
        <h2 className="statsec">
          Players to watch
          <span className="gcserieslead">{note}</span>
        </h2>
        <div className="h2hhead">
          <span>{usAbbr}</span><span /><span>{themName}</span>
        </div>
        {H2H.map(([label, entry, val]) => {
          const x = entry[1];
          return (
            <div className="h2hrow" key={label}>
              <button className="h2hplayer" onClick={() => onPlayer(x.p.id)}>
                <PlayerAvatar size={44} photo={x.p.photo} />
                <span className="h2hnames">
                  <span className="h2hname">{x.p.name}</span>
                  <span className="h2hpos">#{x.p.number || "\\u2014"} · {posOf(x.p)}</span>
                </span>
              </button>
              <span className="h2hnum">{val(x.t)}</span>
              <span className="h2hcat">{label}</span>
              <span className={"h2hnum" + (THEIRS[label] ? "" : " empty")}>
                {THEIRS[label] ? theirValue[label](THEIRS[label]) : "—"}
              </span>
              <span className="h2hplayer empty">
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={44} />}
                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? " known" : "")}>
                    {THEIRS[label] ? THEIRS[label].name : "Not published"}
                  </span>
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? (THEIRS[label].pos || "") + " · " + (THEIRS[label].gp || 0) + " GP"
                      : themName}
                  </span>
                </span>
              </span>
            </div>
          );
        })}
        {!theirStats && (
          <p className="bsm gcnone gpnote">
            {live.loading
              ? "Reading their season from the league\\u2026"
              : "The league has no box scores for them this season. Paste their totals under Opponents and they appear here."}
          </p>
        )}
      </section>
    )}

    <section className="statcard gcpad gpwide">
      <h2 className="statsec">
        Goaltending
        <span className="gcserieslead">{note}</span>
      </h2>
      <div className="gtgrid">
        <div className="gtside">
          <p className="gtteam">{usAbbr}</p>
          <div className="gtline">
            <span><strong>{us.w}-{us.l}{us.t ? "-" + us.t : ""}</strong>W-L{us.t ? "-T" : ""}</span>
            <span><strong>{team.gapg == null ? "—" : team.gapg}</strong>GA/GP</span>
          </div>
          {netminders.map(({ p, k }) => (
            <button className="gtcard" key={p.id} onClick={() => onPlayer(p.id)}>
              <span className="gtname">{p.name}<span className="gtnum">#{p.number || "\\u2014"}</span></span>
              <span className="gtline">
                <span><strong>{k.gp}</strong>GP</span>
                <span><strong>{k.gaa === null ? "—" : k.gaa.toFixed(2)}</strong>GAA</span>
                <span><strong>{pctText(k.svpct)}</strong>SV%</span>
                <span><strong>{k.so}</strong>SO</span>
              </span>
            </button>
          ))}
        </div>
        <div className="gtside">
          <p className="gtteam">{themName}</p>
          <div className="gtline">
            <span><strong>{opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : "—"}</strong>W-L</span>
            <span><strong>{opp.data ? opp.data.gapg : "—"}</strong>GA/GP</span>
          </div>
          {(theirStats ? theirStats.goalies.slice(0, 2).map((p) => {
            /* A pasted row already carries the rates; an aggregated one
               carries saves and goals against, so the rates come from those. */
            if (p.gaa != null || p.svpct != null) return p;
            const faced = (p.saves || 0) + (p.ga || 0);
            return { ...p,
              gaa: p.gp ? ((p.ga || 0) / p.gp).toFixed(2) : null,
              svpct: faced ? (p.saves / faced).toFixed(3).replace(/^0/, "") : null };
          }) : theirGoalies).map((p, i) => (
            <div className="gtcard" key={p.id || p.name || i}>
              <span className="gtname">{p.name}
                <span className="gtnum">
                  {p.number ? "#" + p.number
                    : (theirGoalies.find((g) => g.name === p.name) || {}).number
                      ? "#" + theirGoalies.find((g) => g.name === p.name).number : ""}
                </span>
              </span>
              <span className="gtline">
                <span><strong>{p.gp == null ? "—" : p.gp}</strong>GP</span>
                <span><strong>{p.gaa == null ? "—" : p.gaa}</strong>GAA</span>
                <span><strong>{p.svpct == null ? "—" : String(p.svpct).replace(/^0/, "")}</strong>SV%</span>
                <span><strong>{p.so == null ? "—" : p.so}</strong>SO</span>
              </span>
            </div>
          ))}
          {!theirStats && !theirGoalies.length && (
            <p className="bsm gcnone">{opp.loading ? "Loading\\u2026" : "No roster published."}</p>
          )}
        </div>
      </div>
    </section>

    <section className="statcard gcpad gpwide">
      <h2 className="statsec">
        Roster
        <span className="gcserieslead">{note}</span>
      </h2>"""

NEW = """    <div className="gcgrid">
      <div className="gccol">
      <GameStory story={story} label="Preview" openPost={openPost} />
      {!!H2H.length && (
      <section className="statcard gcpad">
        <div className="gcstatshead">
          {org.logo
            ? <img className="gcstatslogo" src={org.logo} alt="" />
            : <OppBadge name={usAbbr} size={30} />}
          <h2 className="statsec" style={{ margin: 0 }}>Players to watch</h2>
          {game.opponentLogo
            ? <img className="gcstatslogo" src={game.opponentLogo} alt="" />
            : <OppBadge name={themName} size={30} />}
        </div>
        <p className="bsm gcnone" style={{ marginTop: -6, marginBottom: 14 }}>{note}</p>
        {H2H.map(([label, entry, val]) => {
          const x = entry[1];
          const a = val(x.t);
          const them = THEIRS[label] ? theirValue[label](THEIRS[label]) : null;
          const t = a + (them || 0);
          const pa = t ? (a / t) * 100 : 50;
          return (
            <div className="gcbar h2hbar" key={label}>
              <button className="h2hface" onClick={() => onPlayer(x.p.id)}>
                <PlayerAvatar size={38} photo={x.p.photo} />
                <span className="h2hnames">
                  <span className="h2hname">{x.p.name}</span>
                  <span className="h2hpos">#{x.p.number || "\\u2014"} · {posOf(x.p)}</span>
                </span>
              </button>
              <span className="gcbarlab">{label}</span>
              <span className="h2hface right">
                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? "" : " unknown")}>
                    {THEIRS[label] ? THEIRS[label].name : "Not published"}
                  </span>
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? (THEIRS[label].pos || "") + " · " + (THEIRS[label].gp || 0) + " GP"
                      : themName}
                  </span>
                </span>
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={38} />}
              </span>
              <span className="gcbarval">{a}</span>
              <span className="gcbarval right">{them == null ? "\\u2014" : them}</span>
              <span className="gcbartrack">
                {them == null ? <span className="gcbarnone" /> : (
                  <>
                    <span className="gcbarfill left" style={{ width: pa + "%", background: usColor }} />
                    <span className="gcbarfill right" style={{ width: (100 - pa) + "%", background: themColor }} />
                  </>
                )}
              </span>
            </div>
          );
        })}
        {!theirStats && (
          <p className="bsm gcnone gpnote">
            {live.loading
              ? "Reading their season from the league\\u2026"
              : "The league has no box scores for them this season. Paste their totals under Opponents and they appear here."}
          </p>
        )}
      </section>
      )}

      <section className="statcard gcpad">
        <div className="gcstatshead">
          {org.logo
            ? <img className="gcstatslogo" src={org.logo} alt="" />
            : <OppBadge name={usAbbr} size={30} />}
          <h2 className="statsec" style={{ margin: 0 }}>Goaltending</h2>
          {game.opponentLogo
            ? <img className="gcstatslogo" src={game.opponentLogo} alt="" />
            : <OppBadge name={themName} size={30} />}
        </div>
        <div className="gtgrid">
          <div className="gtside">
            <div className="gtline gtteamline">
              <span><strong>{us.w}-{us.l}{us.t ? "-" + us.t : ""}</strong>W-L{us.t ? "-T" : ""}</span>
              <span><strong>{team.gapg == null ? "\\u2014" : team.gapg}</strong>GA/GP</span>
            </div>
            {netminders.map(({ p, k }) => (
              <button className="gtcard" key={p.id} onClick={() => onPlayer(p.id)}>
                <span className="gthead">
                  <PlayerAvatar size={42} photo={p.photo} />
                  <span className="gtnames">
                    <span className="gtname">{p.name}</span>
                    <span className="gtnum">#{p.number || "\\u2014"}</span>
                  </span>
                </span>
                <span className="gtline">
                  <span><strong>{k.gp}</strong>GP</span>
                  <span><strong>{k.gaa === null ? "\\u2014" : k.gaa.toFixed(2)}</strong>GAA</span>
                  <span><strong>{pctText(k.svpct)}</strong>SV%</span>
                  <span><strong>{k.so}</strong>SO</span>
                </span>
              </button>
            ))}
          </div>
          <div className="gtside">
            <div className="gtline gtteamline">
              <span><strong>{opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : "\\u2014"}</strong>W-L</span>
              <span><strong>{opp.data ? opp.data.gapg : "\\u2014"}</strong>GA/GP</span>
            </div>
            {(theirStats ? theirStats.goalies.slice(0, 2).map((p) => {
              /* A pasted row already carries the rates; an aggregated one
                 carries saves and goals against, so the rates come from those. */
              if (p.gaa != null || p.svpct != null) return p;
              const faced = (p.saves || 0) + (p.ga || 0);
              return { ...p,
                gaa: p.gp ? ((p.ga || 0) / p.gp).toFixed(2) : null,
                svpct: faced ? (p.saves / faced).toFixed(3).replace(/^0/, "") : null };
            }) : theirGoalies).map((p, i) => {
              const num = p.number || (theirGoalies.find((g) => g.name === p.name) || {}).number;
              return (
                <div className="gtcard" key={p.id || p.name || i}>
                  <span className="gthead">
                    {/* No headshot for a visiting keeper, so their crest
                        stands in rather than an empty grey circle. */}
                    {game.opponentLogo
                      ? <img className="gtmark" src={game.opponentLogo} alt="" />
                      : <OppBadge name={themName} size={42} />}
                    <span className="gtnames">
                      <span className="gtname">{p.name}</span>
                      <span className="gtnum">{num ? "#" + num : ""}</span>
                    </span>
                  </span>
                  <span className="gtline">
                    <span><strong>{p.gp == null ? "\\u2014" : p.gp}</strong>GP</span>
                    <span><strong>{p.gaa == null ? "\\u2014" : p.gaa}</strong>GAA</span>
                    <span><strong>{p.svpct == null ? "\\u2014" : String(p.svpct).replace(/^0/, "")}</strong>SV%</span>
                    <span><strong>{p.so == null ? "\\u2014" : p.so}</strong>SO</span>
                  </span>
                </div>
              );
            })}
            {!theirStats && !theirGoalies.length && (
              <p className="bsm gcnone">{opp.loading ? "Loading\\u2026" : "No roster published."}</p>
            )}
          </div>
        </div>
      </section>

      <section className="statcard gcpad">
        <h2 className="statsec">
          Roster
          <span className="gcserieslead">{note}</span>
        </h2>"""
sub(OLD, NEW)

# The roster section used to close the wide run and open the grid; now the
# grid is already open, so it just closes itself.
sub("""      {rosterSide === "them" && (
        <p className="bsm gcnone gpnote">
          {theirStats
            ? "Roster and totals live from the league" + (theirStats.games ? " \\u2014 " + theirStats.games + " games" : "")
              + ". A player with no line in any box score shows dashes."
            : "Their roster is live from the league; it carries no season totals."}
        </p>
      )}
    </section>

    <div className="gcgrid">
      <div className="gccol">
        <GameStory story={story} label="Preview" openPost={openPost} />""",
    """        {rosterSide === "them" && (
          <p className="bsm gcnone gpnote">
            {theirStats
              ? "Roster and totals live from the league" + (theirStats.games ? " \\u2014 " + theirStats.games + " games" : "")
                + ". A player with no line in any box score shows dashes."
              : "Their roster is live from the league; it carries no season totals."}
          </p>
        )}
      </section>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('restructured')
