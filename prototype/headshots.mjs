/**
 * Prepare the placeholder headshots for the prototype's demo data.
 *
 * Square at 640px, matching the console's `headshot` upload preset, and JPEG
 * rather than ~1.5MB PNG. The roster and staff pages render these as circles
 * and as short landscape wells, so the crop is pulled in to head-and-shoulders
 * first: the sources are already square, meaning a plain resize crops nothing
 * and leaves the face small inside a lot of dead headroom.
 *
 * Run: node headshots.mjs
 */
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';
import path from 'node:path';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(process.env.USERPROFILE ?? '', 'Downloads');
const out = path.join(dir, 'photos');

const PLAYERS = [
  'hf_20260828_220146_e7db14ca-5790-4fd2-a0d8-e6450b1cffb7.png',
  'hf_20260828_220235_79e5abf0-3bdc-4846-b609-fc44770d61bb.png',
  'hf_20260828_220235_139e2865-f202-492c-944e-af25eadb0245.png',
  'hf_20260828_220235_d2ae1bec-99a7-47d4-8653-94cd4c2230c6.png',
  'hf_20260828_220316_c3d7f23b-a3c1-4dc4-b27f-265654506cce.png',
  'hf_20260828_220439_8cf16dfb-b7e3-46b2-bed1-812bafa3cfbb.png',
  'hf_20260828_220439_3bea3815-a0f7-44ef-a1e1-8f44ebb7549e.png',
  'hf_20260828_220439_63127aff-00a0-4b7c-a77b-2a59e2d520d7.png',
  'hf_20260828_220439_558b206e-3912-4ed8-8282-a7dfabb9bea3.png',
];

const COACHES = [
  'hf_20260828_220804_f06c59af-7659-48de-9d77-90f2e88e8bd7.png',
  'hf_20260828_220917_923b2cdc-a4a9-4a95-8019-0a3582695d38.png',
  'hf_20260828_221246_fd10fdf8-c6f1-4831-bda6-fd51bf15423f.png',
];

await mkdir(out, { recursive: true });

// The suit portraits are framed a little wider than the jersey ones, so they
// get a slightly looser crop — same treatment, different starting frame.
const CROPS = {
  player: { left: 190, top: 30, width: 644, height: 644 },
  coach: { left: 165, top: 45, width: 694, height: 694 },
};

const jobs = [
  ...PLAYERS.map((f, i) => [f, `head-${i + 1}.jpg`, 'player']),
  ...COACHES.map((f, i) => [f, `coach-${i + 1}.jpg`, 'coach']),
];

for (const [from, to, kind] of jobs) {
  const info = await sharp(path.join(src, from))
    .extract(CROPS[kind])
    .resize(640, 640)
    .jpeg({ quality: 82, mozjpeg: true })
    .toFile(path.join(out, to));
  console.log(to.padEnd(13), info.width + 'x' + info.height,
    Math.round(info.size / 1024) + 'KB');
}
