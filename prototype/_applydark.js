/**
 * Fill in the dark-surface slot on the opponent library.
 *
 * The play-by-play draws a goal block in the scoring team's colour and asks
 * oppLogo() for the dark mark. Every opponent had that slot empty, so it fell
 * back to the light one - and a crest drawn in a single ink disappears into a
 * band of its own colour. Washington State's is the clearest case.
 *
 * Two kinds of entry here:
 *
 *   Eastern Washington arrived as SVG, so its white version is the same
 *   drawing with every paint turned white - crisp at any size, and the
 *   two-tone eagle flattens to one clean silhouette. Its light mark is
 *   upgraded to the SVG at the same time, unchanged in colour.
 *
 *   The rest are one-ink rasters, measured rather than eyeballed by
 *   _whitemarks.mjs: pixels bucketed by hue, with the transparent and
 *   near-grey ones dropped. UCLA is one ink too and is deliberately left
 *   alone.
 *
 * Anything uploaded through the admin overwrites these - a mark chosen on
 * purpose outranks one derived here.
 */
window.__applyDark = function applyDark(site) {
  const out = JSON.parse(JSON.stringify(site));

  /* opponent name -> [light, dark]; null means leave that slot as it is. */
  const MARKS = {
    "Eastern Washington": ["/logos/eastern-washington.svg", "/logos/eastern-washington-white.svg"],
    /* Both arrived as SVG, so the white is derived from the drawing rather
       than masked out of a raster - and the light mark is upgraded to vector
       at the same time, unchanged in colour. */
    "Washington State": ["/logos/washington-state.svg", "/logos/washington-state-white.svg"],
    Utah: ["/logos/utah.svg", "/logos/utah-white.svg"],
    /* USC supplied a mark already drawn for dark grounds - gold on nothing.
       It is used exactly as given: deriving a white version of it would
       throw away the colour the mark is meant to be. */
    USC: [null, "/logos/usc-dark.webp"],
    /* UCLA in gold rather than white: it is their own second colour and
       reads better than a white script would on UCLA blue. Nothing in the
       code knows that - it is simply the file chosen for their dark slot. */
    UCLA: [null, "/logos/ucla-gold.webp"],
    "Utah State": [null, "/logos/utah-state-white.webp"],
    "Grand Canyon": [null, "/logos/grand-canyon-white.webp"],
    "UC Davis": [null, "/logos/davis-white.webp"],
    Davis: [null, "/logos/davis-white.webp"],
    Duke: [null, "/logos/duke-white.webp"],
    Indiana: [null, "/logos/indiana-white.webp"],
    Iowa: [null, "/logos/iowa-white.webp"],
    "Long Beach State": [null, "/logos/long-beach-state-white.webp"],
    Montana: [null, "/logos/montana-white.webp"],
    Oregon: [null, "/logos/oregon-white.webp"],
    "Penn State": [null, "/logos/penn-state-white.webp"],
    SMU: [null, "/logos/smu-white.webp"],
    "Texas A&M": [null, "/logos/texas-am-white.webp"],
    Texas: [null, "/logos/texas-white.webp"],
  };

  const set = [];
  const notInLibrary = [];
  const seen = new Set();

  for (const o of out.opponents || []) {
    const m = MARKS[o.name];
    if (!m) continue;
    seen.add(o.name);
    const [light, dark] = m;
    if (light) o.logoLight = light;
    o.logoDark = dark;
    set.push(o.name + "  dark=" + dark + (light ? "  light=" + light : ""));
  }
  for (const name of Object.keys(MARKS)) if (!seen.has(name)) notInLibrary.push(name);

  return {
    site: out,
    report: {
      set: set.length,
      list: set,
      notInLibrary,
      stillNoDark: (out.opponents || []).filter((o) => !o.logoDark).map((o) => o.name),
    },
  };
};
