export interface User {
  user_id: number
  steam_id: string
  steam_name: string | null
  avatar_url: string | null
  last_sync: string | null
  sync_enabled: boolean
  created_at: string
  updated_at: string
}

export interface Player {
  steam_id: string
  current_name: string | null
  previous_names: string[] | null
  avatar_url: string | null
  profile_url: string | null
  account_created: string | null
  last_logoff: string | null
  profile_state: number | null
  visibility_state: number | null
  country_code: string | null
  cs2_hours: number
  total_games_owned: number
  profile_updated: string | null
  stats_updated: string | null
  created_at: string
}

export interface PlayerBan {
  steam_id: string
  community_banned: boolean
  vac_banned: boolean
  number_of_vac_bans: number
  days_since_last_ban: number
  number_of_game_bans: number
  economy_ban: string
  updated_at: string
}

export interface AnalysisFlag {
  severity: 'low' | 'medium' | 'high'
  description: string
  confidence: number
  detected_at: string
}

export interface PlayerAnalysis {
  analysis_id: number
  steam_id: string
  analyzed_by: number
  suspicion_score: number
  flags: Record<string, AnalysisFlag>
  confidence_level: number
  analysis_version: string
  notes: string | null
  analyzed_at: string
}

export interface PlayerWithAnalysis extends Player {
  latest_analysis: PlayerAnalysis | null
  ban_info: PlayerBan | null
}

export interface MonthlyMatchData {
  month: string
  match_count: number
}

export interface DetectionTrend {
  date: string
  detection_count: number
  detection_type: string
}

export interface FlagStatistic {
  flag_type: string
  count: number
  percentage: number
}

export interface Match {
  match_id: string
  user_id: number
  match_date: string
  map: string | null
  score_team1: number | null
  score_team2: number | null
  user_team: number | null
  sharing_code: string | null
  leetify_match_id: string | null
  processed: boolean
  created_at: string
}

export interface AuthResponse {
  steam_id: string
  steam_name: string
  avatar_url: string | null
  access_token: string
  token_type: string
}

export interface DashboardSummary {
  total_matches: number
  total_players_analyzed: number
  suspicious_players: number
  high_risk_players: number
  new_detections_today: number
  last_sync: string | null
}