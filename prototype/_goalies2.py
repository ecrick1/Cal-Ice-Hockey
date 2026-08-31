# -*- coding: utf-8 -*-
"""What the goaltending list is built from, the split name, and the centred
watch/tickets row."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


D = '"\\u2014"'

sub("""  /* The same two colours the Game stats bars use, so a bar means the same
     thing whichever state of the page it is in. */""",
    """  /* A name reads better broken: the given name light, the surname bold
     under it, the way a team sheet sets one. */
  const splitName = (full) => {
    const parts = String(full || "").trim().split(/\\s+/);
    return parts.length > 1
      ? { first: parts.slice(0, -1).join(" "), last: parts[parts.length - 1] }
      : { first: "", last: full || "" };
  };
  const pct3 = (n, d) => (d ? (n / d).toFixed(3).replace(/^0/, "") : """ + D + """);

  /* Both benches, in the same shape, so one list renders either. A team band
     is the sum of its keepers - which is where a team save percentage comes
     from, since neither source publishes one. */
  const ourKeepers = netminders.map(({ p, k }) => ({
    key: p.id, ...splitName(p.name), number: p.number, photo: p.photo || null,
    onClick: () => onPlayer(p.id),
    saves: k.saves, ga: k.ga, so: k.so,
    stats: [
      [k.gp, "GP"],
      [k.gaa === null ? """ + D + """ : k.gaa.toFixed(2), "GAA"],
      [pctText(k.svpct), "SV%"],
      [k.so, "SO"],
    ],
  }));
  const theirKeepers = (theirStats ? theirStats.goalies.slice(0, 2) : []).map((g, i) => {
    const faced = (g.saves || 0) + (g.ga || 0);
    const gaa = g.gaa != null ? g.gaa : (g.gp ? ((g.ga || 0) / g.gp).toFixed(2) : null);
    const sv = g.svpct != null ? String(g.svpct).replace(/^0/, "") : (faced ? pct3(g.saves, faced) : null);
    const number = g.number || (theirGoalies.find((x) => x.name === g.name) || {}).number;
    return {
      key: g.name || i, ...splitName(g.name), number,
      saves: g.saves, ga: g.ga, so: g.so,
      stats: [
        [g.gp == null ? """ + D + """ : g.gp, "GP"],
        [gaa == null ? """ + D + """ : gaa, "GAA"],
        [sv == null ? """ + D + """ : sv, "SV%"],
        [g.so == null ? """ + D + """ : g.so, "SO"],
      ],
    };
  });
  const bandFor = (keepers, rec, gapg) => {
    const saves = keepers.reduce((n, g) => n + (Number(g.saves) || 0), 0);
    const ga = keepers.reduce((n, g) => n + (Number(g.ga) || 0), 0);
    const so = keepers.reduce((n, g) => n + (Number(g.so) || 0), 0);
    return [
      [rec, "W-L"],
      [gapg == null ? """ + D + """ : gapg, "GA/GP"],
      [saves + ga ? pct3(saves, saves + ga) : """ + D + """, "SV%"],
      [so, "SO"],
    ];
  };
  const GOALIE_BLOCKS = [
    { key: "us", abbr: usAbbr, logo: org.logo, keepers: ourKeepers,
      team: bandFor(ourKeepers, us.w + "-" + us.l + (us.t ? "-" + us.t : ""), team.gapg) },
    { key: "them", abbr: themName, logo: game.opponentLogo, keepers: theirKeepers,
      loading: live.loading,
      team: bandFor(theirKeepers,
        opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : """ + D + """,
        opp.data ? opp.data.gapg : null) },
  ];

  /* The same two colours the Game stats bars use, so a bar means the same
     thing whichever state of the page it is in. */""")

# ------------------------------------------- players to watch name split
sub("""                <span className="h2hnames">
                  <span className="h2hname">{x.p.name}</span>
                  <span className="h2hpos">#{x.p.number || """ + D + """} · {posOf(x.p)}</span>
                </span>""",
    """                <span className="h2hnames">
                  <span className="h2hname">
                    <span className="h2hfirst">{splitName(x.p.name).first}</span>
                    <span className="h2hlast">{splitName(x.p.name).last}</span>
                  </span>
                  <span className="h2hpos">#{x.p.number || """ + D + """} · {posOf(x.p)}</span>
                </span>""")

sub("""                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? "" : " unknown")}>
                    {THEIRS[label] ? THEIRS[label].name : "Not published"}
                  </span>
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? (THEIRS[label].pos || "") + " · " + (THEIRS[label].gp || 0) + " GP"
                      : themName}
                  </span>
                </span>""",
    """                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? "" : " unknown")}>
                    <span className="h2hfirst">{THEIRS[label] ? splitName(THEIRS[label].name).first : ""}</span>
                    <span className="h2hlast">
                      {THEIRS[label] ? splitName(THEIRS[label].name).last : "Not published"}
                    </span>
                  </span>
                  {/* Number and position, the same two facts as ours - their
                      games played is on the roster table, not here. */}
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? [THEIRS[label].number ? "#" + THEIRS[label].number : null, THEIRS[label].pos]
                          .filter(Boolean).join(" · ")
                      : themName}
                  </span>
                </span>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('data + names done')
