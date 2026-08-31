import { createPublicClient, hasSupabaseEnv } from '@cal/shared/supabase/public';
import { recordFromView, formatRecord } from '@cal/shared';
import type { Season, SeasonRecordRow } from '@cal/shared';

export const revalidate = 60;

/**
 * Phase 1 scaffold page: proves the anon-key read path and the seeded data.
 * Phase 2 replaces this with the real home page (headlines, record slab,
 * scoreboard strip, recruit CTA) per the prototype.
 */
export default async function HomePage() {
  if (!hasSupabaseEnv()) {
    return (
      <main className="wrap section">
        <p className="eyebrow">Setup</p>
        <h1 className="h1">No database yet</h1>
        <p className="blg">
          Create a Supabase project, then copy <code>.env.example</code> to <code>.env.local</code>{' '}
          and fill in the URL and anon key.
        </p>
      </main>
    );
  }

  const supabase = createPublicClient();

  const [{ data: seasons, error }, { data: records }, { count: playerCount }] = await Promise.all([
    supabase.from('seasons').select('*').order('name', { ascending: false }),
    supabase.from('season_records').select('*'),
    supabase.from('players').select('*', { count: 'exact', head: true }),
  ]);

  if (error) {
    return (
      <main className="wrap section">
        <p className="eyebrow">Database</p>
        <h1 className="h2">Query failed</h1>
        <p className="blg">{error.message}</p>
        <p className="bsm">Has the migration been pushed? Try <code>pnpm db:push</code>.</p>
      </main>
    );
  }

  const list = (seasons ?? []) as Season[];
  const rows = (records ?? []) as SeasonRecordRow[];

  return (
    <main className="wrap section">
      <p className="eyebrow">Cal Ice Hockey</p>
      <h1 className="h1">Phase 1 scaffold</h1>
      <p className="blg">
        Connected. {list.length} season{list.length === 1 ? '' : 's'}, {playerCount ?? 0} players.
      </p>

      {list.length === 0 ? (
        <p className="blg">
          No seasons yet — run <code>pnpm seed</code>.
        </p>
      ) : (
        <table style={{ marginTop: 24, borderCollapse: 'collapse', width: '100%', maxWidth: 680 }}>
          <thead>
            <tr>
              {['Season', 'Record', 'GF-GA', 'Source'].map((h) => (
                <th key={h} className="h6" style={{ textAlign: 'left', padding: '8px 12px' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {list.map((s) => {
              const view = rows.find((r) => r.season_id === s.id);
              const rec = view ? recordFromView(view, s.record_override) : null;
              return (
                <tr key={s.id} style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={{ padding: '8px 12px' }}>
                    {s.name}
                    {s.is_current ? ' (current)' : ''}
                  </td>
                  <td style={{ padding: '8px 12px' }}>{rec ? formatRecord(rec) : '—'}</td>
                  <td style={{ padding: '8px 12px' }}>{rec ? `${rec.gf}-${rec.ga}` : '—'}</td>
                  <td className="bsm" style={{ padding: '8px 12px', color: 'var(--muted)' }}>
                    {rec?.imported ? 'imported' : 'game log'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </main>
  );
}
