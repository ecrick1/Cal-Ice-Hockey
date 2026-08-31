# -*- coding: utf-8 -*-
"""One keeper a side means the team band was that keeper.

The band carried W-L, GA/GP, SV% and SO summed across the goaltenders. With
two of them that was a real total; with one it is the same save percentage
and the same shutouts printed twice, a row apart. So the band keeps only what
belongs to the team - the crest and the record - and the rates live on the
one row that owns them.

The graduated-players note goes too.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# The band becomes a heading: crest and team, nothing the row repeats.
sub("""            <div className="gtband">
              <span className="gtbandmark">
                {side.logo
                  ? <img src={side.logo} alt="" />
                  : <OppBadge name={side.abbr} size={30} />}
              </span>
              {side.team.map(([v, k]) => (
                <span className="gtstat" key={k}>
                  <strong>{v}</strong><span className="gtstatlab">{k}</span>
                </span>
              ))}
            </div>""",
    """            <div className="gtband">
              <span className="gtbandmark">
                {side.logo
                  ? <img src={side.logo} alt="" />
                  : <OppBadge name={side.abbr} size={30} />}
                <span className="gtbandname">{side.abbr}</span>
              </span>
            </div>""")

# The team line it was built from is no longer read.
i = s.index("  const bandFor = (keepers, rec, gapg) => {")
j = s.index("  const GOALIE_BLOCKS = [")
s = s[:i] + s[j:]

sub("""    { key: "us", abbr: usAbbr, logo: org.logo, keepers: ourKeepers,
      team: bandFor(ourKeepers, us.w + "-" + us.l + (us.t ? "-" + us.t : ""), team.gapg) },
    { key: "them", abbr: themName, logo: game.opponentLogo, keepers: theirKeepers,
      loading: live.loading,
      team: bandFor(theirKeepers,
        opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : "\\u2014",
        opp.data ? opp.data.gapg : null) },""",
    """    { key: "us", abbr: usAbbr, logo: org.logo, keepers: ourKeepers },
    { key: "them", abbr: themName, logo: game.opponentLogo, keepers: theirKeepers,
      loading: live.loading },""")

# The note about who graduated.
sub("""        {form.prior && rows.length !== available.length && (
          <p className="bsm gcnone gpnote">
            Last season's numbers, less the {rows.length - available.length} who
            graduated.
          </p>
        )}
""", "")

# Styling: the band is a label now, not a row of figures.
sub(""".gtband, .gtrow { display: grid; grid-template-columns: minmax(0, 1fr) repeat(4, minmax(52px, 74px));
  align-items: center; gap: 10px; }
.gtband { background: var(--ice); border-radius: 10px; padding: 12px 16px; }
.gtbandmark { display: flex; align-items: center; }
.gtbandmark img { height: 30px; width: auto; max-width: 46px; object-fit: contain; display: block; }""",
    """.gtrow { display: grid; grid-template-columns: minmax(0, 1fr) repeat(4, minmax(52px, 74px));
  align-items: center; gap: 10px; }
.gtband { padding: 4px 2px 8px; }
.gtbandmark { display: flex; align-items: center; gap: 10px; }
.gtbandmark img { height: 26px; width: auto; max-width: 42px; object-fit: contain; display: block; }
.gtbandname { font-weight: 800; font-size: 13px; color: var(--muted); }""")

sub(""".gtband .gtstat strong { font-size: 19px; }
""", "")

sub("""  .gtband, .gtrow { grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .gtwho, .gtbandmark { grid-column: 1 / -1; }
  .gtrow { padding: 12px 4px; }
  .gtband { padding: 12px; }""",
    """  .gtrow { grid-template-columns: repeat(4, 1fr); gap: 8px; padding: 12px 4px; }
  .gtwho { grid-column: 1 / -1; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('band trimmed, note removed')
