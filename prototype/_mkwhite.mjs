/* One-off: white silhouette of a raster mark, for a team with no SVG and no
   dark file of their own. Same transform the batch script uses - keep the
   alpha channel, throw the colour away. */
import sharp from '../node_modules/.pnpm/sharp@0.35.4_@types+node@22.20.1/node_modules/sharp/dist/index.mjs';
import { readFile } from 'node:fs/promises';
const [, , src, out] = process.argv;
const { data, info } = await sharp(await readFile(src), { density: 400 })
  .resize(256, 256, { fit: 'inside' }).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
for (let i = 0; i < data.length; i += info.channels) { data[i] = 255; data[i+1] = 255; data[i+2] = 255; }
await sharp(data, { raw: { width: info.width, height: info.height, channels: info.channels } })
  .webp({ quality: 92 }).toFile(out);
console.log('wrote ' + out);
