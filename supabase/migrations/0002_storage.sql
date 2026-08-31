-- Storage bucket for player headshots and news images.
-- 0001_init.sql leaves this as a note; this makes it reproducible.
-- Public read (images are served on the public site); writes require an
-- authenticated session, matching the table policies in 0001.

insert into storage.buckets (id, name, public)
values ('media', 'media', true)
on conflict (id) do nothing;

drop policy if exists "public read media"   on storage.objects;
drop policy if exists "auth upload media"   on storage.objects;
drop policy if exists "auth update media"   on storage.objects;
drop policy if exists "auth delete media"   on storage.objects;

create policy "public read media" on storage.objects
  for select using (bucket_id = 'media');

create policy "auth upload media" on storage.objects
  for insert to authenticated with check (bucket_id = 'media');

create policy "auth update media" on storage.objects
  for update to authenticated using (bucket_id = 'media')
  with check (bucket_id = 'media');

create policy "auth delete media" on storage.objects
  for delete to authenticated using (bucket_id = 'media');
