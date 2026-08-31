"""Rebuild the preview as a two-sided page: our side against theirs, in the
order a hockey preview is usually read - who to watch, who is in net, who is
dressed - with the comparison cards under it.

What their side can and cannot fill is decided by the league's feed, not by
the layout: their record and their roster are published, their players'
season stats are not. Anything the feed does not carry prints as a dash and
the section says why, rather than leaving a column that looks broken.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# ------------------------------------------------------- opponent roster
sub("""/** The season a preview should describe: this one once it has games, else the last one that did. */""",
    """/** Their roster, live from the league. Names, numbers and positions - no stats. */
function useOpponentRoster(opponent, achaSeasonId) {
  const [rows, setRows] = useState(null);
  const teamId = opponent && opponent.achaTeamId;
  useEffect(() => {
    if (!teamId || !achaSeasonId) { setRows(null); return; }
    let alive = true;
    fetch("/acha?view=roster&season_id=" + achaSeasonId + "&team_id=" + teamId)
      .then((r) => r.json())
      .then((j) => {
        const holder = j.roster && (Array.isArray(j.roster) ? j.roster[0] : j.roster);
        const secs = (holder && holder.sections) || [];
        const out = [];
        for (const sec of secs) {
          if (/coach/i.test(sec.title || "")) continue;
          for (const d of sec.data || []) {
            out.push({
              id: "acha-" + d.row.player_id,
              number: d.row.tp_jersey_number || "",
              name: d.row.name,
              position: d.row.position,
              height: (d.row.height_hyphenated || "").replace("-", "\\u2032") + (d.row.height_hyphenated ? "\\u2033" : ""),
              weight: d.row.w ? d.row.w + " lbs" : "",
              shoots: d.row.shoots || d.row.catches || "",
              hometown: (d.row.hometown || "").replace(/,\\s*United States$/, ""),
            });
          }
        }
        if (alive) setRows(out);
      })
      .catch(() => { if (alive) setRows(null); });
    return () => { alive = false; };
  }, [teamId, achaSeasonId]);
  return rows;
}

/** The season a preview should describe: this one once it has games, else the last one that did. */""")

# --------------------------------------------------------- the new layout
OLD = """  return (
    <>
      {(stream || isHome) && (
        <div className="gpbar">"""
NEW = """  const theirRoster = useOpponentRoster(opponentRec, form.season.achaSeasonId);
  const [rosterSide, setRosterSide] = useState("us");
  const usAbbr = ((site.settings && site.settings.org) || {}).abbr || gameName(site);
  const themName = game.opponentShort || game.opponent;

  /* Their leaders are not in the league's feed - only ours are computed. The
     right-hand side of each row is therefore empty, and says so once at the
     foot of the section rather than three times inside it. */
  const H2H = [
    ["Points", watch.find(([l]) => l === "Points"), (t) => (t.g || 0) + (t.a || 0)],
    ["Goals", watch.find(([l]) => l === "Goals"), (t) => t.g || 0],
    ["Assists", watch.find(([l]) => l === "Assists"), (t) => t.a || 0],
  ].filter(([, x]) => x);

  const posOf = (p) => (p.position === "D" || p.position === "G" ? p.position : p.spot || "F");
  const theirGoalies = (theirRoster || []).filter((p) => p.position === "G").slice(0, 2);
  const rosterRows = rosterSide === "us"
    ? (src.roster || []).map((p) => ({ p, t: boxScoreTotals(site, src, p) || p.stats || {}, mine: true }))
    : (theirRoster || []).map((p) => ({ p, t: null, mine: false }));

  return (
    <>
      {(stream || isHome) && (
        <div className="gpbar">"""
sub(OLD, NEW)

# Replace the old single-sided cards with the two-sided sections.
OLD2 = """    <div className="gcgrid">
      <div className="gccol">
        <GameStory story={story} label="Preview" openPost={openPost} />
        <section className="statcard gcpad">
          <h2 className="statsec">
            Players to watch
            <span className="gcserieslead">{note}</span>
          </h2>
          {watch.length ? (
            <div className="gpwatch">
              {watch.map(([label, x, val]) => (
                <button className="gpwatchcard" key={label} onClick={() => onPlayer(x.p.id)}>
                  <PlayerAvatar size={64} photo={x.p.photo} />
                  <span className="gpwatchlab">{label}</span>
                  <span className="gpplayername">{x.p.name}</span>
                  <span className="gpplayermeta">
                    <strong>{val(x.t)}</strong> · {(x.t.g || 0)}G {(x.t.a || 0)}A in {x.t.gp || 0} GP
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <p className="bsm gcnone">No scoring on file for {note}.</p>
          )}
        </section>

        <section className="statcard gcpad">
          <h2 className="statsec">
            Goaltending
            <span className="gcserieslead">{note}</span>
          </h2>
          {netminders.length ? (
            <div className="twrap">
              <table className="stats gcbt">
                <thead>
                  <tr><th>#</th><th>Goaltender</th><th>GP</th><th>SV</th><th>GA</th>
                    <th title="Goals against average">GAA</th>
                    <th title="Save percentage">SV%</th><th>SO</th></tr>
                </thead>
                <tbody>
                  {netminders.map(({ p, k }) => (
                    <tr key={p.id}>
                      <td>{p.number}</td>
                      <td className="gcbtname">
                        <button className="pboxname" onClick={() => onPlayer(p.id)}>{p.name}</button>
                      </td>
                      <td>{k.gp}</td>
                      <td>{k.svText}</td>
                      <td>{k.gaText}</td>
                      <td>{k.gaa === null ? "\\u2014" : k.gaa.toFixed(2)}</td>
                      <td className="gcbtpts">{pctText(k.svpct)}</td>
                      <td>{k.so}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="bsm gcnone">No goaltending on file for {note}.</p>
          )}
        </section>

        {!!ROSTER_ROWS.length && (
          <section className="statcard gcpad">
            <h2 className="statsec">
              Roster
              <span className="gcserieslead">{note}</span>
            </h2>
            <dl className="gcinfo">
              {ROSTER_ROWS.flatMap(([k, v]) => [<dt key={k + "d"}>{k}</dt>, <dd key={k + "v"}>{v}</dd>])}
            </dl>
          </section>
        )}
      </div>
      <div className="gccol">"""

NEW2 = """    {!!H2H.length && (
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
              <span className="h2hnum empty">\\u2014</span>
              <span className="h2hplayer empty">
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={44} />}
                <span className="h2hnames">
                  <span className="h2hname">Not published</span>
                  <span className="h2hpos">{themName}</span>
                </span>
              </span>
            </div>
          );
        })}
        <p className="bsm gcnone gpnote">
          The league publishes their schedule and roster but not their players' season
          totals, so only Cal's leaders can be shown.
        </p>
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
            <span><strong>{team.gapg == null ? "\\u2014" : team.gapg}</strong>GA/GP</span>
          </div>
          {netminders.map(({ p, k }) => (
            <button className="gtcard" key={p.id} onClick={() => onPlayer(p.id)}>
              <span className="gtname">{p.name}<span className="gtnum">#{p.number || "\\u2014"}</span></span>
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
          <p className="gtteam">{themName}</p>
          <div className="gtline">
            <span><strong>{opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : "\\u2014"}</strong>W-L</span>
            <span><strong>{opp.data ? opp.data.gapg : "\\u2014"}</strong>GA/GP</span>
          </div>
          {theirGoalies.length ? theirGoalies.map((p) => (
            <div className="gtcard" key={p.id}>
              <span className="gtname">{p.name}<span className="gtnum">#{p.number || "\\u2014"}</span></span>
              <span className="gtline">
                <span><strong>\\u2014</strong>GP</span>
                <span><strong>\\u2014</strong>GAA</span>
                <span><strong>\\u2014</strong>SV%</span>
                <span><strong>\\u2014</strong>SO</span>
              </span>
            </div>
          )) : <p className="bsm gcnone">{opp.loading ? "Loading\\u2026" : "No roster published."}</p>}
        </div>
      </div>
    </section>

    <section className="statcard gcpad gpwide">
      <h2 className="statsec">
        Roster
        <span className="gcserieslead">{note}</span>
      </h2>
      <div className="tabs" style={{ marginBottom: 14 }}>
        <button className={"tab " + (rosterSide === "us" ? "on" : "")}
          onClick={() => setRosterSide("us")}>{usAbbr}</button>
        <button className={"tab " + (rosterSide === "them" ? "on" : "")}
          onClick={() => setRosterSide("them")}>{themName}</button>
      </div>
      {rosterRows.length ? (
        <div className="twrap">
          <table className="stats gcbt">
            <thead>
              <tr>
                <th>#</th><th>Player</th><th>Pos</th>
                <th>GP</th><th>G</th><th>A</th><th>P</th><th>PIM</th>
              </tr>
            </thead>
            <tbody>
              {[...rosterRows]
                .sort((a, b) => (a.p.position === "G") - (b.p.position === "G")
                  || (b.t ? ((b.t.g || 0) + (b.t.a || 0)) - ((a.t.g || 0) + (a.t.a || 0)) : 0)
                  || (Number(a.p.number) || 99) - (Number(b.p.number) || 99))
                .map(({ p, t, mine }) => (
                <tr key={p.id}>
                  <td>{p.number}</td>
                  <td className="gcbtname">
                    {mine
                      ? <button className="pboxname" onClick={() => onPlayer(p.id)}>{p.name}</button>
                      : p.name}
                  </td>
                  <td className="gcbtspot">{posOf(p)}</td>
                  <td>{t ? (t.gp || 0) : "\\u2014"}</td>
                  <td>{t ? (t.g || 0) : "\\u2014"}</td>
                  <td>{t ? (t.a || 0) : "\\u2014"}</td>
                  <td className="gcbtpts">{t ? (t.g || 0) + (t.a || 0) : "\\u2014"}</td>
                  <td>{t ? (t.pim || 0) : "\\u2014"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="bsm gcnone">{rosterSide === "them" ? "No roster published." : "No roster on file."}</p>
      )}
      {rosterSide === "them" && (
        <p className="bsm gcnone gpnote">
          Their roster is live from the league; it carries no season totals.
        </p>
      )}
    </section>

    <div className="gcgrid">
      <div className="gccol">
        <GameStory story={story} label="Preview" openPost={openPost} />"""
sub(OLD2, NEW2)

io.open(p, 'w', encoding='utf-8').write(s)
print('layout done')
