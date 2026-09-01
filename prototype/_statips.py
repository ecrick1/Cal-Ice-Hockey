# -*- coding: utf-8 -*-
"""Every abbreviation explains itself where it stands, and the glossary goes.

A glossary at the foot of the stats page asks the reader to leave the number
they did not understand, scroll to the bottom, find the letters in a list,
and carry the meaning back up to the row they were on. It also only existed
on that one page: the box score, the game-by-game table and a player's own
page used the same abbreviations and offered nothing at all.

So the meanings live on the headings instead, one list of them, read by
every table that has a column to label. Hovering a heading says what it
means, and the heading carries a dotted underline so there is something to
say it can be hovered.

The list is the glossary's, moved out to where more than one page can see
it, and the goaltending columns that did not exist when it was written are
in it now.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================ one list, where all can read it
sub("""function playElapsed(x) {""",
    """/* What every abbreviation on the site means.
 *
 * Held out here rather than on the stats page because the box score, the
 * game log and a player's own page use the same letters and had no way to
 * explain them - a glossary at the foot of one page cannot label a column on
 * another. Keyed by exactly the text the heading shows. */
const STAT_MEANING = {
  GP: "Games played",
  G: "Goals",
  A: "Assists",
  P: "Points (goals + assists)",
  PTS: "Points (goals + assists)",
  S: "Shots on goal",
  SH: "Shots on goal",
  FO: "Face-offs won and lost",
  "FO%": "Face-off win percentage",
  PIM: "Penalty minutes",
  PPG: "Power-play goals",
  SHG: "Short-handed goals",
  SOG: "Shootout goals",
  GWG: "Game-winning goals",
  TG: "Tying goals",
  Pos: "Position",
  "#": "Jersey number",
  /* Goaltenders */
  "W-L-T": "Wins, losses, ties",
  SA: "Shots against",
  SV: "Saves",
  "SV%": "Save percentage",
  GA: "Goals against",
  "EV GA": "Goals against at even strength",
  "PP GA": "Goals against on the power play",
  "SH GA": "Goals against while short-handed",
  GAA: "Goals against average",
  SO: "Shutouts",
  TOI: "Time on ice",
  /* Team, game by game */
  GF: "Goals for",
  SHA: "Shots against",
};

const statMeaning = (label) => STAT_MEANING[String(label || "").trim()] || null;

/* A column heading that says what it means when you hover it, and looks like
   it will. Falls back to a plain heading for anything not in the list, rather
   than promising an explanation it does not have. */
function StatTh({ label, title, ...rest }) {
  const meaning = title || statMeaning(label);
  return (
    <th {...rest} title={meaning || undefined}
      className={meaning ? "statabbr" : undefined}>
      {label}
    </th>
  );
}

function playElapsed(x) {""")

# ================================================= the skater table headings
sub("""              <th>#</th><th>Player</th>
              {showSpot && <th>Pos</th>}
              <th>G</th><th>A</th><th>P</th>
              <th title="Shots on goal">S</th>
              <th title="Face-offs won and lost">FO</th>
              <th title="Face-off win percentage">FO%</th>
              <th>PIM</th><th>PPG</th><th>SHG</th>""",
    """              <StatTh label="#" /><th>Player</th>
              {showSpot && <StatTh label="Pos" />}
              <StatTh label="G" /><StatTh label="A" /><StatTh label="P" />
              <StatTh label="S" /><StatTh label="FO" /><StatTh label="FO%" />
              <StatTh label="PIM" /><StatTh label="PPG" /><StatTh label="SHG" />""")

sub("""            <tr><th>#</th><th>Goaltender</th>
              <th title="Shots against">SA</th>
              <th title="Saves">SV</th>
              <th title="Goals against">GA</th>
              <th title="Goals against at even strength">EV GA</th>
              <th title="Goals against on the power play">PP GA</th>
              <th title="Goals against while short-handed">SH GA</th>
              <th title="Save percentage">SV%</th>
              <th title="Time on ice">TOI</th></tr>""",
    """            <tr><StatTh label="#" /><th>Goaltender</th>
              <StatTh label="SA" /><StatTh label="SV" /><StatTh label="GA" />
              <StatTh label="EV GA" /><StatTh label="PP GA" /><StatTh label="SH GA" />
              <StatTh label="SV%" /><StatTh label="TOI" /></tr>""")

# ====================================================== the glossary goes
sub("""  const [glossary, setGlossary] = useState(false);
""", "")

sub("""          {/* Glossary lives at the foot of the page — reference material, not a
              control, so it should not sit between the filter and the numbers. */}
          <div className="glosswrap">
            <button className="glossbar" aria-expanded={glossary} onClick={() => setGlossary((v) => !v)}>
              {glossary ? <IcMinusC size={17} /> : <IcPlusC size={17} />} Glossary of abbreviations
            </button>
            {glossary && (
              <div className="glossgrid">
                {GLOSSARY.map(([k, v]) => (
                  <p className="glossitem" key={k}><strong>{k}</strong> — {v}</p>
                ))}
              </div>
            )}
          </div>
""", "")

io.open(p, 'w', encoding='utf-8').write(s)
print('the headings explain themselves')
