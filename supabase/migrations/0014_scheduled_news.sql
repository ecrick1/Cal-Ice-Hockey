-- Scheduled publishing for news stories.
--
-- A story is public when it is published AND its publish_at moment has passed.
-- publish_at null means "as soon as it is published", which is what every
-- existing row wants, so no backfill is needed.
--
-- This is enforced in the row-level security policy, not just in the client:
-- a scheduled story must not be fetchable with the anon key, or the schedule
-- is a suggestion rather than an embargo.

alter table news add column if not exists publish_at timestamptz;

drop policy if exists "public read news" on news;

create policy "public read news" on news for select
  using (published = true and (publish_at is null or publish_at <= now()));

-- The public site orders by date and now filters on publish_at on every read.
create index if not exists news_publish_at_idx on news (publish_at);
