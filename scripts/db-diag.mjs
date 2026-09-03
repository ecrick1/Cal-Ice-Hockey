/**
 * What the database is actually doing, when a write starts timing out.
 *
 * Read-only. Sizes, triggers, timeouts - the things that decide whether a
 * four-megabyte update finishes inside the eight seconds PostgREST allows.
 */
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });

const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
await c.connect();

const q = async (label, sql) => {
  const t = Date.now();
  try {
    const r = await c.query(sql);
    console.log('\n— ' + label + '  (' + (Date.now() - t) + 'ms)');
    console.table(r.rows);
  } catch (e) {
    console.log('\n— ' + label + ': ' + e.message);
  }
};

await q('site_state', `
  select key, pg_size_pretty(length(value)::bigint) as value_size, rev, updated_at
  from site_state order by key`);

await q('history', `
  select count(*) as rows,
         pg_size_pretty(coalesce(sum(length(value)),0)::bigint) as raw_text,
         pg_size_pretty(pg_total_relation_size('site_state_history')) as on_disk
  from site_state_history`);

await q('statement timeout per role', `
  select rolname, rolconfig from pg_roles
  where rolname in ('authenticated','anon','authenticator','service_role')`);

await q('triggers on site_state', `
  select tgname from pg_trigger
  where tgrelid='site_state'::regclass and not tgisinternal`);

await c.end();
