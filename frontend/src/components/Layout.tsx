import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Home,
  Users,
  Target,
  Settings,
  LogOut,
  Shield,
  Activity
} from 'lucide-react'
import { clsx } from 'clsx'

const Layout: React.FC = () => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Players', href: '/players', icon: Users },
    { name: 'Matches', href: '/matches', icon: Target },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center px-6 py-4 border-b">
            <Shield className="h-8 w-8 text-primary-600 mr-3" />
            <span className="text-xl font-bold text-gray-900">CS StatSentry</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              const Icon = item.icon

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User Profile */}
          <div className="border-t px-4 py-4">
            <div className="flex items-center mb-3">
              {user?.avatar_url ? (
                <img
                  className="h-10 w-10 rounded-full"
                  src={user.avatar_url}
                  alt={user.steam_name || 'User avatar'}
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <Users className="h-5 w-5 text-gray-600" />
                </div>
              )}
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  {user?.steam_name || 'Unknown User'}
                </p>
                <p className="text-xs text-gray-500">Steam ID: {user?.steam_id}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-lg transition-colors"
            >
              <LogOut className="h-4 w-4 mr-3" />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout