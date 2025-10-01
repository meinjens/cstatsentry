import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dashboardAPI, usersAPI, matchesAPI } from '../services/api'
import {
  Users,
  Shield,
  AlertTriangle,
  Activity,
  Clock,
  Target,
  UserPlus,
  RefreshCw
} from 'lucide-react'

const Dashboard: React.FC = () => {
  const queryClient = useQueryClient()
  const [isSyncing, setIsSyncing] = useState(false)

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: dashboardAPI.getSummary
  })

  const { data: recentActivity, isLoading: activityLoading } = useQuery({
    queryKey: ['dashboard-recent'],
    queryFn: dashboardAPI.getRecentActivity
  })

  const { data: teammates } = useQuery({
    queryKey: ['teammates'],
    queryFn: () => usersAPI.getTeammates(10, 1)
  })

  const syncMutation = useMutation({
    mutationFn: matchesAPI.triggerSync,
    onSuccess: () => {
      // Refresh dashboard data
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-recent'] })
      setTimeout(() => setIsSyncing(false), 2000)
    },
    onError: (error) => {
      console.error('Sync failed:', error)
      setIsSyncing(false)
    }
  })

  const handleSync = () => {
    setIsSyncing(true)
    syncMutation.mutate()
  }

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  const stats = [
    {
      name: 'Total Matches',
      value: summary?.total_matches || 0,
      icon: Target,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Players Analyzed',
      value: summary?.total_players_analyzed || 0,
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Suspicious Players',
      value: summary?.suspicious_players || 0,
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      name: 'High Risk Players',
      value: summary?.high_risk_players || 0,
      icon: Shield,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    }
  ]

  const formatLastSync = (lastSync: string | null) => {
    if (!lastSync) return 'Never'
    return new Date(lastSync).toLocaleString()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Monitor suspicious player activity and detection results
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${stat.bgColor} rounded-md p-3`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Last Sync Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-900">Last Sync:</span>
            <span className="text-sm text-gray-600 ml-2">
              {formatLastSync(summary?.last_sync || null)}
            </span>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              Recent Analyses
            </h3>
          </div>
          <div className="p-6">
            {activityLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
              </div>
            ) : recentActivity?.recent_analyses?.length ? (
              <div className="space-y-3">
                {recentActivity.recent_analyses.slice(0, 5).map((analysis) => (
                  <div key={analysis.analysis_id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Player {analysis.steam_id.slice(-6)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(analysis.analyzed_at).toLocaleString()}
                      </p>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      analysis.suspicion_score >= 80
                        ? 'bg-red-100 text-red-800'
                        : analysis.suspicion_score >= 60
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {analysis.suspicion_score}% risk
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No recent analyses</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              New Flags
            </h3>
          </div>
          <div className="p-6">
            {recentActivity?.new_flags?.length ? (
              <div className="space-y-3">
                {recentActivity.new_flags.slice(0, 5).map((flag, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{flag.type}</p>
                      <p className="text-xs text-gray-500">{flag.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No new flags detected</p>
            )}
          </div>
        </div>

        {/* Frequent Teammates */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <UserPlus className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Frequent Teammates</h3>
            </div>
          </div>
          <div className="p-6">
            {teammates && teammates.length > 0 ? (
              <div className="space-y-3">
                {teammates.map((teammate) => (
                  <div key={teammate.player_steam_id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-md">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                        <Users className="h-5 w-5 text-primary-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{teammate.player_name}</p>
                        <p className="text-xs text-gray-500">
                          Last seen: {new Date(teammate.last_seen).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-primary-600">
                        {teammate.matches_together}
                      </p>
                      <p className="text-xs text-gray-500">matches</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No teammates found yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard