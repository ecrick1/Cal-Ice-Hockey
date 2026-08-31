import { createClient } from '@cal/shared/supabase/server';
import { hasSupabaseEnv } from '@cal/shared/supabase/public';

export const dynamic = 'force-dynamic';

/**
 * Phase 1 scaffold. Phase 3 replaces this with magic-link auth plus the
 * News / Roster / Schedule / Seasons / Recruits / Settings screens.
 */
export default async function AdminHome() {
  if (!hasSupabaseEnv()) {
    return (
      <main className="wrap section">
        <p className="eyebrow">Setup</p>
        <h1 className="h1">No database yet</h1>
        <p className="blg">
          Create a Supabase project, then copy <code>.env.example</code> to <code>.env.local</code>.
        </p>
      </main>
    );
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <main className="wrap section">
      <p className="eyebrow">Cal Ice Hockey</p>
      <h1 className="h1">Admin</h1>
      <p className="blg">
        {user ? `Signed in as ${user.email}.` : 'Not signed in. Magic-link auth lands in Phase 3.'}
      </p>
    </main>
  );
}
