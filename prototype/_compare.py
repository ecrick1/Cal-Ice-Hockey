"""Pull the opponent's season from the ACHA feed and set it beside ours."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


sub("""/** The season a preview should describe: this one once it has games, else the last one that did. */""",
    """/**
 * The opponent's season, live from the ACHA.
 *
 * Their feed sends no CORS headers, so this goes through the site's own
 * origin - /acha here, a route handler in the real app - which is also where
 * the answer gets cached. One request gives their whole schedule, which is
 * enough for a record and goals per game. Power play and penalty kill would
 * need a summary per game, which is not something to do on a page load.
 *
 * Nothing is shown unless it loads. A comparison with half the numbers
 * missing is worse than no comparison.
 */
function useOpponentSeason(opponent, achaSeasonId) {
  const [state, setState] = useState({ loading: false, data: null });
  const teamId = opponent && opponent.achaTeamId;

  useEffect(() => {
    if (!teamId || !achaSeasonId) { setState({ loading: false, data: null }); return; }
    let alive = true;
    setState({ loading: true, data: null });
    fetch("/acha?view=schedule&season_id=" + achaSeasonId + "&team=" + teamId)
      .then((r) => r.json())
      .then((j) => {
        const holder = Array.isArray(j) ? j[0] : j;
        const rows = ((holder && holder.sections) || []).flatMap((sec) => (sec.data || []).map((d) => d.row));
        let w = 0, l = 0, t = 0, gf = 0, ga = 0;
        for (const g of rows) {
          if (!/final/i.test(g.game_status || "")) continue;
          const home = String(g.home_team_city || "");
          const us = /Berkeley/i.test(home) ? null : null;
          /* Which side they were on, by team id rather than by name. */
          const theirs = String(g.home_team_id) === String(teamId);
          const ours = theirs ? Number(g.home_goal_count) : Number(g.visiting_goal_count);
          const other = theirs ? Number(g.visiting_goal_count) : Number(g.home_goal_count);
          if (!Number.isFinite(ours) || !Number.isFinite(other)) continue;
          gf += ours; ga += other;
          if (ours > other) w++; else if (ours < other) l++; else t++;
        }
        const gp = w + l + t;
        if (!alive) return;
        setState({ loading: false, data: gp ? {
          gp, w, l, t, gf, ga,
          gfpg: (gf / gp).toFixed(2), gapg: (ga / gp).toFixed(2),
        } : null });
      })
      .catch(() => { if (alive) setState({ loading: false, data: null }); });
    return () => { alive = false; };
  }, [teamId, achaSeasonId]);

  return state;
}

/** The season a preview should describe: this one once it has games, else the last one that did. */""")

# ---------------------------------------------------------- the card
sub("""      <div className="gccol">
        <section className="statcard gcpad">
          <h2 className="statsec">
            Team stats
            <span className="gcserieslead">{note}{team.gp ? " \\u00b7 " + team.gp + " GP" : ""}</span>
          </h2>
          <dl className="gcinfo">
            {TEAM_ROWS.flatMap(([k, v]) => [<dt key={k + "d"}>{k}</dt>, <dd key={k + "v"}>{v}</dd>])}
          </dl>
        </section>""",
    """      <div className="gccol">
        <section className="statcard gcpad">
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
        )}""")

# Where the rows come from, and the season to ask the feed about.
sub("""  const isHome = game.homeAway === "H";""",
    """  /* The feed's own id for the season the form comes from. Held on the season
     so nothing has to guess a mapping between our labels and theirs. */
  const opponentRec = (site.opponents || []).find((o) => o.id === game.opponentId);
  const opp = useOpponentSeason(opponentRec, form.season.achaSeasonId);
  const num = (v) => (v == null ? null : Number(v));
  const bigger = (a, b) => { const x = num(a), y = num(b); return x === y ? "" : x > y ? "us" : "them"; };
  const smaller = (a, b) => { const x = num(a), y = num(b); return x === y ? "" : x < y ? "us" : "them"; };
  const us = seasonRecord(form.season);
  const COMPARE_ROWS = opp.data ? [
    ["Record", us.w + "-" + us.l + (us.t ? "-" + us.t : ""),
      opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : ""), null],
    ["Games played", us.gp, opp.data.gp, null],
    ["Goals for", us.gf, opp.data.gf, bigger],
    ["Goals against", us.ga, opp.data.ga, smaller],
    ["GF / GP", team.gfpg == null ? "\\u2014" : team.gfpg, opp.data.gfpg, bigger],
    ["GA / GP", team.gapg == null ? "\\u2014" : team.gapg, opp.data.gapg, smaller],
  ] : [];

  const isHome = game.homeAway === "H";""")

# A record straight off a season's own game log.
sub("""function seasonTeamStats(site, season) {""",
    """/** W-L-T and goals for a season, from its own finished games. */
function seasonRecord(season) {
  let w = 0, l = 0, t = 0, gf = 0, ga = 0;
  for (const g of season.schedule || []) {
    if (!g.result || !countsToward(g)) continue;
    gf += Number(g.result.us) || 0;
    ga += Number(g.result.them) || 0;
    if (g.result.us > g.result.them) w++; else if (g.result.us < g.result.them) l++; else t++;
  }
  return { w, l, t, gf, ga, gp: w + l + t };
}

function seasonTeamStats(site, season) {""")

# --------------------------------------------------------------- styling
sub("""/* The row between the banner and the preview: the two things somebody""",
    """/* Two columns of numbers with the label between them, so the eye compares
   across rather than reading two lists. */
.cmprow { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
  gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--border); }
.cmprow:last-of-type { border-bottom: 0; }
.cmphead { font-weight: 800; font-size: 13px; color: var(--ink); padding-top: 0; }
.cmphead span:first-child { text-align: left; }
.cmphead span:last-child { text-align: right; }
.cmplab { font-size: 11.5px; font-weight: 700; color: var(--muted); text-align: center;
  white-space: nowrap; }
.cmpval { font-family: var(--disp); font-weight: 700; font-size: 20px; color: var(--muted);
  font-variant-numeric: tabular-nums; }
.cmprow .cmpval:first-child { text-align: left; }
.cmprow .cmpval:last-child { text-align: right; }
/* The better of the two carries the ink; the other recedes. */
.cmpval.on { color: var(--ink); }

/* The row between the banner and the preview: the two things somebody""")

io.open(p, 'w', encoding='utf-8').write(s)
print('compare done')
