import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { playersAPI } from '../services/api'
import { Search, Filter, AlertTriangle, Shield } from 'lucide-react'

const Players: React.FC = () => {
  const [minSuspicionScore, setMinSuspicionScore] = useState(60)
  const [searchTerm, setSearchTerm] = useState('')

  const { data: suspiciousPlayers, isLoading } = useQuery({
    queryKey: ['suspicious-players', minSuspicionScore],
    queryFn: () => playersAPI.getSuspiciousPlayers(minSuspicionScore, 50)
  })

  const getSuspicionColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  const getSuspicionLabel = (score: number) => {
    if (score >= 80) return 'High Risk'
    if (score >= 60) return 'Suspicious'
    return 'Low Risk'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Players</h1>
        <p className="text-gray-600 mt-2">
          Monitor and analyze suspicious player behavior
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Players
            </label>
            <div className="relative">
              <Search className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or Steam ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Suspicion Score
            </label>
            <select
              value={minSuspicionScore}
              onChange={(e) => setMinSuspicionScore(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value={0}>All Players (0+)</option>
              <option value={30}>Low Risk (30+)</option>
              <option value={60}>Suspicious (60+)</option>
              <option value={80}>High Risk (80+)</option>
            </select>
          </div>

          <div className="flex items-end">
            <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors flex items-center">
              <Filter className="h-4 w-4 mr-2" />
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Players List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Suspicious Players ({suspiciousPlayers?.length || 0})
          </h3>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : suspiciousPlayers?.length ? (
          <div className="divide-y divide-gray-200">
            {suspiciousPlayers.map((player) => (
              <div key={player.steam_id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {player.avatar_url ? (
                      <img
                        className="h-12 w-12 rounded-full"
                        src={player.avatar_url}
                        alt={player.current_name || 'Player avatar'}
                      />
                    ) : (
                      <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
                        <Shield className="h-6 w-6 text-gray-600" />
                      </div>
                    )}
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">
                        {player.current_name || 'Unknown Player'}
                      </h4>
                      <p className="text-sm text-gray-500">
                        Steam ID: {player.steam_id}
                      </p>
                      <div className="flex items-center mt-1 space-x-4 text-xs text-gray-500">
                        {player.cs2_hours > 0 && (
                          <span>CS2: {player.cs2_hours}h</span>
                        )}
                        {player.total_games_owned > 0 && (
                          <span>Games: {player.total_games_owned}</span>
                        )}
                        {player.account_created && (
                          <span>
                            Created: {new Date(player.account_created).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    {/* Suspicion Score Placeholder */}
                    <div className={`px-3 py-1 rounded-full text-sm font-medium bg-yellow-50 text-yellow-600`}>
                      Pending Analysis
                    </div>

                    <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No suspicious players found</h3>
            <p className="text-gray-500">
              Try adjusting your filters or sync more matches to analyze players.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Players