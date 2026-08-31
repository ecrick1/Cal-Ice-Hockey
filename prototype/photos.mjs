/**
 * Prepare the team photos for the prototype.
 *
 * The originals are 1.7–8.4MB PNGs at mixed aspect ratios. The site crops every
 * story image to 16:9, so the crop happens here once rather than in the browser
 * on every load, and the result is re-encoded as JPEG — the same thing the
 * console's `cover` preset (1600×900, q0.78) does to an upload.
 *
 * Run: node photos.mjs
 */
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';
import path from 'node:path';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(process.env.USERPROFILE ?? '', 'Downloads');
const out = path.join(dir, 'photos');

const FILES = [
  ['0ceffad3-3269-4bfc-8be7-88e5e1bff012.png', 'cal-stanford.jpg'],
  ['hf_20260828_215038_38780edb-5d5c-43a6-8eac-c01db7f51b32.png', 'cal-washington.jpg'],
  ['hf_20260828_214859_2f50e872-3ea8-48f9-9e54-250f3d30405b.png', 'cal-asu.jpg'],
  ['hf_20260828_214825_ea24ce41-34ef-43f3-be1b-df9a6d587547.png', 'cal-ucla.jpg'],
];

await mkdir(out, { recursive: true });

for (const [from, to] of FILES) {
  const info = await sharp(path.join(src, from))
    // `cover` crops rather than letterboxes, and `attention` keeps the crop on
    // the busiest part of the frame — the players, not the empty ice.
    .resize(1600, 900, { fit: 'cover', position: sharp.strategy.attention })
    .jpeg({ quality: 78, mozjpeg: true })
    .toFile(path.join(out, to));
  console.log(to.padEnd(20), info.width + 'x' + info.height,
    Math.round(info.size / 1024) + 'KB');
}
