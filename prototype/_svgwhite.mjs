/**
 * Make the white-on-dark version of an SVG mark.
 *
 * Recolouring vector source beats masking a raster: the shape stays crisp at
 * any size, and a two-tone crest flattens to one clean silhouette instead of
 * a mask with soft edges. Every paint that draws something becomes white -
 * `fill="none"` is left alone because it draws nothing, and a path with no
 * fill attribute at all is painted black by SVG's own default, so it needs
 * one added rather than replaced.
 *
 * This is the same transform the admin applies in the browser when an SVG is
 * uploaded, kept here so marks can also be prepared from the command line.
 *
 * Run: node _svgwhite.mjs <in.svg> <out.svg>
 */
import { readFile, writeFile } from 'node:fs/promises';

export function whiteSvg(src) {
  let s = src;

  /* Anything already painted, except an explicit "none". */
  s = s.replace(/(fill|stroke)="(?!none")[^"]*"/g, '$1="#ffffff"');
  s = s.replace(/(fill|stroke):\s*(?!none)[^;"']+/g, '$1:#ffffff');

  /* A shape with no fill attribute is black by default, so say white. */
  s = s.replace(/<(path|polygon|circle|ellipse|rect)\b(?![^>]*\bfill=)([^>]*?)(\/?)>/g,
    '<$1 fill="#ffffff"$2$3>');

  return s;
}

const [, , inFile, outFile] = process.argv;
if (inFile && outFile) {
  await writeFile(outFile, whiteSvg(await readFile(inFile, 'utf8')), 'utf8');
  console.log('wrote ' + outFile);
}
