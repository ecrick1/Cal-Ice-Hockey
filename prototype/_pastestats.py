# -*- coding: utf-8 -*-
"""A paste box for an opponent's season totals.

EliteProspects publishes what the league's feed does not - an opponent's
skater and goaltender totals - and returns 403 to anything that is not a
browser, so the site cannot fetch it. Somebody with the page open can copy
the table, and that is what this takes: the two tables pasted as they come
off the page, parsed into the shape the game preview reads.

It hangs off the roster expander that is already there, so the opponents grid
does not gain another column.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# ------------------------------------------------------------ the parser
sub("""/** Their roster, live from the league. Names, numbers and positions - no stats. */""",
    """/**
 * An opponent's season, parsed from a pasted stats table.
 *
 * Written against what EliteProspects puts on the clipboard: a rank, then the
 * name carrying its position in brackets, then the numbers. Skaters and
 * goaltenders are told apart by the bracketed position, so both tables can go
 * into the same box in either order.
 */
function parseOpponentStats(text) {
  const skaters = [];
  const goalies = [];
  for (const raw of String(text || "").split(/\\r?\\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const cells = line.split(/\\t+| {2,}/).map((c) => c.trim()).filter((c) => c !== "");
    if (cells.length < 4) continue;
    /* Skip the header row and the league band that sits between the two. */
    if (/^(#|rank)$/i.test(cells[0])) continue;
    if (/^(skater|goalie|player)$/i.test(cells[1] || "")) continue;

    const start = /^\\d+\\.?$/.test(cells[0]) ? 1 : 0;
    let name = cells[start];
    if (!name || !/[A-Za-z]/.test(name)) continue;
    let pos = "";
    const m = name.match(/^(.*?)\\s*\\(([^)]+)\\)\\s*$/);
    if (m) { name = m[1].trim(); pos = m[2].trim(); }
    if (!pos) continue;

    const nums = cells.slice(start + 1).map((c) => (c === "-" ? "" : c));
    const n = (i) => { const v = Number(nums[i]); return nums[i] !== "" && Number.isFinite(v) ? v : null; };

    if (/^G$/i.test(pos)) {
      /* GP, GAA, SV%, W, L, T, SO, TOI, SVS */
      goalies.push({ name, pos, gp: n(0), gaa: nums[1] || null, svpct: nums[2] || null,
        w: n(3), l: n(4), t: n(5), so: n(6) });
    } else {
      /* GP, G, A, TP, PIM */
      skaters.push({ name, pos, gp: n(0), g: n(1), a: n(2), pim: n(4) });
    }
  }
  return { skaters, goalies };
}

/** Their roster, live from the league. Names, numbers and positions - no stats. */""")

# ---------------------------------------------------------- the component
sub("""/* ---------------- Schedule editor ---------------- */""",
    """/**
 * Paste an opponent's season in, per season. Nothing is fetched here - see
 * parseOpponentStats for why - so what lands is exactly what was copied.
 */
function OpponentSeasonStats({ opponent, seasons, setOpp }) {
  const stored = opponent.seasonStats || {};
  const names = Object.keys(seasons).sort().reverse();
  const [season, setSeason] = useState(names[0] || "");
  const [text, setText] = useState("");
  const [msg, setMsg] = useState("");

  const save = () => {
    const parsed = parseOpponentStats(text);
    if (!parsed.skaters.length && !parsed.goalies.length) {
      setMsg("Nothing recognised — paste the table including the position in brackets.");
      return;
    }
    setOpp(opponent.id, {
      seasonStats: { ...stored, [season]: { ...parsed, source: "EliteProspects" } },
    });
    setText("");
    setMsg(parsed.skaters.length + " skaters and " + parsed.goalies.length + " goaltenders saved for " + season + ".");
  };

  const drop = (key) => {
    const next = { ...stored };
    delete next[key];
    setOpp(opponent.id, { seasonStats: next });
  };

  return (
    <div className="auopprosterwrap">
      <p className="h6" style={{ marginBottom: 4 }}>Season totals</p>
      <p className="bsm" style={{ marginBottom: 12 }}>
        The league's feed carries their schedule and roster but not their players' totals.
        Paste the skater and goaltender tables from their EliteProspects season page —
        both can go in together — and the game preview will show their leaders.
      </p>

      {!!Object.keys(stored).length && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
          {Object.entries(stored).map(([k, v]) => (
            <span className="pill pNext" key={k} style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
              {k} · {(v.skaters || []).length}S {(v.goalies || []).length}G
              <button className="btn bGhost bSm" style={{ padding: "0 6px" }} onClick={() => drop(k)}>✕</button>
            </span>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, alignItems: "flex-end", flexWrap: "wrap", marginBottom: 10 }}>
        <div className="field" style={{ maxWidth: 140 }}>
          <label className="h6">Season</label>
          <select value={season} onChange={(e) => setSeason(e.target.value)}>
            {names.map((n) => <option key={n}>{n}</option>)}
          </select>
        </div>
        <button className="btn bNavy bSm" onClick={save} disabled={!text.trim()}>Save season</button>
      </div>
      <textarea rows={6} value={text} placeholder={"1.\\tCharlie Drage (F)\\t20\\t17\\t19\\t36\\t20"}
        onChange={(e) => { setText(e.target.value); setMsg(""); }} />
      {msg && <p className="bsm" style={{ marginTop: 8, color: "var(--au-dim)" }}>{msg}</p>}
    </div>
  );
}

/* ---------------- Schedule editor ---------------- */""")

# ---------------------------------------------------- hang it off the row
sub("""        {openRoster === o.id && (
          <OpponentRoster opponent={o} setOpp={setOpp} onClose={() => setOpenRoster(null)} />
        )}""",
    """        {openRoster === o.id && (
          <>
            <OpponentRoster opponent={o} setOpp={setOpp} onClose={() => setOpenRoster(null)} />
            <OpponentSeasonStats opponent={o} seasons={site.seasons} setOpp={setOpp} />
          </>
        )}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('paste box added')
