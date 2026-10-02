// Merge official completed game sheets into a draft without replacing editorial content.
const key = (name) => String(name || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
const nameOf = (p) => [p.firstName, p.lastName].filter(Boolean).join(' ');
const yes = (v) => v === true || v === 1 || v === '1';
const num = (v) => Number(v) || 0;
const minutes = (value) => { const [m, s] = String(value || '0:00').split(':').map(Number); return m + (s || 0) / 60; };
const lineOf = (p) => ({ dressed: true, g: num(p.stats.goals), a: num(p.stats.assists), pim: num(p.stats.penaltyMinutes),
  shots: num(p.stats.shots), ppg: 0, shg: 0, gwg: 0,
  ...(p.info.position === 'G' ? { saves: num(p.stats.saves), ga: num(p.stats.goalsAgainst), minutes: minutes(p.stats.timeOnIce) } : {}) });

export function mergeAchaGames(site, seasonName, summaries) {
  const season = site.seasons[seasonName];
  if (!season) throw new Error('Season no longer exists.');
  const roster = season.roster.map((p) => ({ ...p }));
  const gameStats = { ...site.gameStats }, opponentStats = { ...site.opponentStats };
  const updates = new Map();
  for (const sheet of summaries) {
    const details = sheet.details || {};
    if (!yes(details.final)) continue;
    const game = season.schedule.find((g) => String(g.achaGameId) === String(details.id));
    if (!game || String(details.seasonId) !== String(season.achaSeasonId)) throw new Error('The ACHA game does not match this season.');
    const home = /California-Berkeley/i.test(sheet.homeTeam?.info?.name || '');
    const away = /California-Berkeley/i.test(sheet.visitingTeam?.info?.name || '');
    if (home === away) throw new Error('Cannot identify Cal in the ACHA game.');
    const us = home ? sheet.homeTeam : sheet.visitingTeam;
    const them = home ? sheet.visitingTeam : sheet.homeTeam;
    const people = [...us.skaters, ...us.goalies];
    const ids = new Map();
    for (const p of people) {
      const name = nameOf(p.info);
      let found = roster.find((r) => String(r.achaPlayerId) === String(p.info.id));
      if (!found) {
        const hits = roster.filter((r) => key(r.name) === key(name));
        if (hits.length > 1) throw new Error('Duplicate roster name: ' + name + '. Link the player before refreshing.');
        found = hits[0];
      }
      if (!found) { found = { id: 'acha-' + season.achaSeasonId + '-player-' + p.info.id, name, number: String(p.info.jerseyNumber), position: p.info.position, stats: {} }; roster.push(found); }
      found.achaPlayerId = String(p.info.id);
      ids.set(String(p.info.id), found.id);
    }
    const lines = Object.fromEntries(roster.map((p) => [p.id, { dressed: false }]));
    for (const p of people) lines[ids.get(String(p.info.id))] = lineOf(p);
    const theirs = [...them.skaters, ...them.goalies].map((p) => ({ id: 'acha-' + p.info.id, name: nameOf(p.info), number: p.info.jerseyNumber, position: p.info.position, ...lineOf(p) }));
    const sideOf = (id) => String(id) === String(us.info.id) ? 'us' : 'them';
    const playerId = (id, side) => side === 'us' ? ids.get(String(id)) || null : 'acha-' + id;
    const plays = [], periodShots = {};
    for (const period of sheet.periods || []) {
      const per = period.info.shortName || period.info.id;
      // HockeyTech uses elapsed time; the console displays time remaining.
      const clock = (at) => { const seconds = Math.max(0, (Number(per) <= 3 ? 1200 : 300) - Math.round(minutes(at) * 60)); return Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0'); };
      periodShots[per] = { us: num(period.stats[home ? 'homeShots' : 'visitingShots']), them: num(period.stats[home ? 'visitingShots' : 'homeShots']) };
      const events = [];
      for (const goal of period.goals || []) {
        const side = sideOf(goal.team.id), prop = goal.properties || {};
        const id = playerId(goal.scoredBy.id, side);
        const line = side === 'us' ? lines[id] : theirs.find((p) => p.id === id);
        if (line) { line.ppg += yes(prop.isPowerPlay) ? 1 : 0; line.shg += yes(prop.isShortHanded) ? 1 : 0; line.gwg += yes(prop.isGameWinningGoal) ? 1 : 0; }
        events.push({ elapsed: minutes(goal.time), id: 'acha-goal-' + goal.game_goal_id, kind: 'goal', team: side, period: String(per), clock: clock(goal.time),
          scorer: nameOf(goal.scoredBy), scorerId: id, assists: (goal.assists || []).map(nameOf), assistIds: (goal.assists || []).map((p) => playerId(p.id, side)),
          strength: yes(prop.isEmptyNet) ? 'EN' : yes(prop.isPowerPlay) ? 'PP' : yes(prop.isShortHanded) ? 'SH' : 'EV', emptyNet: yes(prop.isEmptyNet) });
      }
      for (const pen of period.penalties || []) {
        const side = sideOf(pen.againstTeam.id);
        events.push({ elapsed: minutes(pen.time), id: 'acha-penalty-' + pen.game_penalty_id, kind: 'penalty', team: side, period: String(per), clock: clock(pen.time),
          player: nameOf(pen.takenBy || {}) || 'Bench', playerId: pen.takenBy ? playerId(pen.takenBy.id, side) : null, minutes: num(pen.minutes), infraction: pen.description });
      }
      plays.push(...events.sort((a, b) => a.elapsed - b.elapsed).map(({ elapsed, ...event }) => event));
    }
    const result = { us: num(us.stats.goals), them: num(them.stats.goals), ot: (sheet.periods || []).some((p) => Number(p.info.id) > 3), so: !!sheet.hasShootout };
    // Shootout sheets need attempt/decision mapping; refuse a partial import.
    if (sheet.hasShootout) throw new Error('This game ended in a shootout. Import its full game sheet in the box-score editor.');
    if (Object.values(lines).reduce((n, p) => n + num(p.g), 0) !== result.us || theirs.reduce((n, p) => n + num(p.g), 0) !== result.them) throw new Error('The ACHA player goals do not reconcile with the final score yet. Try again after the league corrects the sheet.');
    plays.push({ id: 'acha-end-' + details.id, kind: 'game', phase: 'end', period: String(sheet.periods.at(-1)?.info.shortName || '3'), clock: '00:00', ...result });
    updates.set(game.id, { ...game, result, plays, lineup: { dressed: people.map((p) => ids.get(String(p.info.id))), starters: people.filter((p) => yes(p.starting)).map((p) => ids.get(String(p.info.id))), goalie: ids.get(String(us.goalies.find((p) => yes(p.starting))?.info.id)) || '' }, live: { us: result.us, them: result.them, period: 'Final', running: false, clockMs: 0, shotsUs: num(us.stats.shots), shotsThem: num(them.stats.shots), periodShots },
      achaSource: 'https://www.achahockey.org/stats/game-center/' + details.id });
    gameStats[game.id] = lines; opponentStats[game.id] = theirs;
  }
  // Ensure newly added players have explicit scratches in other imported games.
  for (const id of updates.keys()) for (const p of roster) gameStats[id][p.id] ||= { dressed: false };
  return { ...site, gameStats, opponentStats, seasons: { ...site.seasons, [seasonName]: { ...season, roster, record: null, schedule: season.schedule.map((g) => updates.get(g.id) || g) } } };
}
