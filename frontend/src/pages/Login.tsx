import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../services/api'
import { Shield, LogIn } from 'lucide-react'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, login } = useAuth()

  useEffect(() => {
    // If user is already logged in, redirect to dashboard
    if (user) {
      navigate('/')
      return
    }

    // Handle Steam OAuth callback
    const handleCallback = async () => {
      const openidMode = searchParams.get('openid.mode')

      if (openidMode === 'id_res') {
        try {
          // Extract all OpenID parameters
          const authResponse = await authAPI.handleSteamCallback(searchParams)

          // Store auth data and redirect
          login(authResponse.steam_id, authResponse.access_token, {
            user_id: 0, // Will be updated by auth context
            steam_id: authResponse.steam_id,
            steam_name: authResponse.steam_name,
            avatar_url: authResponse.avatar_url,
            last_sync: null,
            sync_enabled: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })

          navigate('/')
        } catch (error) {
          console.error('Steam authentication failed:', error)
          // Show error message to user
        }
      }
    }

    handleCallback()
  }, [searchParams, user, navigate, login])

  const handleSteamLogin = async () => {
    try {
      const { auth_url } = await authAPI.getSteamLoginUrl()
      window.location.href = auth_url
    } catch (error) {
      console.error('Failed to initiate Steam login:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="flex justify-center items-center mb-4">
            <Shield className="h-16 w-16 text-primary-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">StatSentry</h1>
          <p className="text-gray-600 text-lg">
            CS2 Anti-Cheat Detection System
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Welcome Back
            </h2>
            <p className="text-gray-600">
              Sign in with your Steam account to analyze your CS2 teammates
            </p>
          </div>

          <button
            onClick={handleSteamLogin}
            className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm bg-gray-900 text-white font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
          >
            <LogIn className="h-5 w-5 mr-3" />
            Sign in through Steam
          </button>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              We only access public Steam profile information
            </p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <div className="grid grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <Shield className="h-6 w-6 mx-auto mb-2 text-primary-600" />
              <span>Secure OAuth</span>
            </div>
            <div>
              <div className="h-6 w-6 mx-auto mb-2 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">CS2</span>
              </div>
              <span>CS2 Analysis</span>
            </div>
            <div>
              <div className="h-6 w-6 mx-auto mb-2 bg-danger-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">!</span>
              </div>
              <span>Cheat Detection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login