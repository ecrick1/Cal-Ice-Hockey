/**
 * Work out which opponent marks are a single colour, and make white versions
 * of them for dark surfaces.
 *
 * The play-by-play rows sit on navy and ask for `logoDark`. Every opponent on
 * file has that slot empty, so oppLogo() falls back to the light mark - and a
 * one-colour navy crest like Washington State's disappears into the row.
 *
 * "One colour" is measured rather than eyeballed: pixels are read at low
 * resolution, the transparent and near-grey ones are dropped, and what is
 * left is bucketed by hue. A mark drawn in one ink lands in one bucket no
 * matter how much anti-aliasing surrounds its edges; a two-tone crest lands
 * in two or more. The report is printed so the call can be checked by eye
 * before anything is written.
 *
 * Run: node _whitemarks.mjs [--write]
 */
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const logos = path.join(dir, 'logos');
const write = process.argv.includes('--write');

const rgbToHsl = (r, g, b) => {
  r /= 255; g /= 255; b /= 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  const l = (mx + mn) / 2;
  if (!d) return [0, 0, l];
  const s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
  let h;
  if (mx === r) h = ((g - b) / d + (g < b ? 6 : 0));
  else if (mx === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  return [h * 60, s, l];
};

async function inks(file) {
  const { data, info } = await sharp(await readFile(file), { density: 200 })
    .resize(96, 96, { fit: 'inside' })
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const buckets = new Map();      // 30-degree hue bucket -> count
  let dark = 0, light = 0, solid = 0;
  for (let i = 0; i < data.length; i += info.channels) {
    const a = data[i + 3];
    if (a < 200) continue;        // edge pixels are a blend, not an ink
    solid++;
    const [h, s, l] = rgbToHsl(data[i], data[i + 1], data[i + 2]);
    if (s < 0.18) { if (l < 0.5) dark++; else light++; continue; }
    const k = Math.floor(h / 30) % 12;
    buckets.set(k, (buckets.get(k) || 0) + 1);
  }

  /* A hue only counts as an ink if it covers a real share of the mark -
     otherwise a hundred stray pixels of JPEG fringe read as a second colour. */
  const real = [...buckets.entries()].filter(([, n]) => n / solid > 0.06);
  if (dark / solid > 0.06) real.push(['dark', dark]);
  if (light / solid > 0.06) real.push(['light', light]);
  return { solid, inks: real.map(([k]) => k), detail: real };
}

const files = (await readdir(logos)).filter((f) => f !== 'cal.svg');
const rows = [];
for (const f of files) {
  const { inks: k, detail } = await inks(path.join(logos, f));
  rows.push({ f, n: k.length, k, detail });
}

rows.sort((a, b) => a.n - b.n || a.f.localeCompare(b.f));
for (const r of rows) {
  console.log(String(r.n).padStart(2) + ' ink  ' + r.f.padEnd(34)
    + r.detail.map(([k, n]) => k + ':' + n).join(' '));
}

/* The rule, stated once: a mark drawn in one ink goes white on navy, and so
   does Eastern Washington's despite being two-tone. UCLA stays as it is. */
const KEEP_AS_IS = new Set(['ucla.webp', 'ucla.svg']);
const ALSO_WHITE = new Set(['eastern-washington.webp']);
const chosen = rows
  .filter((r) => (r.n <= 1 || ALSO_WHITE.has(r.f)) && !KEEP_AS_IS.has(r.f))
  .map((r) => r.f);

console.log('\nwhite version for ' + chosen.length + ':');
console.log('  ' + chosen.join('\n  '));

if (!write) { console.log('\n(dry run - pass --write to generate)'); process.exit(0); }

/* The white mark is the shape of the original: keep the alpha channel, throw
   the colour away. That is exactly right for a one-ink logo and is what
   flattening a two-tone one to a silhouette means. */
for (const f of chosen) {
  const src = path.join(logos, f);
  const base = sharp(await readFile(src), { density: 400 }).resize(256, 256, { fit: 'inside' });
  const { data, info } = await base.ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  for (let i = 0; i < data.length; i += info.channels) {
    data[i] = 255; data[i + 1] = 255; data[i + 2] = 255;
  }
  const outName = f.replace(/\.[^.]+$/, '') + '-white.webp';
  await sharp(data, { raw: { width: info.width, height: info.height, channels: info.channels } })
    .webp({ quality: 92 })
    .toFile(path.join(logos, outName));
  console.log('wrote logos/' + outName);
}
