# -*- coding: utf-8 -*-
"""A story about 2019 can mention the 2019 team.

The picker offered this season's roster and nothing else, so writing about
an older game meant every name in it was unlinkable - the men the story was
actually about were the ones you could not link to. "Names in older stories
keep working" was true and beside the point: what already existed rendered,
and nothing new could be added.

The reason for the limit was real, though, and is kept. Every player on file
is past a hundred names in one flat list, and a Link players pass over all
of them reaches back years to wrap a graduate who happens to share a
sentence with the team.

So the picker is scoped rather than capped. A story knows which season it
belongs to - the game it is attached to, or failing that its own date - and
that season's roster comes first, under its own heading. Everyone else
follows, grouped by season, newest first, so a name from any year is
reachable without being the first thing offered.

The automatic pass stays narrow for exactly the old reason: it wraps names
from the story's own season, which is the set it can be confident about.
Anything else is a deliberate choice made from the picker.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""/** Every player across every season, de-duplicated, for the mention picker. */
/* The current roster, and only that.
 *
 * A mention is a link to a player page, so the question is who should be
 * linkable from a story written today - and that is the team, not everyone
 * who has ever worn the shirt. Every season on file put the picker past a
 * hundred names and had Link players quietly reach back years to link a
 * graduate who happened to share a sentence.
 *
 * Mentions already written are untouched: renderInline links whatever name a
 * body carries, so an archived story about a 2019 team still works. This
 * governs what you can add, not what exists. */
function allPlayers(site) {
  const season = (site.seasons || {})[site.currentSeason] || {};
  const byName = new Map();
  for (const p of season.roster || []) {
    if (!p.name) continue;
    if (!byName.has(p.name)) byName.set(p.name, p);
  }
  return [...byName.values()].sort((a, b) => a.name.localeCompare(b.name));
}""",
    """/** The roster of one season, de-duplicated by name. */
function rosterOf(site, seasonName) {
  const season = (site.seasons || {})[seasonName] || {};
  const byName = new Map();
  for (const p of season.roster || []) {
    if (!p.name) continue;
    if (!byName.has(p.name)) byName.set(p.name, p);
  }
  return [...byName.values()].sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * Which season a story belongs to.
 *
 * The game it is attached to knows, and says so exactly. Failing that the
 * date does: a season is the year its schedule covers, so a story filed in
 * November 2019 belongs to whichever season was being played then. Failing
 * both, the season being played now.
 */
function seasonOfPost(site, post) {
  const seasons = site.seasons || {};
  const gid = post && post.gameId;
  if (gid) {
    for (const [sn, se] of Object.entries(seasons)) {
      if ((se.schedule || []).some((g) => g.id === gid)) return sn;
    }
  }
  const d = post && post.date;
  if (d) {
    for (const [sn, se] of Object.entries(seasons)) {
      const dates = (se.schedule || []).map((g) => g.date).filter(Boolean).sort();
      if (dates.length && d >= dates[0] && d <= dates[dates.length - 1]) return sn;
    }
  }
  return site.currentSeason;
}

/**
 * Who this story can mention: its own season first, then everyone else by
 * season, newest first.
 *
 * Scoped rather than capped. The old rule offered the current roster only,
 * which made the men an older story was about the ones it could not link to.
 * A flat list of every player on file is past a hundred names, so the
 * grouping is what makes the whole archive reachable without burying the
 * dozen names actually likely.
 */
function mentionGroups(site, post) {
  const home = seasonOfPost(site, post);
  const seen = new Set();
  const groups = [];
  const take = (sn) => {
    const rows = rosterOf(site, sn).filter((p) => !seen.has(personKey(p.name)));
    rows.forEach((p) => seen.add(personKey(p.name)));
    if (rows.length) groups.push([sn, rows]);
  };
  take(home);
  Object.keys(site.seasons || {}).sort().reverse()
    .filter((sn) => sn !== home)
    .forEach(take);
  return groups;
}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('mentions are scoped to the story, not to today')
