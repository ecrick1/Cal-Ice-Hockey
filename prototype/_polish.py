# -*- coding: utf-8 -*-
"""Preview polish: bars on head to head, Team stats gone, goaltending stacked
full width with a team band over each pair, centred CTA row, and names set
first-light-over-last-bold."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


D = '"\\u2014"'

# ---------------------------------------------------- head-to-head rows
sub("""  const COMPARE_ROWS = opp.data ? [
    ["Record", us.w + "-" + us.l + (us.t ? "-" + us.t : ""),
      opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : ""), null],
    ["Games played", us.gp, opp.data.gp, null],
    ["Goals for", us.gf, opp.data.gf, bigger],
    ["Goals against", us.ga, opp.data.ga, smaller],
    ["GF / GP", team.gfpg == null ? "\\u2014" : team.gfpg, opp.data.gfpg, bigger],
    ["GA / GP", team.gapg == null ? "\\u2014" : team.gapg, opp.data.gapg, smaller],
  ] : [];""",
    """  /* A record is two numbers in a hyphen, not one quantity, so it gets no
     bar - there is nothing to divide. Everything under it is a single
     figure a side and compares properly. */
  const COMPARE_ROWS = opp.data ? [
    ["Record", us.w + "-" + us.l + (us.t ? "-" + us.t : ""),
      opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : ""), false],
    ["Games played", us.gp, opp.data.gp, true],
    ["Goals for", us.gf, opp.data.gf, true],
    ["Goals against", us.ga, opp.data.ga, true],
    ["GF / GP", team.gfpg == null ? """ + D + """ : team.gfpg, opp.data.gfpg, true],
    ["GA / GP", team.gapg == null ? """ + D + """ : team.gapg, opp.data.gapg, true],
  ] : [];""")

# --------------------------------- team stats out, head to head redrawn
sub("""        <section className="statcard gcpad">
          <h2 className="statsec">
            Team stats
            <span className="gcserieslead">{note}{team.gp ? " \\u00b7 " + team.gp + " GP" : ""}</span>
          </h2>
          <dl className="gcinfo">
            {TEAM_ROWS.flatMap(([k, v]) => [<dt key={k + "d"}>{k}</dt>, <dd key={k + "v"}>{v}</dd>])}
          </dl>
        </section>

        {opp.data && (
          <section className="statcard gcpad">
            <h2 className="statsec">
              Head to head
              <span className="gcserieslead">{form.name}</span>
            </h2>
            <div className="cmprow cmphead">
              <span>{gameName(site)}</span><span className="cmplab" /><span>{game.opponent}</span>
            </div>
            {COMPARE_ROWS.map(([label, a, b, better]) => {
              const lead = better === null ? "" : better(a, b);
              return (
                <div className="cmprow" key={label}>
                  <span className={"cmpval " + (lead === "us" ? "on" : "")}>{a}</span>
                  <span className="cmplab">{label}</span>
                  <span className={"cmpval " + (lead === "them" ? "on" : "")}>{b}</span>
                </div>
              );
            })}
            <p className="bsm gcnone" style={{ marginTop: 12 }}>
              Their side is read live from the ACHA. Power play and penalty kill are not
              in that feed's schedule, so they are ours only.
            </p>
          </section>
        )}""",
    """        {opp.data && (
          <section className="statcard gcpad">
            <div className="gcstatshead">
              {org.logo
                ? <img className="gcstatslogo" src={org.logo} alt="" />
                : <OppBadge name={usAbbr} size={30} />}
              <h2 className="statsec" style={{ margin: 0 }}>Head to head</h2>
              {game.opponentLogo
                ? <img className="gcstatslogo" src={game.opponentLogo} alt="" />
                : <OppBadge name={themName} size={30} />}
            </div>
            <p className="bsm gcnone gpseason">{form.name}</p>
            {COMPARE_ROWS.map(([label, a, b, bar]) => {
              const x = Number(a), y = Number(b);
              const t = (x || 0) + (y || 0);
              const pa = t ? (x / t) * 100 : 50;
              return (
                <div className="gcbar" key={label}>
                  <span className="gcbarval">{a}</span>
                  <span className="gcbarlab">{label}</span>
                  <span className="gcbarval right">{b}</span>
                  <span className="gcbartrack">
                    {bar && Number.isFinite(x) && Number.isFinite(y) ? (
                      <>
                        <span className="gcbarfill left" style={{ width: pa + "%", background: usColor }} />
                        <span className="gcbarfill right" style={{ width: (100 - pa) + "%", background: themColor }} />
                      </>
                    ) : <span className="gcbarnone" />}
                  </span>
                </div>
              );
            })}
          </section>
        )}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('head to head done')
