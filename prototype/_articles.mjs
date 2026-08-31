/**
 * Pull the club's own article archive off californiaicehockey.com.
 *
 * REAL CONTENT, and the club's own - this is the team's writing being carried
 * from the site it is on now to the one being built, not text taken from
 * somewhere else.
 *
 * Every article page is the same shape: a .date, an h2, one p.paragraph that
 * serves as the lede, and then the body. The banner sits on the index page
 * next to the "Read More" link rather than on the article itself, so the two
 * are matched up here by article number.
 *
 * Run: node _articles.mjs   -> _articles.json  +  articles/*.jpg
 */
import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const BASE = 'https://californiaicehockey.com';
const outDir = path.join(dir, 'articles');

const strip = (h) => h
  .replace(/<br\s*\/?>/gi, ' ')
  .replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
  .replace(/&#39;|&rsquo;/g, "\u2019").replace(/&quot;/g, '"')
  .replace(/&mdash;/g, '\u2014').replace(/&ndash;/g, '\u2013')
  .replace(/\s+/g, ' ').trim();

/* ---- the running order and the banners ----
   The index at /articles is client-rendered, so a plain fetch of it returns
   an empty root div. The article pages themselves are static HTML and fetch
   fine; only this pairing had to be read out of the rendered page, so it is
   recorded here rather than re-derived. Order is the club's own, newest
   first. */
const CARDS = [
  ['13', 'article13.png'],
  ['12', 'article12.png'],
  ['11', 'article11img.png'],
  ['10', 'article10img.png'],
  ['8',  'article8.png'],
  ['9',  'Article8Banner.avif'],
  ['1',  'Article1Banner.jpg'],
  ['2',  'MeetTheBearsBanner.jpg'],
  ['3',  'Article3Banner.png'],
  ['4',  'Article4Banner.jpg'],
  ['5',  'Article5Banner.jpeg'],
  ['6',  'Article6Banner.png'],
  ['7',  'Article7Banner.jpg'],
];
const nums = CARDS.map(([n]) => n);
const banners = Object.fromEntries(CARDS.map(([n, f]) => [n, `${BASE}/images/${f}`]));

await mkdir(outDir, { recursive: true });

const out = [];
for (const n of nums) {
  const html = await fetch(`${BASE}/article-pages/article${n}.html`).then((r) => r.text());
  const body = html.split(/<div class="blog"/)[1] || html;

  const date = strip((body.match(/<div class="date">([\s\S]*?)<\/div>/) || [])[1] || '');
  const title = strip((body.match(/<h2[^>]*>([\s\S]*?)<\/h2>/) || [])[1] || '');
  const paras = [...body.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)].map((m) => strip(m[1])).filter(Boolean);
  const video = (body.match(/<iframe[^>]+src="([^"]+)"/) || [])[1] || '';

  /* Some articles carry their own in-body image; prefer the index banner
     because that is the one the club chose as the cover. */
  const inBody = (body.match(/<img[^>]+src="([^"]+)"/) || [])[1];
  const cover = banners[n] || (inBody ? new URL(inBody, `${BASE}/article-pages/`).href : '');

  out.push({ n, date, title, lede: paras[0] || '', body: paras.slice(1), video, cover });
  console.log(`article${n}  ${date}  ${paras.length}p  ${cover ? 'cover' : 'NO COVER'}  ${title.slice(0, 54)}`);
}

/* ---- covers, cropped the way the site crops a story image ---- */
for (const a of out) {
  if (!a.cover) continue;
  const buf = Buffer.from(await fetch(a.cover).then((r) => r.arrayBuffer()));
  const file = `article${a.n}.jpg`;
  await sharp(buf).resize(1600, 900, { fit: 'cover', position: 'attention' })
    .jpeg({ quality: 78 }).toFile(path.join(outDir, file));
  a.image = '/articles/' + file;
}

await writeFile(path.join(dir, '_articles.json'), JSON.stringify(out, null, 1), 'utf8');
console.log(`\n${out.length} articles, ${out.filter((a) => a.image).length} covers -> _articles.json`);
