import { createClient } from '@supabase/supabase-js';

/**
 * Anon-key client with no cookie binding.
 *
 * The public site is read-only and identical for every visitor, so its reads
 * must not touch cookies() — that would opt every page into dynamic rendering
 * and defeat ISR. Use this for all of apps/web; use ./server only where an
 * authenticated session matters (the admin app).
 */
export function createPublicClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { persistSession: false, autoRefreshToken: false } },
  );
}

/** False until the Supabase project exists and .env.local is filled in. */
export function hasSupabaseEnv(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  );
}
