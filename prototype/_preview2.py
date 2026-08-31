"""The preview body: watch/tickets bar, players to watch, goaltending, roster,
team stats."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


OLD = """  const leaders = [...(season.roster || [])]
    .map((p) => ({ p, t: boxScoreTotals(site, season, p) || p.stats || {} }))
    .filter((x) => x.p.position !== "G" && ((x.t.g || 0) + (x.t.a || 0)) > 0)
    .sort((a, b) => ((b.t.g || 0) + (b.t.a || 0)) - ((a.t.g || 0) + (a.t.a || 0)))
    .slice(0, 3);

  return (
    <div className="gcgrid">
      <div className="gccol">
        <GameStory story={story} label="Preview" openPost={openPost} />
        <section className="statcard gcpad">
          <h2 className="statsec">Players to watch</h2>
          {leaders.length ? (
            <div className="gpwatch">
              {leaders.map(({ p, t }) => (
                <button className="gpwatchcard" key={p.id} onClick={() => onPlayer(p.id)}>
                  <PlayerAvatar size={64} photo={p.photo} />
                  <span className="gpplayername">{p.name}</span>
                  <span className="gpplayermeta">
                    {(t.g || 0)}G {(t.a || 0)}A · {(t.g || 0) + (t.a || 0)}P
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <p className="bsm gcnone">No scoring recorded yet this season.</p>
          )}
        </section>
      </div>
      <div className="gccol">"""

NEW = """  /* Before a season has been played there is no form to show, so the preview
     describes the year before and labels every card with which year it is. */
  const form = formSeason(site, seasonName);
  const src = form.season;
  const rows = (src.roster || []).map((p) => ({ p, t: boxScoreTotals(site, src, p) || p.stats || {} }));
  const skaters = rows.filter((x) => x.p.position !== "G");

  /* Three categories, so the same player can lead two of them - which is
     itself worth knowing before a game. */
  const best = (key) => {
    const pool = skaters.filter((x) => (key(x.t) || 0) > 0);
    if (!pool.length) return null;
    return pool.sort((a, b) => key(b.t) - key(a.t) || (b.t.g || 0) - (a.t.g || 0))[0];
  };
  const watch = [
    ["Points", best((t) => (t.g || 0) + (t.a || 0)), (t) => (t.g || 0) + (t.a || 0)],
    ["Goals", best((t) => t.g || 0), (t) => t.g || 0],
    ["Assists", best((t) => t.a || 0), (t) => t.a || 0],
  ].filter(([, x]) => x);

  /* The two who carried the net. A qualifying share of the season keeps a
     keeper with one lucky night off the top of the list; if nobody clears it,
     the two who played most stand instead. */
  const keepers = rows.filter((x) => x.p.position === "G" && (x.t.gp || 0) > 0)
    .map((x) => {
      const k = keeperLine(x.t);
      return { ...x, k, faced: k.saves + k.ga };
    });
  const games = (src.schedule || []).filter((g) => g.result).length;
  const qualified = keepers.filter((x) => x.k.gp >= Math.max(1, games * 0.25) && x.faced > 0);
  const netminders = (qualified.length ? qualified.sort((a, b) => (b.k.svpct || 0) - (a.k.svpct || 0))
    : [...keepers].sort((a, b) => b.k.gp - a.k.gp)).slice(0, 2);

  const team = seasonTeamStats(site, src);
  const TEAM_ROWS = [
    ["Power play %", team.pp == null ? "\\u2014" : team.pp + "%"],
    ["Penalty kill %", team.pk == null ? "\\u2014" : team.pk + "%"],
    ["Face-off %", team.fo == null ? "\\u2014" : team.fo + "%"],
    ["GF / GP", team.gfpg == null ? "\\u2014" : team.gfpg],
    ["GA / GP", team.gapg == null ? "\\u2014" : team.gapg],
  ];

  /* Counts only. Heights and weights are known for some seasons and not
     others, so they appear when they are there. */
  const roster = src.roster || [];
  const byPos = (pos) => roster.filter((p) => p.position === pos).length;
  const inches = (h) => {
    const m = String(h || "").match(/(\\d+)\\D+(\\d+)/);
    return m ? Number(m[1]) * 12 + Number(m[2]) : null;
  };
  const heights = roster.map((p) => inches(p.height)).filter(Boolean);
  const weights = roster.map((p) => Number(String(p.weight || "").replace(/\\D/g, ""))).filter(Boolean);
  const avg = (a) => (a.length ? a.reduce((n, x) => n + x, 0) / a.length : null);
  const avgH = avg(heights);
  const avgW = avg(weights);
  const ROSTER_ROWS = [
    ["Players", roster.length],
    ["Forwards", byPos("F")],
    ["Defense", byPos("D")],
    ["Goaltenders", byPos("G")],
    ...(avgH ? [["Average height", Math.floor(avgH / 12) + "\\u2032" + Math.round(avgH % 12) + "\\u2033"]] : []),
    ...(avgW ? [["Average weight", Math.round(avgW) + " lbs"]] : []),
  ].filter(([, v]) => v);

  const isHome = game.homeAway === "H";
  const ticketsUrl = (site.settings || {}).ticketsUrl;
  const stream = /^https?:\\/\\//i.test(game.streamUrl || "") ? game.streamUrl : "";
  const note = form.prior ? form.name + " season" : seasonName + " season";

  return (
    <>
      {(stream || isHome) && (
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
      )}
    <div className="gcgrid">
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
              {ROSTER_ROWS.map(([k, v]) => <React.Fragment key={k}><dt>{k}</dt><dd>{v}</dd></React.Fragment>)}
            </dl>
          </section>
        )}
      </div>
      <div className="gccol">
        <section className="statcard gcpad">
          <h2 className="statsec">
            Team stats
            <span className="gcserieslead">{note}{team.gp ? " \\u00b7 " + team.gp + " GP" : ""}</span>
          </h2>
          <dl className="gcinfo">
            {TEAM_ROWS.map(([k, v]) => <React.Fragment key={k}><dt>{k}</dt><dd>{v}</dd></React.Fragment>)}
          </dl>
        </section>"""

sub(OLD, NEW)

# Close the fragment the bar opened.
sub("""            <dt>Type</dt>
            <dd>{game.roundLabel || GAME_TYPE_LABEL[gameType(game)] || gameType(game)}</dd>
          </dl>
        </section>
      </div>
    </div>
  );
}

/* One row of the lineup sheet.""",
    """            <dt>Type</dt>
            <dd>{game.roundLabel || GAME_TYPE_LABEL[gameType(game)] || gameType(game)}</dd>
          </dl>
        </section>
      </div>
    </div>
    </>
  );
}

/* One row of the lineup sheet.""")

io.open(p, 'w', encoding='utf-8').write(s)
print('body done')
