/**
 * How long a save takes by the path the app uses, with the history trigger
 * firing. Inside a transaction that is rolled back, so nothing changes.
 */
import { config } from 'dotenv';
import pg from 'pg';

config({ path: '.env.local' });

const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
await c.connect();
await c.query('begin');
try {
  const { rows: [cur] } = await c.query(
    `select value, rev from site_state where key='cal-hockey-site'`);
  // a real edit: the document with its rev bumped, as the console would send
  const doc = JSON.parse(cur.value);
  doc.rev = Number(cur.rev) + 1;
  const payload = JSON.stringify(doc);

  console.log('one save of a %s MB document, trigger and all:\n',
    (payload.length / 1048576).toFixed(1));
  const t = Date.now();
  await c.query(
    `insert into site_state (key, value, rev, updated_at)
     values ('cal-hockey-site', $1, $2, now())
     on conflict (key) do update set value = excluded.value,
       rev = excluded.rev, updated_at = excluded.updated_at`, [payload, doc.rev]);
  const ms = Date.now() - t;
  const { rows: [h] } = await c.query(
    `select count(*) as rows from site_state_history where key='cal-hockey-site'`);
  console.log('  upsert + history trigger + prune   %sms', ms);
  console.log('  versions kept afterwards           %s', h.rows);
  console.log('\n  budget is 8000ms (statement_timeout for the authenticated role)');
  console.log('  headroom: %sx', (8000 / ms).toFixed(1));
} finally {
  await c.query('rollback');
  await c.end();
  console.log('\nrolled back — nothing changed');
}
