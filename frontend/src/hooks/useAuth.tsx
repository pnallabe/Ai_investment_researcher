import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { jwtDecode } from 'jwt-decode'
import { authService, AuthResponse, User } from '@services/authService'

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

interface AuthProviderProps {
  children: ReactNode
}

interface JWTPayload {
  sub: string
  exp: number
  email: string
  user_id: string
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Check if token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      // Try JWT decode first
      const decoded = jwtDecode<JWTPayload>(token)
      const currentTime = Date.now() / 1000
      return decoded.exp < currentTime
    } catch {
      // If JWT decode fails, try base64 decode (for simplified tokens)
      try {
        const decoded = JSON.parse(atob(token))
        if (decoded.exp) {
          const expTime = new Date(decoded.exp).getTime() / 1000
          const currentTime = Date.now() / 1000
          return expTime < currentTime
        }
        // If no expiration, assume valid for now
        return false
      } catch {
        return true
      }
    }
  }

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('access_token')
        const storedUser = localStorage.getItem('user')

        if (storedToken && storedUser && !isTokenExpired(storedToken)) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          
          // Set default axios header
          authService.setAuthToken(storedToken)
        } else {
          // Clear invalid/expired data
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!token || isTokenExpired(token)) return

    let expirationTime: number
    
    try {
      // Try JWT decode first
      const decoded = jwtDecode<JWTPayload>(token)
      expirationTime = decoded.exp * 1000
    } catch {
      // Try base64 decode for simplified tokens
      try {
        const decoded = JSON.parse(atob(token))
        if (decoded.exp) {
          expirationTime = new Date(decoded.exp).getTime()
        } else {
          // No expiration info, skip auto-refresh
          return
        }
      } catch {
        return
      }
    }

    const currentTime = Date.now()
    const timeUntilExpiration = expirationTime - currentTime
    
    // Refresh 5 minutes before expiration
    const refreshTime = Math.max(timeUntilExpiration - 5 * 60 * 1000, 0)

    const refreshTimer = setTimeout(async () => {
      try {
        await refreshToken()
      } catch (error) {
        console.error('Auto-refresh failed:', error)
        logout()
      }
    }, refreshTime)

    return () => clearTimeout(refreshTimer)
  }, [token])

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true)
      const response: AuthResponse = await authService.login(email, password)
      
      const { access_token, user: userData } = response
      
      // Store in state
      setToken(access_token)
      setUser(userData)
      
      // Store in localStorage
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Set axios default header
      authService.setAuthToken(access_token)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = (): void => {
    // Clear state
    setUser(null)
    setToken(null)
    
    // Clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    
    // Clear axios header
    authService.clearAuthToken()
  }

  const refreshToken = async (): Promise<void> => {
    try {
      const response = await authService.refreshToken()
      const { access_token, user: userData } = response
      
      // Update state
      setToken(access_token)
      setUser(userData)
      
      // Update localStorage
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Update axios header
      authService.setAuthToken(access_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
      throw error
    }
  }

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token && !isTokenExpired(token || ''),
    loading,
    login,
    logout,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default useAuth