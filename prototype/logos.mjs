/**
 * Convert the opponent marks in Downloads into the prototype's logo folder.
 *
 * Everything lands as a 256px-wide WebP on transparency, which is what the
 * existing marks are and roughly four times the largest size the site ever
 * draws one (the box-score banner). SVG passes through untouched — it is
 * already resolution-independent and the server serves image/svg+xml.
 *
 * Run: node logos.mjs
 */
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';
import path from 'node:path';
import { readdir, copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
// The team drops opponent marks in Downloads/logos; the Western Washington
// SVG arrived in Downloads itself.
const src = path.join(process.env.USERPROFILE ?? '', 'Downloads', 'logos');
const srcAlt = path.join(process.env.USERPROFILE ?? '', 'Downloads');
const out = path.join(dir, 'logos');

/* Downloaded filename -> the slug the site refers to it by. */
const MAP = {
  'Northeastern.png': 'northeastern',
  'Santa Clara.png': 'santa-clara',
  'University of San Diego.png': 'san-diego',
  'LMU.png': 'lmu',
  'UC Santa Barbara.png': 'ucsb',
  'UC San Diego.png': 'ucsd',
  'Cal State Fullerton.png': 'fullerton',
  'UC Irvine.png': 'uc-irvine',
  'NAU.png': 'nau',
  'Northern Colorado.png': 'northern-colorado',
  'Utah Tech.png': 'utah-tech',
  'Weber State.png': 'weber-state',
  'Montana State.png': 'montana-state',
  'Montana.png': 'montana',
  'Eastern Washington.png': 'eastern-washington',
  'grand canyon.png': 'grand-canyon',
  'Virginia Tech.png': 'virginia-tech',
  'Virginia.png': 'virginia',
  'Vanderbilt.png': 'vanderbilt',
  'Texas A&M.png': 'texas-am',
  'duke.png': 'duke',
  'Texas.png': 'texas',
  'penn state.png': 'penn-state',
  'illinois.png': 'illinois',
  'indiana.png': 'indiana',
  'iowa.png': 'iowa',
  'utah state.png': 'utah-state',
  'fresno state.png': 'fresno-state',
  'colorado state.png': 'colorado-state',
  'boise state.png': 'boise-state',
  'nc state.png': 'nc-state',
  'miami.png': 'miami',
  'louisville.png': 'louisville',
  'georgia tech.png': 'georgia-tech',
  'florida state.png': 'florida-state',
  'Western_Washington_Vikings_logo.svg': 'western-washington',
  // The two 2025-26 opponents the library had no mark for.
  'metro state denver.png': 'metro-state-denver',
  'dakota college bottineau.png': 'dakota-college-bottineau',
  // The last opponent on any schedule that had no mark.
  'csun.png': 'csun',
  // Opponents from the 2012-15 seasons, which nothing before them played.
  'santa rosa.png': 'santa-rosa',
  'byu.png': 'byu',
  'gonzaga.png': 'gonzaga',
  // Already in the library; re-converted so every mark comes from one pipeline.
  'long beach.png': 'long-beach-state',
  'washington state.png': 'washington-state',
  'san diego state.png': 'sdsu',
};

await mkdir(out, { recursive: true });
const have = new Set(await readdir(src));
const haveAlt = new Set(await readdir(srcAlt));
const locate = (f) => (have.has(f) ? path.join(src, f) : haveAlt.has(f) ? path.join(srcAlt, f) : null);
let done = 0;
const missing = [];

for (const [file, slug] of Object.entries(MAP)) {
  const from = locate(file);
  if (!from) { missing.push(file); continue; }
  if (file.toLowerCase().endsWith('.svg')) {
    await copyFile(from, path.join(out, slug + '.svg'));
    console.log(slug.padEnd(20), 'svg (copied)');
  } else {
    const info = await sharp(from)
      .resize(256, 256, { fit: 'inside', withoutEnlargement: true })
      .webp({ quality: 90, alphaQuality: 100 })
      .toFile(path.join(out, slug + '.webp'));
    console.log(slug.padEnd(20), info.width + 'x' + info.height, Math.round(info.size / 1024) + 'KB');
  }
  done++;
}

console.log('\n' + done + ' converted');
if (missing.length) console.log('NOT FOUND: ' + missing.join(', '));
