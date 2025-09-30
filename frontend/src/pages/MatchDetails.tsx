import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { matchesAPI } from '../services/api'
import { ArrowLeft, Trophy, Users, Target } from 'lucide-react'
import { MatchDetails as MatchDetailsType, MatchPlayer } from '../types'

const MatchDetails: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>()
  const navigate = useNavigate()

  const { data: match, isLoading, error } = useQuery<MatchDetailsType>({
    queryKey: ['match', matchId],
    queryFn: () => matchesAPI.getMatch(matchId!),
    enabled: !!matchId
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (error || !match) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Match not found</h3>
        <p className="text-gray-500 mb-6">
          The match you're looking for doesn't exist or you don't have access to it.
        </p>
        <button
          onClick={() => navigate('/matches')}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Back to Matches
        </button>
      </div>
    )
  }

  // Separate players by team
  const team1Players = match.players.filter((p: MatchPlayer) => p.team === 1)
  const team2Players = match.players.filter((p: MatchPlayer) => p.team === 2)

  const getPlayerKD = (player: MatchPlayer) => {
    return player.deaths > 0 ? (player.kills / player.deaths).toFixed(2) : player.kills.toFixed(2)
  }

  const renderPlayerRow = (player: MatchPlayer) => {
    const isMVP = player.steam_id === match.mvp_player

    return (
      <tr key={player.steam_id} className={isMVP ? 'bg-yellow-50' : ''}>
        <td className="px-4 py-3 text-sm font-medium text-gray-900">
          <div className="flex items-center">
            {isMVP && <Trophy className="h-4 w-4 text-yellow-500 mr-2" />}
            {player.player_name || 'Unknown'}
          </div>
        </td>
        <td className="px-4 py-3 text-sm text-gray-700">{player.kills}</td>
        <td className="px-4 py-3 text-sm text-gray-700">{player.deaths}</td>
        <td className="px-4 py-3 text-sm text-gray-700">{player.assists}</td>
        <td className="px-4 py-3 text-sm text-gray-700">{getPlayerKD(player)}</td>
        <td className="px-4 py-3 text-sm text-gray-700">{player.headshot_percentage.toFixed(1)}%</td>
      </tr>
    )
  }

  const team1Won = match.winner === 1
  const team2Won = match.winner === 2

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/matches')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Matches
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{match.map_name}</h1>
        <p className="text-gray-600 mt-2">
          {match.started_at ? new Date(match.started_at).toLocaleString() : 'Date unknown'}
        </p>
      </div>

      {/* Match Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Score */}
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">Final Score</div>
            <div className="text-4xl font-bold">
              <span className={team1Won ? 'text-green-600' : 'text-gray-900'}>
                {match.score_team1}
              </span>
              <span className="text-gray-400 mx-3">:</span>
              <span className={team2Won ? 'text-green-600' : 'text-gray-900'}>
                {match.score_team2}
              </span>
            </div>
            <div className="text-sm text-gray-500 mt-2">
              {match.total_rounds} rounds played
            </div>
          </div>

          {/* Stats */}
          <div className="border-l border-r border-gray-200 px-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center text-gray-700">
                <Target className="h-5 w-5 mr-2" />
                <span className="text-sm">Average K/D</span>
              </div>
              <span className="font-semibold">{match.average_kd_ratio}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center text-gray-700">
                <Users className="h-5 w-5 mr-2" />
                <span className="text-sm">Players</span>
              </div>
              <span className="font-semibold">{match.players.length}</span>
            </div>
          </div>

          {/* MVP */}
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">Match MVP</div>
            <div className="flex items-center justify-center text-xl font-bold text-yellow-600">
              <Trophy className="h-6 w-6 mr-2" />
              {match.players.find((p: MatchPlayer) => p.steam_id === match.mvp_player)?.player_name || 'Unknown'}
            </div>
          </div>
        </div>
      </div>

      {/* Team 1 */}
      <div className="bg-white rounded-lg shadow">
        <div className={`px-6 py-4 border-b ${team1Won ? 'bg-green-50 border-green-200' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
              <h3 className="text-lg font-medium text-gray-900">
                Team 1 {team1Won && <span className="text-green-600 ml-2">(Winner)</span>}
              </h3>
            </div>
            <div className="text-sm text-gray-600">
              {match.team_stats.team1.total_kills} kills · {match.team_stats.team1.total_deaths} deaths
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Player</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">K</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">D</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">A</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">K/D</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">HS%</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {team1Players.map((player: MatchPlayer) => renderPlayerRow(player))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Team 2 */}
      <div className="bg-white rounded-lg shadow">
        <div className={`px-6 py-4 border-b ${team2Won ? 'bg-green-50 border-green-200' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-orange-500 rounded-full mr-3"></div>
              <h3 className="text-lg font-medium text-gray-900">
                Team 2 {team2Won && <span className="text-green-600 ml-2">(Winner)</span>}
              </h3>
            </div>
            <div className="text-sm text-gray-600">
              {match.team_stats.team2.total_kills} kills · {match.team_stats.team2.total_deaths} deaths
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Player</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">K</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">D</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">A</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">K/D</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">HS%</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {team2Players.map((player: MatchPlayer) => renderPlayerRow(player))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default MatchDetails