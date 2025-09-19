import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Save, User, Shield, Database } from 'lucide-react'

const Settings: React.FC = () => {
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    steam_name: user?.steam_name || '',
    sync_enabled: user?.sync_enabled ?? true
  })

  const updateProfileMutation = useMutation({
    mutationFn: usersAPI.updateProfile,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(['user-profile'], updatedUser)
      refreshUser()
      setIsEditing(false)
    }
  })

  const handleSave = () => {
    updateProfileMutation.mutate(formData)
  }

  const handleCancel = () => {
    setFormData({
      steam_name: user?.steam_name || '',
      sync_enabled: user?.sync_enabled ?? true
    })
    setIsEditing(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account preferences and synchronization settings
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Settings */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  Profile Settings
                </h3>
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                  >
                    Edit Profile
                  </button>
                ) : (
                  <div className="space-x-2">
                    <button
                      onClick={handleCancel}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={updateProfileMutation.isPending}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {updateProfileMutation.isPending ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Profile Picture */}
              <div className="flex items-center space-x-4">
                {user?.avatar_url ? (
                  <img
                    className="h-20 w-20 rounded-full"
                    src={user.avatar_url}
                    alt="Profile"
                  />
                ) : (
                  <div className="h-20 w-20 rounded-full bg-gray-300 flex items-center justify-center">
                    <User className="h-10 w-10 text-gray-600" />
                  </div>
                )}
                <div>
                  <h4 className="text-lg font-medium text-gray-900">Profile Picture</h4>
                  <p className="text-sm text-gray-500">
                    Profile picture is synced from your Steam account
                  </p>
                </div>
              </div>

              {/* Steam Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.steam_name}
                    onChange={(e) => setFormData({ ...formData, steam_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Enter display name"
                  />
                ) : (
                  <p className="text-gray-900">{user?.steam_name || 'No name set'}</p>
                )}
              </div>

              {/* Steam ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Steam ID
                </label>
                <p className="text-gray-900 font-mono">{user?.steam_id}</p>
                <p className="text-sm text-gray-500 mt-1">
                  Your Steam ID cannot be changed
                </p>
              </div>

              {/* Account Created */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Account Created
                </label>
                <p className="text-gray-900">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                </p>
              </div>
            </div>
          </div>

          {/* Sync Settings */}
          <div className="bg-white rounded-lg shadow mt-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Database className="h-5 w-5 mr-2" />
                Synchronization Settings
              </h3>
            </div>

            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Automatic Sync</h4>
                  <p className="text-sm text-gray-500">
                    Automatically sync new matches every 30 minutes
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isEditing ? formData.sync_enabled : user?.sync_enabled}
                    onChange={(e) => setFormData({ ...formData, sync_enabled: e.target.checked })}
                    disabled={!isEditing}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Sync
                </label>
                <p className="text-gray-900">
                  {user?.last_sync
                    ? new Date(user.last_sync).toLocaleString()
                    : 'Never synced'
                  }
                </p>
              </div>

              <div className="p-4 bg-blue-50 rounded-md">
                <div className="flex">
                  <Shield className="h-5 w-5 text-blue-400 mr-2" />
                  <div>
                    <h5 className="text-sm font-medium text-blue-800">Privacy Notice</h5>
                    <p className="text-sm text-blue-700 mt-1">
                      We only access publicly available match data and Steam profile information.
                      Your private data remains private.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Account Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Account Statistics</h3>

            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Matches Analyzed</span>
                <span className="text-sm font-medium text-gray-900">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Players Encountered</span>
                <span className="text-sm font-medium text-gray-900">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Suspicious Players Found</span>
                <span className="text-sm font-medium text-gray-900">0</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>

            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors">
                Sync Now
              </button>
              <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors">
                Export Data
              </button>
              <button className="w-full px-4 py-2 border border-red-300 text-red-700 rounded-md hover:bg-red-50 transition-colors">
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings