import * as esbuild from 'esbuild';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const watch = process.argv.includes('--watch');

/** The prototype injects its own <style> block, so no CSS entry is needed. */
const options = {
  entryPoints: ['entry.jsx'],
  bundle: true,
  format: 'iife',
  jsx: 'automatic',
  outfile: 'app.js',
  logLevel: 'info',
  define: { 'process.env.NODE_ENV': '"development"' },
  // The reference file lives outside this package, so esbuild would try to
  // resolve `react` next to reference/ and fail. Point it at our own deps.
  nodePaths: [path.join(dir, 'node_modules')],
};

if (watch) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
  console.log('watching reference/cal-ice-hockey-app.jsx for changes...');
} else {
  await esbuild.build(options);
}
