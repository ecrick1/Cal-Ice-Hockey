-- Cal Ice Hockey — player weight.
--
-- Text rather than an integer, to match `height` and to survive whatever a
-- coach types: "185", "185 lbs", "84 kg". Rosters are transcribed by hand from
-- a dozen sources and a strict numeric column would reject half of them.

alter table people add column weight text not null default '';

comment on column people.weight is 'As listed, e.g. "185 lbs". Free text like height.';
