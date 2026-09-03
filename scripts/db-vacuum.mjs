/**
 * Reclaim the space the pruned versions left behind.
 *
 * VACUUM FULL rewrites the table, which returns the disk rather than merely
 * marking it reusable - the point here, since the whole problem was a table
 * growing past what the database can spare. It takes an exclusive lock, so it
 * is run deliberately from here rather than left to autovacuum, and it is over
 * in seconds on a table of this size.
 */
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });

const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
await c.connect();

const size = async () => {
  const { rows: [r] } = await c.query(`
    select (select count(*) from site_state_history) as rows,
           pg_size_pretty(pg_total_relation_size('site_state_history')) as history,
           pg_size_pretty(pg_total_relation_size('site_state')) as state`);
  return r;
};

console.log('before:', await size());
for (const t of ['site_state_history', 'site_state']) {
  const at = Date.now();
  await c.query('vacuum (full, analyze) ' + t);
  console.log('  vacuumed %s in %sms', t, Date.now() - at);
}
console.log('after: ', await size());
await c.end();
