/**
 * Which opponent marks actually need a dark-background variant, and make one.
 *
 * A "logoDark" is only needed for a mark that disappears on navy - a black
 * or dark-blue wordmark. A mark that is already light reads fine as it is,
 * and flattening it to a white silhouette would throw away colour for
 * nothing. So this measures before it draws: the mean luminance of the
 * opaque pixels, weighted the way an eye weights them.
 *
 * Dark marks get a white silhouette, which is what a school's own style
 * guide reaches for on a dark ground. Everything else is left alone and
 * reported, so the decision is visible rather than assumed.
 *
 * Run: node _darkmarks.mjs [--write]
 */
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const write = process.argv.includes('--write');

const MARKS = [
  'sjsu.webp', 'ucsd.webp', 'washington.webp', 'western-washington.svg',
  'lmu.webp', 'weber-state.webp', 'montana-state.webp', 'metro-state-denver.webp',
  'dakota-college-bottineau.webp', 'northeastern.webp', 'colorado.webp',
  'stanford.webp', 'santa-clara.webp', 'boise-state.webp', 'ucsb.webp',
  'ucla.webp', 'csun.webp', 'asu.webp', 'wyoming.webp', 'new-mexico.webp',
  'santa-rosa.webp', 'byu.webp', 'gonzaga.webp', 'fresno-state.webp',
  'colorado-state.webp',
];

/* Navy is #041E42, luminance about 0.09. A mark has to clear it by a real
   margin to be readable on it; 0.45 is the point where these particular
   marks stop being legible, checked against the ten that already carry a
   white variant. */
const NEEDS_WHITE_BELOW = 0.45;

const results = [];
for (const file of MARKS) {
  const src = path.join(dir, 'logos', file);
  const { data, info } = await sharp(await readFile(src), { density: 400 })
    .resize(256, 256, { fit: 'inside' })
    .ensureAlpha().raw().toBuffer({ resolveWithObject: true });

  let lum = 0, n = 0;
  for (let i = 0; i < data.length; i += info.channels) {
    const a = data[i + 3];
    if (a < 128) continue;               // transparent: not part of the mark
    // Rec. 709 luma, which tracks how bright a colour looks rather than what
    // its channels add up to.
    lum += (0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2]) / 255;
    n++;
  }
  const mean = n ? lum / n : 1;
  const needs = mean < NEEDS_WHITE_BELOW;
  const out = file.replace(/\.(webp|svg|png|jpe?g)$/i, '-white.webp');

  if (needs && write) {
    const w = Buffer.from(data);
    for (let i = 0; i < w.length; i += info.channels) { w[i] = 255; w[i + 1] = 255; w[i + 2] = 255; }
    await sharp(w, { raw: { width: info.width, height: info.height, channels: info.channels } })
      .webp({ quality: 92 }).toFile(path.join(dir, 'logos', out));
  }
  results.push({ file, mean: Number(mean.toFixed(3)), needs, out: needs ? '/logos/' + out : null });
}

results.sort((a, b) => a.mean - b.mean);
for (const r of results) {
  console.log((r.needs ? 'WHITE ' : 'keep  ') + String(r.mean).padEnd(6) + ' ' + r.file);
}
console.log('\n' + results.filter((r) => r.needs).length + ' of ' + results.length + ' need a white variant'
  + (write ? ' (written)' : ' (dry run - pass --write)'));

if (write) {
  await writeFile(path.join(dir, '_darkmarks.json'),
    JSON.stringify(Object.fromEntries(results.filter((r) => r.needs).map((r) => [r.file, r.out])), null, 1));
  console.log('map written to _darkmarks.json');
}
