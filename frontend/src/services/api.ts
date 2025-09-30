import axios from 'axios'
import type {
  User,
  Player,
  PlayerWithAnalysis,
  PlayerAnalysis,
  Match,
  AuthResponse,
  DashboardSummary,
  MonthlyMatchData,
  DetectionTrend,
  FlagStatistic,
  MatchDetails
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  getSteamLoginUrl: async (): Promise<{ auth_url: string }> => {
    const response = await api.get('/auth/steam/login')
    return response.data
  },

  handleSteamCallback: async (params: URLSearchParams): Promise<AuthResponse> => {
    const response = await api.get(`/auth/steam/callback?${params.toString()}`)
    return response.data
  },

  refreshToken: async (): Promise<{ access_token: string }> => {
    const response = await api.post('/auth/refresh')
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
}

// Users API
export const usersAPI = {
  getProfile: async (): Promise<User> => {
    const response = await api.get('/users/me')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put('/users/me', data)
    return response.data
  },

  getTeammates: async (limit = 50, minMatches = 1): Promise<Array<{
    player_steam_id: string
    player_name: string
    matches_together: number
    first_seen: string
    last_seen: string
    relationship_type: string
  }>> => {
    const response = await api.get(`/users/me/teammates?limit=${limit}&min_matches=${minMatches}`)
    return response.data
  },
}

// Players API
export const playersAPI = {
  getPlayer: async (steamId: string): Promise<PlayerWithAnalysis> => {
    const response = await api.get(`/players/${steamId}`)
    return response.data
  },

  getPlayerAnalysisHistory: async (
    steamId: string,
    limit = 10
  ): Promise<PlayerAnalysis[]> => {
    const response = await api.get(`/players/${steamId}/analysis?limit=${limit}`)
    return response.data
  },

  triggerPlayerAnalysis: async (steamId: string): Promise<{ message: string; status: string }> => {
    const response = await api.post(`/players/${steamId}/analyze`)
    return response.data
  },

  getSuspiciousPlayers: async (
    minScore = 60,
    limit = 50
  ): Promise<Player[]> => {
    const response = await api.get(`/players?min_suspicion_score=${minScore}&limit=${limit}`)
    return response.data
  },
}

// Matches API
export const matchesAPI = {
  getMatches: async (limit = 50, offset = 0): Promise<{
    matches: Match[]
    total: number
    limit: number
    offset: number
  }> => {
    const response = await api.get(`/matches?limit=${limit}&offset=${offset}`)
    return response.data
  },

  getMatch: async (matchId: string): Promise<MatchDetails> => {
    const response = await api.get(`/matches/${matchId}`)
    return response.data
  },

  triggerSync: async (): Promise<{ message: string; status: string }> => {
    const response = await api.post('/matches/sync')
    return response.data
  },

  getSyncStatus: async (): Promise<{
    status: string
    last_sync: string | null
    sync_enabled: boolean
  }> => {
    const response = await api.get('/matches/sync/status')
    return response.data
  },
}

// Dashboard API
export const dashboardAPI = {
  getSummary: async (): Promise<DashboardSummary> => {
    const response = await api.get('/dashboard/summary')
    return response.data
  },

  getRecentActivity: async (): Promise<{
    recent_analyses: PlayerAnalysis[]
    new_flags: FlagStatistic[]
    updated_players: Player[]
  }> => {
    const response = await api.get('/dashboard/recent')
    return response.data
  },

  getStatistics: async (): Promise<{
    matches_by_month: MonthlyMatchData[]
    suspicion_score_distribution: Record<string, number>
    detection_trends: DetectionTrend[]
    most_common_flags: FlagStatistic[]
  }> => {
    const response = await api.get('/dashboard/statistics')
    return response.data
  },
}

export default api