import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (steamId: string, token: string, userData: User) => void
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const storedUser = localStorage.getItem('user')

        if (token && storedUser) {
          // Try to refresh user data from server
          try {
            const currentUser = await authAPI.getCurrentUser()
            setUser(currentUser)
            localStorage.setItem('user', JSON.stringify(currentUser))
          } catch (error) {
            // If token is invalid, fall back to stored user data
            console.warn('Failed to refresh user data:', error)
            const parsedUser = JSON.parse(storedUser)
            setUser(parsedUser)
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        // Clear invalid data
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = (_steamId: string, token: string, userData: User) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      setUser(null)
    }
  }

  const refreshUser = async () => {
    try {
      const currentUser = await authAPI.getCurrentUser()
      setUser(currentUser)
      localStorage.setItem('user', JSON.stringify(currentUser))
    } catch (error) {
      console.error('Failed to refresh user data:', error)
      throw error
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}