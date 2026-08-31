/**
 * Tidy the opponents the ACHA import created.
 *
 * The feed names teams the way the league files them - "MD2 University of
 * California-Santa Barbara" - and my importer stripped that down to
 * "California-Santa Barbara", which is nobody's name for them. It also failed
 * to spot that two of them were teams the library already had under their
 * common names, so it made duplicates.
 *
 * Three things happen here:
 *   1. Duplicates are merged into the entry that was already there, with
 *      every game reassigned before the spare is removed.
 *   2. The rest are renamed to what people call them, with an abbreviation
 *      and the team's colour.
 *   3. A logo is attached wherever one is already on file.
 */
window.__fixOpponents = function fixOpponents(site) {
  const out = JSON.parse(JSON.stringify(site));
  const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  /* Imported name -> the entry it is really the same team as. */
  const MERGE = {
    "California-San Diego": "UC San Diego",
    "Southern California": "USC",
  };

  /* Imported name -> [proper name, short, colour, logo file or null]. */
  const FIX = {
    "California-Santa Barbara": ["UCSB", "UCSB", "#003660", "ucsb.webp"],
    "California-Los Angeles": ["UCLA", "UCLA", "#2D68C4", "ucla.webp"],
    "California-Davis": ["UC Davis", "UCD", "#002855", "davis.webp"],
    "California State University-Northridge": ["Cal State Northridge", "CSUN", "#CE1141", null],
    Stanford: ["Stanford", "STAN", "#8C1515", "stanford.webp"],
    Oregon: ["Oregon", "ORE", "#154733", "oregon.webp"],
    "Santa Clara": ["Santa Clara", "SCU", "#862633", "santa-clara.webp"],
    "Boise State": ["Boise State", "BSU", "#0033A0", "boise-state.webp"],
    Texas: ["Texas", "TEX", "#BF5700", "texas.webp"],
    "Arizona State": ["Arizona State", "ASU", "#8C1D40", "asu.webp"],
    Wyoming: ["Wyoming", "WYO", "#492F24", null],
    "New Mexico": ["New Mexico", "UNM", "#BA0C2F", null],
  };

  const byName = new Map((out.opponents || []).map((o) => [norm(o.name), o]));
  const report = { merged: [], renamed: [], logos: [], stillNoLogo: [], gamesMoved: 0 };

  /* ---- 1. merge duplicates ---- */
  const drop = new Set();
  for (const [dupeName, keepName] of Object.entries(MERGE)) {
    const dupe = byName.get(norm(dupeName));
    const keep = byName.get(norm(keepName));
    if (!dupe || !keep || dupe.id === keep.id) continue;
    let moved = 0;
    for (const season of Object.values(out.seasons || {})) {
      for (const g of season.schedule || []) {
        if (g.opponentId === dupe.id) { g.opponentId = keep.id; moved++; }
      }
    }
    drop.add(dupe.id);
    report.merged.push(dupeName + " -> " + keepName + " (" + moved + " games)");
    report.gamesMoved += moved;
  }
  out.opponents = (out.opponents || []).filter((o) => !drop.has(o.id));

  /* ---- 2 and 3. rename, colour, logo ---- */
  for (const o of out.opponents) {
    const fix = FIX[o.name];
    if (!fix) continue;
    const [name, short, color, logo] = fix;
    if (o.name !== name) report.renamed.push(o.name + " -> " + name);
    o.name = name;
    o.short = short;
    o.color = color;
    if (logo && !o.logoLight) {
      o.logoLight = "/logos/" + logo;
      report.logos.push(name + " -> " + logo);
    }
  }

  const used = new Set();
  for (const season of Object.values(out.seasons || {})) {
    for (const g of season.schedule || []) if (g.opponentId) used.add(g.opponentId);
  }
  report.stillNoLogo = out.opponents.filter((o) => used.has(o.id) && !o.logoLight).map((o) => o.name);
  report.total = out.opponents.length;
  return { site: out, report };
};
