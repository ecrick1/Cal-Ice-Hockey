# -*- coding: utf-8 -*-
"""Their sheet becomes ours: scratches, dressing, and five positions.

Three changes to the Rosters tab.

The club roster came off it. It is a general list kept between games, and it
was sitting under the sheet for tonight looking like a second answer to the
same question. It is still on the Opponents tab, and this tab's Copy button
still reads from it.

Their sheet gains what ours has: a Scratched section, and a Scratch, Dress
and In net button in the last column - so a player who does not come out for
the third can be taken off the pickers mid-game, on their bench as well as
ours. The cross that removed a row is gone, because ours has no cross and
the two are meant to be one thing; a row typed wrong is corrected in place
or scratched.

And a position is one of five. F, D and G was what the league's feed gives,
so it was what the picker offered; a scoresheet says LW, C or RW and so does
ours, and the two sheets disagreeing about how many positions exist is the
kind of difference that survives every attempt to make them match.
Everything that reads a position already folds a wing back to F.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------- a wing is still a forward
sub("""const oppRowPos = (row) => {
  const p = String((row && (row.position || row.pos)) || "").toUpperCase();
  if (p === "D") return "D";
  if (p === "G") return "G";
  return p ? "F" : null;
};""",
    """const oppRowPos = (row) => {
  const p = String((row && (row.position || row.pos)) || "").toUpperCase();
  if (p === "D") return "D";
  if (p === "G") return "G";
  /* LW, C and RW are all forwards to everything that reads this. The sheet
     keeps the wing; the model only ever asks which of the three it is. */
  return p ? "F" : null;
};

/* What a scoresheet writes in the position column. */
const SHEET_POSITIONS = ["LW", "C", "RW", "D", "G"];

/* Absent means dressed: every sheet written before scratches existed. */
const oppDressed = (row) => (row && row.dressed) !== false;""")

# ------------------------------------- scratched rows leave the pickers
sub("""  const theirSheet = ((site.opponentStats || {})[game.id] || [])
    .filter((r) => String(r.name || "").trim())""",
    """  const theirSheet = ((site.opponentStats || {})[game.id] || [])
    .filter((r) => String(r.name || "").trim() && oppDressed(r))""")

# ------------------------------------------------------- the sheet itself
sub("""  const skaters = rows.filter((r) => !isOppGoalie(r));
  const keepers = rows.filter(isOppGoalie);

  const line = (r) => (
    <div className="opprow oppsheetrow" key={r.id}>
      <input value={r.number || ""} placeholder="—"
        onChange={(e) => setRow(r.id, { number: e.target.value })} />
      <input value={r.name || ""} placeholder="Player name"
        onChange={(e) => setRow(r.id, { name: e.target.value })} />
      <select value={isOppGoalie(r) ? "G" : (r.position || "F")}
        onChange={(e) => setRow(r.id, {
          position: e.target.value, isGoalie: e.target.value === "G",
          ...(e.target.value === "G" && r.saves === undefined ? { saves: 0, ga: 0 } : {}),
        })}>
        <option value="F">F</option><option value="D">D</option><option value="G">G</option>
      </select>
      <button className="btn bDanger" aria-label="Remove player"
        onClick={() => setRows(rows.filter((x) => x.id !== r.id))}>✕</button>
    </div>
  );""",
    """  const dressed = rows.filter(oppDressed);
  const skaters = dressed.filter((r) => !isOppGoalie(r));
  const keepers = dressed.filter(isOppGoalie);
  const scratched = rows.filter((r) => !oppDressed(r));

  /* The same row as ours, and the same last column: who is on the bench
     tonight, and which of them is in net. */
  const line = (r) => {
    const out = !oppDressed(r);
    const keeper = isOppGoalie(r);
    return (
      <div className={"opprow oppsheetrow" + (out ? " ausheetout" : "")} key={r.id}>
        <input value={r.number || ""} placeholder="—"
          onChange={(e) => setRow(r.id, { number: e.target.value })} />
        <input value={r.name || ""} placeholder="Player name"
          onChange={(e) => setRow(r.id, { name: e.target.value })} />
        <select value={keeper ? "G" : (r.position || "LW")}
          onChange={(e) => setRow(r.id, {
            position: e.target.value, isGoalie: e.target.value === "G",
            ...(e.target.value === "G" && r.saves === undefined ? { saves: 0, ga: 0 } : {}),
          })}>
          {SHEET_POSITIONS.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
        {keeper && !out ? (
          <button className={"btn bSm " + (live && live.goalieThem === r.name ? "bLive" : "bGhost")}
            title={live && live.goalieThem === r.name ? "In net" : "Put them in net"}
            onClick={() => setLive && setLive({ goalieThem: r.name })}>
            In net
          </button>
        ) : (
          <button className="btn bGhost bSm"
            title={out ? "Dress them" : "Take them out of the lineup"}
            onClick={() => setRow(r.id, { dressed: out })}>
            {out ? "Dress" : "Scratch"}
          </button>
        )}
      </div>
    );
  };""")

sub("""function GameSheet({ game, oppName, site, setDraft, library }) {""",
    """function GameSheet({ game, oppName, site, setDraft, library, live, setLive }) {""")

sub("""        <span className="bsm" style={{ color: "var(--au-faint)", marginLeft: "auto" }}>
          {rows.length ? rows.length + " dressed" : "nobody yet"}
        </span>""",
    """        <span className="bsm" style={{ color: "var(--au-faint)", marginLeft: "auto" }}>
          {dressed.length ? dressed.length + " dressed" : "nobody yet"}
        </span>""")

sub("""      {keepers.length > 0 && (
        <>
          <div className="opprow oppsheetrow head" style={{ marginTop: 10 }}>
            <span>#</span><span>Goaltenders</span><span>Pos</span><span />
          </div>
          {keepers.map(line)}
        </>
      )}""",
    """      {keepers.length > 0 && (
        <>
          <div className="opprow oppsheetrow head" style={{ marginTop: 10 }}>
            <span>#</span><span>Goaltenders</span><span>Pos</span><span />
          </div>
          {keepers.map(line)}
        </>
      )}

      {scratched.length > 0 && (
        <>
          <div className="opprow oppsheetrow head" style={{ marginTop: 10 }}>
            <span>#</span><span>Scratched</span><span>Pos</span><span />
          </div>
          {scratched.map(line)}
        </>
      )}""")

sub("""  const add = (goalie) => setRows([...rows, {
    id: uid(), name: "", number: "", isGoalie: goalie, position: goalie ? "G" : "F",""",
    """  const add = (goalie) => setRows([...rows, {
    id: uid(), name: "", number: "", isGoalie: goalie, position: goalie ? "G" : "LW",""")

sub("""  const copyFromLibrary = () => setRows((library || []).map((p) => ({
    id: uid(), name: p.name, number: p.number,
    isGoalie: p.position === "G", position: p.position || "F",""",
    """  const copyFromLibrary = () => setRows((library || []).map((p) => ({
    id: uid(), name: p.name, number: p.number,
    isGoalie: p.position === "G", position: p.position || "LW",""")

# --------------------------------------------- the club roster comes off
sub("""          {opponent && opponent.id
          ? <>
              {/* This game's sheet first, because it is the list every picker
                  in the console is actually offering. The club roster below
                  is the fallback for games that have none. */}
              <GameSheet game={game} oppName={oppName} site={site} setDraft={setDraft}
                library={(opponent || {}).roster || []} />
              <p className="auhint" style={{ margin: "18px 0 8px", maxWidth: 680 }}>
                Below is {oppName || "their"} club roster — a general list kept between
                games. It is what a game with no sheet of its own falls back to; editing it
                does not change this game.
              </p>
              <OpponentRoster opponent={opponent} setOpp={setOpp}
                achaSeasonId={(site.seasons[site.currentSeason] || {}).achaSeasonId}
                onClose={() => setTab("scoring")} />
            </>""",
    """          {opponent && opponent.id
          ? <GameSheet game={game} oppName={oppName} site={site} setDraft={setDraft}
              library={(opponent || {}).roster || []} live={live} setLive={setLive} />""")

io.open(p, 'w', encoding='utf-8').write(s)
print('their sheet matches ours')
