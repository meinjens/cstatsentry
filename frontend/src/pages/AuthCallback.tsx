import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const AuthCallback = () => {
  const navigate = useNavigate()
  const { login } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Parse URL parameters for token and user data
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token')
        const userData = urlParams.get('user')

        if (token && userData) {
          const user = JSON.parse(decodeURIComponent(userData))
          login(user.steam_id, token, user)
          navigate('/', { replace: true })
        } else {
          // Handle error case - missing parameters
          console.error('Missing authentication parameters')
          navigate('/login?error=auth_failed', { replace: true })
        }
      } catch (error) {
        console.error('Authentication callback error:', error)
        navigate('/login?error=auth_failed', { replace: true })
      }
    }

    handleCallback()
  }, [login, navigate])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Authentifizierung läuft...</p>
      </div>
    </div>
  )
}

export default AuthCallback