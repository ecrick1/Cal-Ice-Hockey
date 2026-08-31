# -*- coding: utf-8 -*-
"""Goaltending as one stacked list: a team band, then that team's two keepers,
then the same again for the visitors. Replaces lines 7230..7308 by range,
because the block mixes real dashes with escapes.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
lines = io.open(p, encoding='utf-8').read().split('\n')

START, END = 7229, 7308  # 1-indexed 7230 .. 7308
assert lines[START].strip() == '<section className="statcard gcpad">', lines[START]
assert lines[END - 1].strip() == '</section>', lines[END - 1]

D = '"\\u2014"'

NEW = '''      <section className="statcard gcpad">
        <h2 className="statsec">
          Goaltending
          <span className="gcserieslead">{note}</span>
        </h2>
        {GOALIE_BLOCKS.map((side) => (
          <div className="gtblock" key={side.key}>
            <div className="gtband">
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
            </div>
            {side.keepers.map((g, i) => {
              const Row = g.onClick ? "button" : "div";
              return (
                <Row className="gtrow" key={g.key || i}
                  onClick={g.onClick ? () => g.onClick() : undefined}>
                  <span className="gtwho">
                    {g.photo !== undefined && g.photo !== null
                      ? <PlayerAvatar size={44} photo={g.photo} />
                      : (side.logo
                        ? <img className="gtmark" src={side.logo} alt="" />
                        : <OppBadge name={side.abbr} size={44} />)}
                    <span className="gtnames">
                      <span className="gtfirst">{g.first}</span>
                      <span className="gtlast">{g.last}</span>
                      <span className="gtnum">{g.number ? "#" + g.number : ""}</span>
                    </span>
                  </span>
                  {g.stats.map(([v, k]) => (
                    <span className="gtstat" key={k}>
                      <strong>{v}</strong><span className="gtstatlab">{k}</span>
                    </span>
                  ))}
                </Row>
              );
            })}
            {!side.keepers.length && (
              <p className="bsm gcnone" style={{ padding: "10px 2px" }}>
                {side.loading ? "Loading\\u2026" : "No goaltending on file."}
              </p>
            )}
          </div>
        ))}
      </section>'''

lines[START:END] = NEW.split('\n')
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('goaltending markup replaced')
