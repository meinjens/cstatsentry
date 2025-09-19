import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { playersAPI } from '../services/api'
import {
  Shield,
  Clock,
  MapPin,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye
} from 'lucide-react'

const PlayerDetail: React.FC = () => {
  const { steamId } = useParams<{ steamId: string }>()

  const { data: player, isLoading } = useQuery({
    queryKey: ['player', steamId],
    queryFn: () => playersAPI.getPlayer(steamId!),
    enabled: !!steamId
  })

  useQuery({
    queryKey: ['player-analysis', steamId],
    queryFn: () => playersAPI.getPlayerAnalysisHistory(steamId!, 10),
    enabled: !!steamId
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (!player) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">Player not found</h3>
      </div>
    )
  }

  const getVisibilityLabel = (state: number | null) => {
    switch (state) {
      case 1: return 'Private'
      case 3: return 'Public'
      default: return 'Unknown'
    }
  }

  const getBanIcon = (banned: boolean) => {
    return banned ? (
      <XCircle className="h-5 w-5 text-red-500" />
    ) : (
      <CheckCircle className="h-5 w-5 text-green-500" />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-6">
          {player.avatar_url ? (
            <img
              className="h-24 w-24 rounded-full"
              src={player.avatar_url}
              alt={player.current_name || 'Player avatar'}
            />
          ) : (
            <div className="h-24 w-24 rounded-full bg-gray-300 flex items-center justify-center">
              <Shield className="h-12 w-12 text-gray-600" />
            </div>
          )}

          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">
              {player.current_name || 'Unknown Player'}
            </h1>
            <p className="text-gray-600 mb-2">Steam ID: {player.steam_id}</p>

            <div className="flex items-center space-x-6 text-sm text-gray-500">
              {player.country_code && (
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 mr-1" />
                  {player.country_code}
                </div>
              )}
              <div className="flex items-center">
                <Eye className="h-4 w-4 mr-1" />
                {getVisibilityLabel(player.visibility_state)}
              </div>
              {player.account_created && (
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  Created {new Date(player.account_created).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>

          <div className="text-right">
            {player.latest_analysis ? (
              <div className={`px-4 py-2 rounded-full text-lg font-medium ${
                player.latest_analysis.suspicion_score >= 80
                  ? 'bg-red-100 text-red-800'
                  : player.latest_analysis.suspicion_score >= 60
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-green-100 text-green-800'
              }`}>
                {player.latest_analysis.suspicion_score}% Risk
              </div>
            ) : (
              <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors">
                Analyze Player
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">CS2 Hours</dt>
                <dd className="mt-1 text-sm text-gray-900">{player.cs2_hours || 0} hours</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Total Games</dt>
                <dd className="mt-1 text-sm text-gray-900">{player.total_games_owned || 0} games</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Logoff</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {player.last_logoff ? new Date(player.last_logoff).toLocaleString() : 'Unknown'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Profile Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {player.profile_updated ? new Date(player.profile_updated).toLocaleString() : 'Never'}
                </dd>
              </div>
            </div>

            {player.previous_names && player.previous_names.length > 0 && (
              <div className="mt-4">
                <dt className="text-sm font-medium text-gray-500">Previous Names</dt>
                <dd className="mt-1">
                  <div className="flex flex-wrap gap-2">
                    {player.previous_names.slice(0, 5).map((name, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {name}
                      </span>
                    ))}
                  </div>
                </dd>
              </div>
            )}
          </div>

          {/* Latest Analysis */}
          {player.latest_analysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Latest Analysis</h3>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Suspicion Score</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    player.latest_analysis.suspicion_score >= 80
                      ? 'bg-red-100 text-red-800'
                      : player.latest_analysis.suspicion_score >= 60
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {player.latest_analysis.suspicion_score}/100
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Confidence Level</span>
                  <span className="text-sm text-gray-900">
                    {Math.round(player.latest_analysis.confidence_level * 100)}%
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Analysis Date</span>
                  <span className="text-sm text-gray-900">
                    {new Date(player.latest_analysis.analyzed_at).toLocaleString()}
                  </span>
                </div>

                {Object.keys(player.latest_analysis.flags || {}).length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-gray-500 block mb-2">Detection Flags</span>
                    <div className="space-y-2">
                      {Object.entries(player.latest_analysis.flags || {}).map(([key, flag]) => (
                        <div key={key} className={`p-3 rounded-md ${
                          flag.severity === 'high' ? 'bg-red-50 border border-red-200' :
                          flag.severity === 'medium' ? 'bg-yellow-50 border border-yellow-200' :
                          'bg-blue-50 border border-blue-200'
                        }`}>
                          <div className="flex justify-between items-center">
                            <span className={`text-sm font-medium ${
                              flag.severity === 'high' ? 'text-red-800' :
                              flag.severity === 'medium' ? 'text-yellow-800' :
                              'text-blue-800'
                            }`}>
                              {key.replace(/_/g, ' ').toUpperCase()}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              flag.severity === 'high' ? 'bg-red-100 text-red-700' :
                              flag.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {flag.severity}
                            </span>
                          </div>
                          <p className={`text-sm mt-1 ${
                            flag.severity === 'high' ? 'text-red-700' :
                            flag.severity === 'medium' ? 'text-yellow-700' :
                            'text-blue-700'
                          }`}>
                            {flag.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Ban Status */}
          {player.ban_info && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Ban Status</h3>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">VAC Banned</span>
                  <div className="flex items-center">
                    {getBanIcon(player.ban_info.vac_banned)}
                    <span className="ml-2 text-sm">
                      {player.ban_info.vac_banned ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Community Banned</span>
                  <div className="flex items-center">
                    {getBanIcon(player.ban_info.community_banned)}
                    <span className="ml-2 text-sm">
                      {player.ban_info.community_banned ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>

                {player.ban_info.number_of_vac_bans > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">VAC Bans</span>
                    <span className="text-sm text-red-600">{player.ban_info.number_of_vac_bans}</span>
                  </div>
                )}

                {player.ban_info.number_of_game_bans > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Game Bans</span>
                    <span className="text-sm text-red-600">{player.ban_info.number_of_game_bans}</span>
                  </div>
                )}

                {player.ban_info.days_since_last_ban > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Days Since Last Ban</span>
                    <span className="text-sm text-gray-900">{player.ban_info.days_since_last_ban}</span>
                  </div>
                )}

                <div className="text-xs text-gray-500 mt-3">
                  Last updated: {new Date(player.ban_info.updated_at).toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Actions</h3>

            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors">
                Trigger Analysis
              </button>

              {player.profile_url && (
                <a
                  href={player.profile_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors text-center"
                >
                  View Steam Profile
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlayerDetail