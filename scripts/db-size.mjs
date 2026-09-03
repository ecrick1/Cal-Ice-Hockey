/**
 * How much of the database is used, and by what.
 *
 * Deliberately cheap: relation sizes come from the catalogue, not from
 * reading the rows. The earlier version of this summed length(value) across
 * the history table, which reads thirty-odd megabytes of TOAST and takes half
 * a minute - long enough, on a small instance, to make the site itself slow
 * while it runs.
 */
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });

const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
await c.connect();

const { rows: [db] } = await c.query(
  `select pg_size_pretty(pg_database_size(current_database())) as total,
          pg_database_size(current_database()) as bytes`);

const { rows: tables } = await c.query(`
  select relname as table,
         pg_size_pretty(pg_total_relation_size(relid)) as size,
         pg_total_relation_size(relid) as bytes,
         n_live_tup as rows
  from pg_stat_user_tables
  order by pg_total_relation_size(relid) desc
  limit 8`);

const FREE = 500 * 1024 * 1024;
console.log('database total: %s  (%s%% of a 500 MB free tier)',
  db.total, ((db.bytes / FREE) * 100).toFixed(1));
console.table(tables.map(({ table, size, rows }) => ({ table, size, rows })));
await c.end();
