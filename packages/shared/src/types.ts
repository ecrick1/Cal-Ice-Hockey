/** Row types mirroring supabase/migrations/. */

export type Position = 'F' | 'D' | 'G';
export type HomeAway = 'H' | 'A';
/** '' = neither, 'C' = captain, 'A' = alternate. */
export type Captain = '' | 'C' | 'A';

/** seasons.record_override — used only for seasons with no game log. */
export interface RecordOverride {
  w: number;
  l: number;
  t: number;
  gf: number;
  ga: number;
  note?: string;
}

export interface Season {
  id: string;
  name: string;
  is_current: boolean;
  record_override: RecordOverride | null;
  created_at: string;
}

/** An opposing team. Rows, not free text, so they can carry a logo. */
export interface Opponent {
  id: string;
  name: string;
  short_name: string;
  /**
   * Two marks, because one cannot serve both surfaces: dark-ink logos vanish on
   * the console, knocked-out white ones vanish on the public site. Either may be
   * null — the other stands in, and initials stand in for both.
   */
  logo_light_url: string | null;
  logo_dark_url: string | null;
  created_at: string;
}

export type Density = 'comfortable' | 'compact';

/**
 * A staff member's console profile. Auth itself (email, password, sessions)
 * lives in auth.users and is reached through the Supabase client, never here.
 */
export interface Profile {
  id: string;
  display_name: string;
  avatar_url: string | null;
  density: Density;
  default_season_id: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * A human. Everything true of the person regardless of season lives here;
 * career stats key off `id`, so they survive a name being respelled.
 */
export interface Person {
  id: string;
  name: string;
  hometown: string;
  high_school: string;
  prior_team: string;
  shoots: string;
  height: string;
  bio: string;
  photo_url: string | null;
  ep_player_id: number | null;
  created_at: string;
}

/** One person's appearance on one season's roster. */
export interface Player {
  id: string;
  season_id: string;
  person_id: string;
  number: string;
  position: Position;
  year: string;
  captain: Captain;
  /** Manual fallback only — ignored once game_stats rows exist for this player. */
  gp: number;
  g: number;
  a: number;
  pim: number;
  created_at: string;
}

export interface Game {
  id: string;
  season_id: string;
  date: string | null;
  opponent_id: string | null;
  home_away: HomeAway;
  venue: string;
  time: string;
  /** null => the game has not been played; the row is a scheduled fixture. */
  score_us: number | null;
  score_them: number | null;
  ot: boolean;
  ep_game_id: number | null;
  created_at: string;
}

/** One player's line in one game's box score. */
export interface GameStat {
  id: string;
  game_id: string;
  player_id: string;
  /** false = scratched; does not count toward GP. */
  dressed: boolean;
  g: number;
  a: number;
  pim: number;
  saves: number | null;
  goals_against: number | null;
  created_at: string;
}

export interface Coach {
  id: string;
  season_id: string;
  name: string;
  title: string;
  email: string;
  bio: string;
  photo_url: string | null;
  sort: number;
}

export interface News {
  id: string;
  date: string;
  tag: string;
  title: string;
  blurb: string;
  body: string;
  author: string;
  image_url: string | null;
  published: boolean;
  created_at: string;
}

export interface Recruit {
  id: string;
  name: string;
  email: string;
  grad_year: string;
  position: string;
  shoots: string;
  height: string;
  current_team: string;
  gpa: string;
  highlight_link: string;
  message: string;
  read: boolean;
  created_at: string;
}

export type SettingKey = 'tickets_url' | 'contact_email' | 'home_venue';

export interface Setting {
  key: SettingKey;
  value: string;
}

/** The season_records view: W-L-T computed from games that have results. */
export interface SeasonRecordRow {
  season_id: string;
  name: string;
  gp: number;
  w: number;
  l: number;
  t: number;
  gf: number;
  ga: number;
}

/**
 * The player_season_stats view. Totals come from game_stats when box scores
 * exist for the player, and fall back to the manual columns otherwise —
 * `from_box_scores` says which.
 */
export interface PlayerSeasonStats {
  player_id: string;
  season_id: string;
  person_id: string;
  name: string;
  number: string;
  position: Position;
  year: string;
  captain: Captain;
  gp: number;
  g: number;
  a: number;
  pts: number;
  pim: number;
  saves: number;
  goals_against: number;
  from_box_scores: boolean;
}

/** The player_career_stats view: player_season_stats summed per person. */
export interface PlayerCareerStats {
  person_id: string;
  name: string;
  seasons: number;
  gp: number;
  g: number;
  a: number;
  pts: number;
  pim: number;
}
