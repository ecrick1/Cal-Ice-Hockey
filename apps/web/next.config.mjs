import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { config } from 'dotenv';

// Next loads .env files from the app directory, but in this monorepo the single
// source of truth is the root .env.local. Load it here so both apps and the
// seed script read the same credentials.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
config({ path: path.join(root, '.env.local') });
config({ path: path.join(root, '.env') });

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@cal/shared'],
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  },
  images: {
    remotePatterns: [
      // Supabase Storage: player headshots and news images from the `media` bucket.
      { protocol: 'https', hostname: '*.supabase.co', pathname: '/storage/v1/object/public/**' },
    ],
  },
};

export default nextConfig;
