# -*- coding: utf-8 -*-
"""Fetch the visiting roster where it is actually needed: at the rink.

The lineup sheet's second step is someone standing at the glass twenty
minutes before a faceoff with the other team's roster on a sheet of paper.
That is the moment to read it from the league, not the evening before on
the Opponents tab.

The button goes into OpponentRoster, which is the same editor in all three
places it appears - the lineup step, the Rosters tab during a game, and the
Opponents tab - so it turns up in all of them from one change.

Two differences from the Cal version. It keeps only number, name and
position, because this is a record of who played us rather than a roster we
maintain for another club. And where an opponent has no league id on file,
it looks one up by name and remembers it, so the next fetch is direct.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------- find a team by name
sub("""/* What the league is allowed to write.""",
    """/* League names carry a division prefix and spell out what our records
   abbreviate: "MD2 University of California-Los Angeles" against "UCLA".
   Stripping both down to letters matches most of them, and the ones it
   cannot are left to be linked by hand rather than guessed at. */
function achaNameKey(x) {
  return String(x || "").toLowerCase()
    .replace(/^m[d]?\\s*[123]\\s+/, "")
    .replace(/\\buniv(ersity)?\\b/g, "")
    .replace(/\\bof\\b/g, "")
    .replace(/[^a-z]/g, "");
}

/* What the league is allowed to write.""")

# ------------------------------------------------------------- the component
sub("""function OpponentRoster({ opponent, setOpp, onClose }) {
  const roster = opponent.roster || [];
  const [paste, setPaste] = useState("");""",
    """function OpponentRoster({ opponent, setOpp, onClose, achaSeasonId }) {
  const ask = useAsk();
  const roster = opponent.roster || [];
  const [paste, setPaste] = useState("");
  const [pulling, setPulling] = useState(false);

  /* Their id if we have it, otherwise found by name and kept, so this is a
     lookup once rather than every time. */
  const pullTheirs = async () => {
    setPulling(true);
    try {
      let teamId = opponent.achaTeamId;
      if (!teamId) {
        const teams = await fetch("/acha?view=teamsForSeason&season_id=" + achaSeasonId)
          .then((r) => r.json());
        const want = [opponent.name, opponent.short].filter(Boolean).map(achaNameKey);
        const hit = (teams.teams || []).find((t) => want.includes(achaNameKey(t.name)));
        if (!hit) {
          setPulling(false);
          await ask({
            title: "Cannot find them in the league",
            message: "No team in this season matches \\u201c" + (opponent.name || "") + "\\u201d.",
            detail: "Set their ACHA team id on the Opponents tab and this will go straight to it.",
            blocked: true,
          });
          return;
        }
        teamId = hit.id;
        setOpp(opponent.id, { achaTeamId: teamId });
      }
      const j = await fetch("/acha?view=roster&season_id=" + achaSeasonId + "&team_id=" + teamId)
        .then((r) => r.json());
      const holder = j.roster && (Array.isArray(j.roster) ? j.roster[0] : j.roster);
      const rows = [];
      for (const sec of (holder && holder.sections) || []) {
        if (/coach/i.test(sec.title || "")) continue;
        const fallback = /goal/i.test(sec.title || "") ? "G"
          : /defen/i.test(sec.title || "") ? "D" : "F";
        for (const d of sec.data || []) {
          const r = d.row || {};
          if (!r.name) continue;
          /* Number, name, position. Nothing else: this is a record of who
             played us, not a roster we keep for another club. */
          rows.push({
            id: uid(),
            number: String(r.tp_jersey_number || "").replace(/\\D/g, ""),
            name: String(r.name).trim(),
            position: /^[FDG]$/.test(r.position || "") ? r.position : fallback,
          });
        }
      }
      setPulling(false);
      if (!rows.length) {
        await ask({
          title: "The league has not posted their roster",
          message: (opponent.name || "This team") + " has no players listed for this season.",
          blocked: true,
        });
        return;
      }
      const key = (n) => String(n || "").toLowerCase().replace(/[^a-z]/g, "");
      const have = new Set(roster.map((x) => key(x.name)));
      const fresh = rows.filter((x) => !have.has(key(x.name)));
      if (!fresh.length) {
        await ask({
          title: "Nothing to add",
          message: "All " + rows.length + " players the league lists are already here.",
          blocked: true,
        });
        return;
      }
      const ok = await ask({
        title: "Add " + fresh.length + " from the league?",
        message: (opponent.name || "They") + " have " + rows.length + " listed"
          + (rows.length === fresh.length ? "." : "; the rest are already here."),
        list: fresh.map((x) => ({ label: (x.number ? "#" + x.number + "  " : "") + x.name, note: x.position })),
        confirmLabel: "Add them",
      });
      if (ok) setOpp(opponent.id, { roster: [...roster, ...fresh] });
    } catch (e) {
      setPulling(false);
      await ask({ title: "Could not read the league", message: String((e && e.message) || e), blocked: true });
    }
  };""")

sub("""        <button className="btn bGhost bSm" style={{ marginLeft: "auto" }} onClick={onClose}>Done</button>""",
    """        <button className="btn bGhost bSm" style={{ marginLeft: "auto" }}
          onClick={pullTheirs} disabled={pulling || !achaSeasonId}
          title={achaSeasonId
            ? "Read their roster from the ACHA"
            : "This season is not linked to an ACHA season"}>
          {pulling ? "Reading the league\\u2026" : "Fetch from ACHA"}
        </button>
        <button className="btn bGhost bSm" onClick={onClose}>Done</button>""")

# ------------------------------------------------------------- the three uses
sub("""            <OpponentRoster opponent={o} setOpp={setOpp} onClose={() => setOpenRoster(null)} />""",
    """            <OpponentRoster opponent={o} setOpp={setOpp}
              achaSeasonId={(site.seasons[site.currentSeason] || {}).achaSeasonId}
              onClose={() => setOpenRoster(null)} />""")

sub("""            <OpponentRoster opponent={opponent} setOpp={setOpp}
              onClose={() => setTheirOpen(false)} />""",
    """            <OpponentRoster opponent={opponent} setOpp={setOpp} achaSeasonId={achaSeasonId}
              onClose={() => setTheirOpen(false)} />""")

sub("""              <OpponentRoster opponent={opponent} setOpp={setOpp}
                onClose={() => setTab("scoring")} />""",
    """              <OpponentRoster opponent={opponent} setOpp={setOpp}
                achaSeasonId={(site.seasons[site.currentSeason] || {}).achaSeasonId}
                onClose={() => setTab("scoring")} />""")

# LiveLineup has to carry the season id through to it.
sub("""function LiveLineup({ game, roster, oppName, previous, opponent, setOpp, setGame, onStart, onWarmup, onCancel }) {""",
    """function LiveLineup({ game, roster, oppName, previous, opponent, setOpp, setGame, onStart, onWarmup, onCancel, achaSeasonId }) {""")

sub("""        setGame={setGame} onStart={() => goLive(setupGame)}
        onWarmup={() => goLive(setupGame, false, true)}
        onCancel={() => setSetupId(null)} />""",
    """        setGame={setGame} onStart={() => goLive(setupGame)}
        onWarmup={() => goLive(setupGame, false, true)}
        achaSeasonId={season.achaSeasonId}
        onCancel={() => setSetupId(null)} />""")

io.open(p, 'w', encoding='utf-8').write(s)
print('opponent fetch added')
