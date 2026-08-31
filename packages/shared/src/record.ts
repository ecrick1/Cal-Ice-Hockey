import type { Game, RecordOverride, SeasonRecordRow } from './types';

export interface TeamRecord extends RecordOverride {
  gp: number;
  /** True when the numbers came from record_override rather than a game log. */
  imported: boolean;
}

const EMPTY: TeamRecord = { w: 0, l: 0, t: 0, gf: 0, ga: 0, gp: 0, imported: false };

/**
 * A season's record is computed from games that have results. `record_override`
 * is a fallback for imported historical seasons that have no game log at all —
 * it must never mask a real one. Mirrors computeRecord() in the prototype.
 */
export function computeRecord(
  games: Pick<Game, 'score_us' | 'score_them'>[],
  override?: RecordOverride | null,
): TeamRecord {
  const played = games.filter((g) => g.score_us !== null && g.score_them !== null);

  if (played.length === 0) {
    return override ? { ...override, gp: override.w + override.l + override.t, imported: true } : { ...EMPTY };
  }

  const rec = { ...EMPTY, gp: played.length };
  for (const g of played) {
    const us = g.score_us as number;
    const them = g.score_them as number;
    if (us > them) rec.w += 1;
    else if (us < them) rec.l += 1;
    else rec.t += 1;
    rec.gf += us;
    rec.ga += them;
  }
  return rec;
}

/** Same rule, applied to a row of the season_records view. */
export function recordFromView(row: SeasonRecordRow, override?: RecordOverride | null): TeamRecord {
  if (row.gp === 0 && override) {
    return { ...override, gp: override.w + override.l + override.t, imported: true };
  }
  return { w: row.w, l: row.l, t: row.t, gf: row.gf, ga: row.ga, gp: row.gp, imported: false };
}

export function formatRecord(r: TeamRecord): string {
  return `${r.w}-${r.l}-${r.t}`;
}

/** Win percentage counting ties as half a win. Returns 0 for an empty record. */
export function winPct(r: TeamRecord): number {
  const decided = r.w + r.l + r.t;
  return decided === 0 ? 0 : (r.w + r.t * 0.5) / decided;
}
