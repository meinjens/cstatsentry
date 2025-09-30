import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { matchesAPI } from '../services/api'
import { Target, Clock, RefreshCw } from 'lucide-react'

const Matches: React.FC = () => {
  const navigate = useNavigate()

  const { data: matchesData, isLoading } = useQuery({
    queryKey: ['matches'],
    queryFn: () => matchesAPI.getMatches(50, 0)
  })

  const { data: syncStatus } = useQuery({
    queryKey: ['sync-status'],
    queryFn: matchesAPI.getSyncStatus,
    refetchInterval: 5000 // Refresh every 5 seconds
  })

  const handleTriggerSync = async () => {
    try {
      await matchesAPI.triggerSync()
      // Refresh sync status
    } catch (error) {
      console.error('Failed to trigger sync:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-600 bg-blue-50'
      case 'completed': return 'text-green-600 bg-green-50'
      case 'failed': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Matches</h1>
        <p className="text-gray-600 mt-2">
          View your CS2 match history and synchronization status
        </p>
      </div>

      {/* Sync Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Synchronization Status</h3>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center">
                <span className="text-gray-600">Status:</span>
                <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(syncStatus?.status || 'idle')}`}>
                  {syncStatus?.status || 'idle'}
                </span>
              </div>
              {syncStatus?.last_sync && (
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-400 mr-1" />
                  <span className="text-gray-600">
                    Last sync: {new Date(syncStatus.last_sync).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={handleTriggerSync}
            disabled={syncStatus?.status === 'running'}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${syncStatus?.status === 'running' ? 'animate-spin' : ''}`} />
            {syncStatus?.status === 'running' ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>
      </div>

      {/* Matches List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Recent Matches ({matchesData?.total || 0})
            </h3>
            <div className="text-sm text-gray-500">
              Showing {matchesData?.matches?.length || 0} of {matchesData?.total || 0}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : matchesData?.matches?.length ? (
          <div className="divide-y divide-gray-200">
            {matchesData.matches.map((match) => (
              <div key={match.match_id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <Target className="h-10 w-10 text-primary-600" />
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">
                        {match.map || 'Unknown Map'}
                      </h4>
                      <p className="text-sm text-gray-500">
                        Match ID: {match.match_id.slice(-8)}
                      </p>
                      <div className="flex items-center mt-1 space-x-4 text-xs text-gray-500">
                        <div className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {new Date(match.match_date).toLocaleString()}
                        </div>
                        {match.score_team1 !== null && match.score_team2 !== null && (
                          <span>
                            Score: {match.score_team1} - {match.score_team2}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      match.processed
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {match.processed ? 'Processed' : 'Pending'}
                    </div>

                    <button
                      onClick={() => navigate(`/matches/${match.match_id}`)}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No matches found</h3>
            <p className="text-gray-500 mb-6">
              Sync your Steam account to import your CS2 match history.
            </p>
            <button
              onClick={handleTriggerSync}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              Sync Matches
            </button>
          </div>
        )}
      </div>

      {/* Pagination */}
      {matchesData?.total && matchesData.total > 50 && (
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing 1 to {Math.min(50, matchesData.total)} of {matchesData.total} results
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50">
                Previous
              </button>
              <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Matches