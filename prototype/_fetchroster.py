# -*- coding: utf-8 -*-
"""Pull the roster from the league instead of typing it in.

Why the ACHA and not EliteProspects: EliteProspects answers a browser and
refuses a server, 403 to every request whether it announces itself or not.
The ACHA's own feed answers anything, and it is where the numbers on this
site already come from - so it is the one source that can be read on demand
without pretending to be someone else.

Which year it pulls is not asked. The season being edited carries the
league's own id for that season, and Cal's team id is looked up inside it
rather than assumed, because the league renumbers teams between years.

What it will and will not overwrite is the important part. The league knows
a jersey number, a position, a height, a weight, a shooting hand and a
hometown. It does not know a class year, a bio, a headshot or a stat line,
and those are typed here. So a fetch fills blanks and adds people; it never
writes over something already entered. What it would change is listed
before anything is written, and nothing is written until that list is
accepted.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the fetch
sub("""function RosterEditor({ site, updateSeason: updateSeasonProp }) {""",
    """/**
 * Cal's roster for one season, straight from the league.
 *
 * Returns { rows, teamName } or throws with something a person can act on.
 * The team is found by name inside the season rather than by a remembered
 * id, because the league renumbers teams from year to year.
 */
async function fetchAchaRoster(seasonId, match) {
  const teams = await fetch("/acha?view=teamsForSeason&season_id=" + seasonId)
    .then((r) => r.json());
  const team = (teams.teams || []).find((t) => match.test(t.name || ""));
  if (!team) throw new Error("The league has no team matching that name in this season.");
  const j = await fetch("/acha?view=roster&season_id=" + seasonId + "&team_id=" + team.id)
    .then((r) => r.json());
  const holder = j.roster && (Array.isArray(j.roster) ? j.roster[0] : j.roster);
  const rows = [];
  for (const sec of (holder && holder.sections) || []) {
    if (/coach/i.test(sec.title || "")) continue;
    const position = /goal/i.test(sec.title || "") ? "G"
      : /defen/i.test(sec.title || "") ? "D" : "F";
    for (const d of sec.data || []) {
      const r = d.row || {};
      if (!r.name) continue;
      rows.push({
        name: String(r.name).trim(),
        number: String(r.tp_jersey_number || "").replace(/\\D/g, ""),
        position: /^[FDG]$/.test(r.position || "") ? r.position : position,
        height: r.height_hyphenated
          ? String(r.height_hyphenated).replace("-", "\\u2032") + "\\u2033" : "",
        weight: r.w ? r.w + " lbs" : "",
        shoots: r.shoots || r.catches || "",
        hometown: String(r.hometown || "").replace(/,\\s*United States$/, ""),
      });
    }
  }
  return { rows, teamName: team.name };
}

/* What the league is allowed to write. Everything else on a player - class
   year, bio, headshot, stat line - is typed in this console and is not the
   league's to know, let alone to replace. */
const ACHA_FIELDS = ["number", "position", "height", "weight", "shoots", "hometown"];

function RosterEditor({ site, updateSeason: updateSeasonProp }) {""")

# -------------------------------------------------------------- the action
sub("""  const cols = "44px 1.55fr 52px 56px 58px 62px 50px 96px 92px 1.2fr 1.3fr 50px 28px";""",
    """  const cols = "44px 1.55fr 52px 56px 58px 62px 50px 96px 92px 1.2fr 1.3fr 50px 28px";

  const [pulling, setPulling] = useState(false);
  const achaSeasonId = season.achaSeasonId;

  /* Names are matched loosely: the two sources disagree about punctuation and
     about which of a first name someone goes by, and a roster is small enough
     that surname plus first initial is unambiguous within it. */
  const nameKey = (n) => {
    const parts = String(n || "").toLowerCase().replace(/[^a-z ]/g, "").trim().split(/\\s+/);
    return parts.length > 1 ? parts[parts.length - 1] + "|" + parts[0][0] : parts.join("");
  };

  const pullRoster = async () => {
    if (!achaSeasonId) {
      await ask({
        title: "No league season linked",
        message: sel + " has no ACHA season id on it, so there is nothing to fetch from.",
        detail: "Seasons imported from the league carry one. This season was entered by hand or came from elsewhere.",
        blocked: true,
      });
      return;
    }
    setPulling(true);
    let data;
    try {
      const org = (site.settings || {}).org || {};
      const match = org.achaTeamMatch
        ? new RegExp(org.achaTeamMatch, "i")
        : /california-berkeley/i;
      data = await fetchAchaRoster(achaSeasonId, match);
    } catch (e) {
      setPulling(false);
      await ask({
        title: "Could not read the league's roster",
        message: String((e && e.message) || e),
        blocked: true,
      });
      return;
    }
    setPulling(false);

    if (!data.rows.length) {
      await ask({
        title: "The league has not posted this roster yet",
        message: data.teamName + " has no players listed for " + sel + ".",
        detail: "Rosters usually appear once the season is under way. Nothing has been changed.",
        blocked: true,
      });
      return;
    }

    /* Work out what would change before changing any of it. */
    const byKey = new Map(roster.map((p) => [nameKey(p.name), p]));
    const added = [];
    const filled = [];
    const differs = [];
    for (const r of data.rows) {
      const cur = byKey.get(nameKey(r.name));
      if (!cur) { added.push(r); continue; }
      const blanks = ACHA_FIELDS.filter((f) => !String(cur[f] || "").trim() && String(r[f] || "").trim());
      const clashes = ACHA_FIELDS.filter((f) => String(cur[f] || "").trim()
        && String(r[f] || "").trim() && String(cur[f]).trim() !== String(r[f]).trim());
      if (blanks.length) filled.push({ name: cur.name, fields: blanks });
      if (clashes.length) differs.push({ name: cur.name, fields: clashes });
    }
    const missing = roster.filter((p) => !data.rows.some((r) => nameKey(r.name) === nameKey(p.name)));

    if (!added.length && !filled.length) {
      await ask({
        title: "Nothing to add",
        message: "All " + data.rows.length + " players the league lists are already here, with those fields filled in.",
        detail: differs.length
          ? differs.length + " differ from what the league has, and are left as typed."
          : undefined,
        blocked: true,
      });
      return;
    }

    const list = [
      ...added.map((r) => ({ label: r.name, note: "new" })),
      ...filled.map((f) => ({ label: f.name, note: f.fields.join(", ") })),
    ];
    const ok = await ask({
      title: "Add from the league?",
      message: added.length + " to add, " + filled.length + " with blanks to fill, from "
        + data.rows.length + " listed.",
      detail: [
        differs.length ? differs.length + " already differ from the league and are left as typed." : "",
        missing.length ? missing.length + " here are not on the league's list and are left alone." : "",
      ].filter(Boolean).join(" "),
      list,
      confirmLabel: "Add them",
    });
    if (!ok) return;

    const next = roster.map((p) => {
      const r = data.rows.find((x) => nameKey(x.name) === nameKey(p.name));
      if (!r) return p;
      const patch = {};
      for (const f of ACHA_FIELDS) {
        if (!String(p[f] || "").trim() && String(r[f] || "").trim()) patch[f] = r[f];
      }
      return Object.keys(patch).length ? { ...p, ...patch } : p;
    });
    for (const r of added) {
      next.push({
        id: uid(), name: r.name, number: r.number, position: r.position,
        spot: "", shoots: r.shoots, year: "", captain: "",
        height: r.height, weight: r.weight, hometown: r.hometown,
        highSchool: "", priorTeam: "", bio: "", photo: null, stats: {},
      });
    }
    updateSeason(sel, { roster: next });
  };""")

# -------------------------------------------------------------- the button
sub("""        {prevSeasons.length > 0 && (
          <select style={{ marginLeft: "auto", padding: "7px 9px", fontSize: 13.5 }}
            value="" onChange={(e) => e.target.value && copyFrom(e.target.value)}>
            <option value="">Copy roster from…</option>
            {prevSeasons.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        )}""",
    """        <button className="btn bGhost bSm" style={{ marginLeft: "auto" }}
          onClick={pullRoster} disabled={pulling || !achaSeasonId}
          title={achaSeasonId
            ? "Read " + sel + " from the ACHA and add anyone missing"
            : sel + " is not linked to an ACHA season"}>
          {pulling ? "Reading the league…" : "Fetch from ACHA"}
        </button>
        {prevSeasons.length > 0 && (
          <select style={{ padding: "7px 9px", fontSize: 13.5 }}
            value="" onChange={(e) => e.target.value && copyFrom(e.target.value)}>
            <option value="">Copy roster from…</option>
            {prevSeasons.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        )}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('fetch button added')
