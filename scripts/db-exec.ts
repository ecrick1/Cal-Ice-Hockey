/**
 * Runs a .sql file against the project database.
 *
 * The Supabase REST API cannot execute DDL, so migrations otherwise have to be
 * pasted into the dashboard SQL editor by hand. This connects directly instead.
 *
 *   pnpm db:exec supabase/migrations/0003_opponents_people_stats.sql
 *   pnpm db:exec --all        # every migration, in filename order
 *
 * Each file runs inside a single transaction: it either lands completely or
 * not at all, matching how the SQL editor behaves.
 *
 * Needs DATABASE_URL in .env.local (Supabase dashboard -> Connect).
 */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });
config({ path: '.env' });

const url = process.env.DATABASE_URL;
if (!url) {
  console.error(
    'Missing DATABASE_URL.\n\n' +
      'Supabase dashboard -> Connect -> Session pooler, copy the URI and put it in\n' +
      '.env.local as DATABASE_URL, replacing [YOUR-PASSWORD] with the database password.',
  );
  process.exit(1);
}

const MIGRATIONS = 'supabase/migrations';

async function targets(): Promise<string[]> {
  const args = process.argv.slice(2).filter((a) => a !== '--all');
  if (process.argv.includes('--all')) {
    const files = await readdir(MIGRATIONS);
    return files
      .filter((f) => f.endsWith('.sql'))
      .sort()
      .map((f) => path.join(MIGRATIONS, f));
  }
  if (args.length === 0) {
    console.error('Usage: pnpm db:exec <file.sql> [more.sql] | --all');
    process.exit(1);
  }
  return args;
}

async function main() {
  const files = await targets();
  const client = new pg.Client({
    connectionString: url,
    // Supabase terminates non-TLS connections; the pooler presents a cert that
    // does not match the hostname, so verification is off but transport is not.
    ssl: { rejectUnauthorized: false },
  });

  await client.connect();
  console.log(`connected -> ${url.replace(/:[^:@]+@/, ':****@')}\n`);

  try {
    for (const file of files) {
      const sql = await readFile(file, 'utf8');
      process.stdout.write(`${path.basename(file)} ... `);
      try {
        await client.query('begin');
        await client.query(sql);
        await client.query('commit');
        console.log('ok');
      } catch (e) {
        await client.query('rollback');
        const err = e as { message?: string; position?: string; hint?: string };
        console.log('FAILED (rolled back)');
        console.error(`  ${err.message}`);
        if (err.hint) console.error(`  hint: ${err.hint}`);
        if (err.position) {
          // Point at the offending statement rather than making the reader count.
          const upto = sql.slice(0, Number(err.position));
          const line = upto.split('\n').length;
          console.error(`  at line ${line}: ${sql.split('\n')[line - 1]?.trim()}`);
        }
        process.exitCode = 1;
        return;
      }
    }
    console.log('\nAll statements applied.');
  } finally {
    await client.end();
  }
}

main().catch((e) => {
  console.error('\n', e instanceof Error ? e.message : e);
  process.exit(1);
});
