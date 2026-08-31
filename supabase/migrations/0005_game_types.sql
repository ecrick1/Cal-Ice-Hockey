-- Cal Ice Hockey — playoff and exhibition games.
--
-- Until now every game counted the same way. Playoffs need to be identifiable
-- (they are usually reported separately from the regular-season record), and
-- exhibitions must not count toward the record at all.

alter table games add column game_type text not null default 'regular'
  check (game_type in ('regular', 'playoff', 'exhibition'));

-- Free text so it fits any league's bracket naming: "Quarterfinal",
-- "ACHA Regionals R1", "Pac-8 Championship".
alter table games add column round_label text not null default '';

comment on column games.game_type is
  'regular | playoff | exhibition. Exhibitions are excluded from the record.';
comment on column games.round_label is
  'Optional bracket label, shown next to playoff games.';

create index games_type_idx on games(season_id, game_type);

-- ============================================================
-- season_records, rebuilt
-- ============================================================
-- w/l/t/gf/ga stay the headline record and now cover regular season plus
-- playoffs, excluding exhibitions. The split is exposed alongside so the site
-- can show "20-10-0 (2-1 in playoffs)" without a second query.

drop view if exists season_records;

create view season_records as
with counted as (
  select
    g.season_id,
    g.game_type,
    g.score_us,
    g.score_them,
    -- Exhibitions are played but never counted.
    (g.score_us is not null and g.game_type <> 'exhibition') as counts
  from games g
)
select
  s.id                                                                  as season_id,
  s.name,
  count(*) filter (where c.counts)                                      as gp,
  count(*) filter (where c.counts and c.score_us > c.score_them)        as w,
  count(*) filter (where c.counts and c.score_us < c.score_them)        as l,
  count(*) filter (where c.counts and c.score_us = c.score_them)        as t,
  coalesce(sum(c.score_us)   filter (where c.counts), 0)                as gf,
  coalesce(sum(c.score_them) filter (where c.counts), 0)                as ga,

  count(*) filter (where c.counts and c.game_type = 'regular' and c.score_us > c.score_them) as regular_w,
  count(*) filter (where c.counts and c.game_type = 'regular' and c.score_us < c.score_them) as regular_l,
  count(*) filter (where c.counts and c.game_type = 'regular' and c.score_us = c.score_them) as regular_t,

  count(*) filter (where c.counts and c.game_type = 'playoff' and c.score_us > c.score_them) as playoff_w,
  count(*) filter (where c.counts and c.game_type = 'playoff' and c.score_us < c.score_them) as playoff_l,
  count(*) filter (where c.counts and c.game_type = 'playoff' and c.score_us = c.score_them) as playoff_t,

  count(*) filter (where c.game_type = 'exhibition' and c.score_us is not null)              as exhibition_gp
from seasons s
left join counted c on c.season_id = s.id
group by s.id, s.name;
