-- Cal Ice Hockey — cover photos.
--
-- A headshot and a cover are different crops doing different jobs: the headshot
-- is a square-ish portrait for roster tiles, the cover is a wide action shot
-- behind the player page header. One image cannot serve both without being
-- badly cropped in one of the two places.

alter table people add column cover_url text;

comment on column people.photo_url is 'Portrait headshot, roster tiles and player header.';
comment on column people.cover_url is 'Wide banner image behind the player page header.';

-- news.image_url already exists and is the story cover; name its role.
comment on column news.image_url is 'Cover image for the card and the article header.';
