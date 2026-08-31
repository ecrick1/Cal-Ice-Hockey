/**
 * A cover image for every game recap.
 *
 * Six of the thirty games are against USC and Washington, and the team's photo
 * library has action shots of both - those recaps get a real photograph of the
 * two sides that actually played. For the other eleven opponents there is no
 * photograph, and putting an unrelated action shot on the card would tell the
 * reader they are looking at a game they are not. So those get a matchup card
 * built from the two crests: it carries no claim beyond who played, which is
 * the one thing it can honestly say.
 *
 * Light background on purpose. The Cal script is navy (#041e42) and every
 * opponent mark on file is a `logoLight` drawn for a pale surface, so a navy
 * card would swallow half of them.
 *
 * Run: node _covers.mjs   -> covers/*.jpg
 */
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, 'covers');
await mkdir(out, { recursive: true });

const W = 1600, H = 900;
const NAVY = '#041E42', GOLD = '#FFC72C';

/* The card itself: a pale field, a hairline between the two crests, and the
   navy-over-gold footer the rest of the site ends every page with. */
const plate = Buffer.from(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
     <defs>
       <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
         <stop offset="0" stop-color="#FFFFFF"/>
         <stop offset="1" stop-color="#E7EDF3"/>
       </linearGradient>
     </defs>
     <rect width="${W}" height="${H}" fill="url(#g)"/>
     <rect x="${W / 2 - 1.5}" y="230" width="3" height="380" fill="#CFD8E1"/>
     <rect x="0" y="762" width="${W}" height="8" fill="${GOLD}"/>
     <rect x="0" y="770" width="${W}" height="130" fill="${NAVY}"/>
   </svg>`
);

/* Fit inside a box without distorting, then place it centred on a point. */
async function mark(file, boxW, boxH, cx, cy) {
  const buf = await sharp(await readFile(file), { density: 400 })
    .resize(boxW, boxH, { fit: 'inside', withoutEnlargement: false })
    .png()
    .toBuffer();
  const { width, height } = await sharp(buf).metadata();
  return { input: buf, left: Math.round(cx - width / 2), top: Math.round(cy - height / 2) };
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

/* Every opponent mark the prototype has, keyed the way the site stores it. */
const logoDir = path.join(dir, 'logos');
const have = new Set(await readdir(logoDir));

const opponents = JSON.parse(await readFile(path.join(dir, '_opponents.json'), 'utf8'));

let made = 0;
const missing = [];
for (const o of opponents) {
  const file = (o.logoLight || '').replace(/^\/logos\//, '');
  if (!file || !have.has(file)) { missing.push(o.name); continue; }

  const cal = await mark(path.join(logoDir, 'cal.svg'), 460, 300, W * 0.29, 415);
  const them = await mark(path.join(logoDir, file), 430, 320, W * 0.71, 415);

  await sharp(plate)
    .composite([cal, them])
    .jpeg({ quality: 82 })
    .toFile(path.join(out, slug(o.name) + '.jpg'));
  made++;
}

console.log(`${made} matchup covers -> covers/`);
if (missing.length) console.log('no mark on file for:', missing.join(', '));
