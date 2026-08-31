/**
 * Class years for the 2025-26 roster, from the club's own site.
 *
 * REAL DATA. Source: californiaicehockey.com/roster, read at import time.
 * The ACHA publishes stats but not class standing; the club's own roster page
 * does, and it is the more authoritative source for it either way.
 *
 * Only `year` is written. The page also carries heights and hometowns that
 * disagree with the EliteProspects data already on the roster, and jersey
 * numbers that disagree with what players actually wore in ACHA games. Those
 * are reported for a human to settle rather than overwritten here.
 */
window.__addYears2526 = function addYears2526(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2025-26"];
  if (!season) return { site: out, report: { error: "no 2025-26 season" } };

  const CLASS = { Freshman: "Fr", Sophomore: "So", Junior: "Jr", Senior: "Sr", Graduate: "Grad" };

  /* name as the club site spells it, number as it lists it, class */
  const LISTED = [
    ["Dominik Sedlak-Braude", "3", "Freshman"],
    ["Kodai Mizuno", "9", "Sophomore"],
    ["Arya Nahavandi", "10", "Sophomore"],
    ["Brendan Baker", "12", "Senior"],
    ["Ryan Lee", "13", "Junior"],
    ["Mark Rejna", "14", "Junior"],
    ["Bryan Bartolo", "15", "Junior"],
    ["Connor Kanas", "17", "Freshman"],
    ["Tyson Storr", "18", "Senior"],
    ["Kayden Roloff", "19", "Junior"],
    ["Henry Conlin", "20", "Junior"],
    ["Lucas Fung", "23", "Freshman"],
    ["Roy Chebaclo", "25", "Senior"],
    ["Kristian Seppanen", "29", "Senior"],
    ["Liam Collins", "72", "Freshman"],
    ["Patrick Liu", "81", "Senior"],
    ["Colten Fazio", "93", "Freshman"],
    ["Jason Lee", "4", "Senior"],
    ["William Hagan", "6", "Freshman"],
    ["Ellis O'Dowd", "8", "Junior"],
    ["Patrick Nasta", "11", "Graduate"],
    ["John Burbank", "16", "Senior"],
    ["Trent Teruya", "21", "Sophomore"],
    ["Simon Mantoani", "51", "Freshman"],
    ["Sean Dolim", "88", "Senior"],
    ["Enzo Goebel", "95", "Junior"],
    ["Eric Khodorenko", "96", "Senior"],
    ["Yusuf Akbas", "1", "Senior"],
    ["Charles Anaka", "30", "Senior"],
    ["Aidan Comeau", "80", "Sophomore"],
    ["Nikola Tomic", "", "Graduate"],
  ];

  /* The club site and our roster spell three players differently. Matching on
     the surname alone would collide on Lee, so these map the full name. */
  const ALIAS = {
    patrickliu: "tianshuliu",
    charlesanaka: "allananaka",
    johnburbank: "jackburbank",
  };
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  const roster = season.roster || [];
  const byName = new Map(roster.map((p) => [norm(p.name), p]));

  const set = [];
  const missing = [];
  const numberDiffers = [];

  for (const [name, number, cls] of LISTED) {
    const key = norm(name);
    const p = byName.get(ALIAS[key] || key);
    if (!p) { missing.push(name); continue; }
    p.year = CLASS[cls] || "";
    set.push(p.name + " " + p.year);
    /* What they wore in ACHA games is what the box scores say; this only
       notes where the club page disagrees. */
    if (number && String(p.number || "") !== number) {
      numberDiffers.push(`${p.name}: roster #${p.number || "—"}, club site #${number}`);
    }
  }

  const untouched = roster.filter((p) => !p.year).map((p) => p.name);

  return {
    site: out,
    report: {
      set: set.length,
      byClass: ["Fr", "So", "Jr", "Sr", "Grad"].reduce((o, c) => {
        o[c] = roster.filter((p) => p.year === c).length; return o;
      }, {}),
      notOnOurRoster: missing,
      stillWithoutAYear: untouched,
      jerseyNumberDisagrees: numberDiffers,
    },
  };
};
