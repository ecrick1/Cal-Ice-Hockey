import details from '../data/enrichment/elite-prospects-2026-27.json' with { type: 'json' };
import existingRoster from '../data/enrichment/existing-roster-2026-27.json' with { type: 'json' };

// A reviewed, season-specific import. Never replace an editor's existing
// values, and remember the import so deliberately cleared values stay clear.
export function addPlayerDetails(site) {
  const season = site.seasons?.[details.season];
  if (!season?.roster) return site;
  const sources = new Map(details.players.map(p => [p.id, p]));
  const clubSources = new Map(existingRoster.players.map(p => [p.id, p]));
  const returningNames = new Set(Object.entries(site.seasons)
    .filter(([year]) => year < details.season)
    .flatMap(([, value]) => (value.roster || []).map(p => p.name?.trim().toLowerCase())));
  let changed = false;
  const roster = season.roster.map(player => {
    const clubEntry = clubSources.get(player.id);
    if (clubEntry?.name === player.name && !player.clubRosterImported) {
      const additions = Object.fromEntries(Object.entries(clubEntry.fields)
        .filter(([key, value]) => value && (!String(player[key] || '').trim() ||
          (key === 'year' && player.newPlayerClassAssigned && player.year === 'Fr'))));
      player = { ...player, ...additions, clubRosterImported: true,
        clubRosterSource: existingRoster.source };
      changed = true;
    }
    // Replace only the club-imported originals; leave custom uploads alone.
    const originalPhoto = clubEntry?.fields.photo;
    if (originalPhoto && player.photo === originalPhoto) {
      player = { ...player, photo: originalPhoto.replace('/roster/', '/roster-clean/') };
      changed = true;
    }
    const entry = sources.get(player.id);
    if (!entry || entry.name !== player.name) return player;
    // Requested class assumption applies only to newcomers, not returning
    // players whose class happens to be missing. Keep it editable afterward.
    if (!player.year && !player.newPlayerClassAssigned &&
        !returningNames.has(player.name.trim().toLowerCase())) {
      player = { ...player, year: 'Fr', newPlayerClassAssigned: true };
      changed = true;
    }
    if (entry.rosterDetails && !player.eliteProspectsRosterDetailsImported) {
      const additions = Object.fromEntries(Object.entries(entry.rosterDetails)
        .filter(([key, value]) => value && !String(player[key] || '').trim()));
      player = { ...player, ...additions,
        eliteProspectsRosterDetailsImported: details.checkedAt,
        eliteProspectsRosterDetailsSource: entry.rosterDetailsSource };
      changed = true;
    }
    if (player.eliteProspectsImported) return player;
    changed = true;
    return {
      ...player,
      weight: player.weight || entry.weight,
      birthday: player.birthday || entry.birthday,
      eliteProspectsSource: entry.source,
      eliteProspectsImported: details.checkedAt,
    };
  });
  return changed ? { ...site, seasons: { ...site.seasons, [details.season]: { ...season, roster } } } : site;
}
