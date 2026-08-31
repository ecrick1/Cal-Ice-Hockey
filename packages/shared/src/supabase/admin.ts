import { createClient } from '@supabase/supabase-js';

/**
 * Service-role client. Bypasses RLS entirely.
 *
 * Server-only: node scripts and route handlers. Importing this from anything
 * that reaches a client bundle leaks full database access.
 */
export function createAdminClient() {
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!key) throw new Error('SUPABASE_SERVICE_ROLE_KEY is not set');

  return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
