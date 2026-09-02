import * as esbuild from 'esbuild';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const watch = process.argv.includes('--watch');

/**
 * The two public Supabase values, baked into the bundle.
 *
 * Both are meant to be readable by anyone holding the page - the publishable
 * key identifies the project, and what it may do is decided by row-level
 * security rather than by keeping it secret. The secret key is a different
 * value entirely and is never read here.
 *
 * Read from .env.local rather than written down, so there is one copy. A
 * build without them still works: entry.jsx falls back to localStorage, which
 * is what a machine with no database should do.
 */
const env = (() => {
  const out = {};
  for (const f of ['.env.local', '.env']) {
    let text;
    try { text = readFileSync(path.join(dir, '..', f), 'utf8'); } catch { continue; }
    for (const line of text.split(/\r?\n/)) {
      const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*)$/.exec(line);
      if (m && !(m[1] in out)) out[m[1]] = m[2].trim().replace(/^["']|["']$/g, '');
    }
  }
  return out;
})();
const SUPABASE_URL = env.NEXT_PUBLIC_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.warn('no Supabase settings found — building a localStorage-only copy');
}

/** The prototype injects its own <style> block, so no CSS entry is needed. */
/* Anchored to this file rather than to the working directory, so `node
   prototype/build.mjs` works from the repo root the same as from in here -
   which is how it gets typed when somebody is packaging a release. */
const options = {
  entryPoints: [path.join(dir, 'entry.jsx')],
  bundle: true,
  format: 'iife',
  jsx: 'automatic',
  outfile: path.join(dir, 'app.js'),
  logLevel: 'info',
  define: {
    'process.env.NODE_ENV': '"development"',
    'process.env.SUPABASE_URL': JSON.stringify(SUPABASE_URL),
    'process.env.SUPABASE_ANON_KEY': JSON.stringify(SUPABASE_ANON_KEY),
  },
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
