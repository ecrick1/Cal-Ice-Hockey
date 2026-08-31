# -*- coding: utf-8 -*-
"""Replace lines 7159..7278 - the three wide sections - with the two-column
version. Done by line range because the block mixes real em dashes with
\\uXXXX escapes and matching it as text keeps going wrong.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
lines = io.open(p, encoding='utf-8').read().split('\n')

# 1-indexed 7159 .. 7278 -> slice bounds
START, END = 7158, 7277
head = lines[START]
tail = lines[END - 1]
assert head.strip() == '{!!H2H.length && (', head
assert tail.strip() == '<span className="gcserieslead">{note}</span>', tail

DASH = '"\\u2014"'

NEW = '''    <div className="gcgrid">
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
        <p className="bsm gcnone gpseason">{note}</p>
        {H2H.map(([label, entry, val]) => {
          const x = entry[1];
          const a = val(x.t);
          const them = THEIRS[label] ? theirValue[label](THEIRS[label]) : null;
          const total = a + (them || 0);
          /* Even split when neither has one, so the bar does not read as a
             lopsided result where there is no result. */
          const pa = total ? (a / total) * 100 : 50;
          return (
            <div className="gcbar h2hbar" key={label}>
              <button className="h2hface" onClick={() => onPlayer(x.p.id)}>
                <PlayerAvatar size={38} photo={x.p.photo} />
                <span className="h2hnames">
                  <span className="h2hname">{x.p.name}</span>
                  <span className="h2hpos">#{x.p.number || DASH} · {posOf(x.p)}</span>
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
              <span className="gcbarval right">{them == null ? DASH : them}</span>
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
        <p className="bsm gcnone gpseason">{note}</p>
        <div className="gtgrid">
          <div className="gtside">
            <div className="gtline gtteamline">
              <span><strong>{us.w}-{us.l}{us.t ? "-" + us.t : ""}</strong>W-L{us.t ? "-T" : ""}</span>
              <span><strong>{team.gapg == null ? DASH : team.gapg}</strong>GA/GP</span>
            </div>
            {netminders.map(({ p, k }) => (
              <button className="gtcard" key={p.id} onClick={() => onPlayer(p.id)}>
                <span className="gthead">
                  <PlayerAvatar size={42} photo={p.photo} />
                  <span className="gtnames">
                    <span className="gtname">{p.name}</span>
                    <span className="gtnum">#{p.number || DASH}</span>
                  </span>
                </span>
                <span className="gtline">
                  <span><strong>{k.gp}</strong>GP</span>
                  <span><strong>{k.gaa === null ? DASH : k.gaa.toFixed(2)}</strong>GAA</span>
                  <span><strong>{pctText(k.svpct)}</strong>SV%</span>
                  <span><strong>{k.so}</strong>SO</span>
                </span>
              </button>
            ))}
          </div>
          <div className="gtside">
            <div className="gtline gtteamline">
              <span><strong>{opp.data ? opp.data.w + "-" + opp.data.l + (opp.data.t ? "-" + opp.data.t : "") : DASH}</strong>W-L</span>
              <span><strong>{opp.data ? opp.data.gapg : DASH}</strong>GA/GP</span>
            </div>
            {(theirStats ? theirStats.goalies.slice(0, 2).map((p) => {
              /* A pasted row carries the rates already; one added up from box
                 scores carries saves and goals against, so they come from
                 those. */
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
                    {/* A visiting keeper has no headshot here, so their crest
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
                    <span><strong>{p.gp == null ? DASH : p.gp}</strong>GP</span>
                    <span><strong>{p.gaa == null ? DASH : p.gaa}</strong>GAA</span>
                    <span><strong>{p.svpct == null ? DASH : String(p.svpct).replace(/^0/, "")}</strong>SV%</span>
                    <span><strong>{p.so == null ? DASH : p.so}</strong>SO</span>
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
          <span className="gcserieslead">{note}</span>'''.replace('DASH', DASH)

lines[START:END] = NEW.split('\n')
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('replaced %d lines with %d' % (END - START, len(NEW.split('\n'))))
