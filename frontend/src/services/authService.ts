import axios, { AxiosInstance, AxiosResponse } from 'axios'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Types
export interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  username: string
  first_name?: string
  last_name?: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

class AuthService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor to handle token expiration
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
              const response = await this.refreshToken()
              const { access_token } = response
              
              localStorage.setItem('access_token', access_token)
              originalRequest.headers.Authorization = `Bearer ${access_token}`
              
              return this.api(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.clearAuthToken()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Set authentication token
  setAuthToken(token: string): void {
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  // Clear authentication token
  clearAuthToken(): void {
    delete this.api.defaults.headers.common['Authorization']
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // Login
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response: AxiosResponse<AuthResponse> = await this.api.post('/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      return response.data
    } catch (error) {
      console.error('Login error:', error)
      throw this.handleError(error)
    }
  }

  // Register
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await this.api.post('/v1/auth/register', userData)
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      throw this.handleError(error)
    }
  }

  // Refresh token
  async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response: AxiosResponse<AuthResponse> = await this.api.post('/v1/auth/refresh', {
        refresh_token: refreshToken,
      })

      return response.data
    } catch (error) {
      console.error('Token refresh error:', error)
      throw this.handleError(error)
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      await this.api.post('/v1/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.clearAuthToken()
    }
  }

  // Get current user profile
  async getProfile(): Promise<User> {
    try {
      const response: AxiosResponse<User> = await this.api.get('/v1/auth/me')
      return response.data
    } catch (error) {
      console.error('Get profile error:', error)
      throw this.handleError(error)
    }
  }

  // Update user profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    try {
      const response: AxiosResponse<User> = await this.api.put('/v1/auth/me', userData)
      return response.data
    } catch (error) {
      console.error('Update profile error:', error)
      throw this.handleError(error)
    }
  }

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      await this.api.post('/v1/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
    } catch (error) {
      console.error('Change password error:', error)
      throw this.handleError(error)
    }
  }

  // Reset password request
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await this.api.post('/v1/auth/password-reset-request', { email })
    } catch (error) {
      console.error('Password reset request error:', error)
      throw this.handleError(error)
    }
  }

  // Reset password confirm
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    try {
      await this.api.post('/v1/auth/password-reset-confirm', {
        token,
        new_password: newPassword,
      })
    } catch (error) {
      console.error('Password reset confirm error:', error)
      throw this.handleError(error)
    }
  }

  // Verify email
  async verifyEmail(token: string): Promise<void> {
    try {
      await this.api.post('/v1/auth/verify-email', { token })
    } catch (error) {
      console.error('Email verification error:', error)
      throw this.handleError(error)
    }
  }

  // Resend verification email
  async resendVerificationEmail(): Promise<void> {
    try {
      await this.api.post('/v1/auth/resend-verification')
    } catch (error) {
      console.error('Resend verification error:', error)
      throw this.handleError(error)
    }
  }

  // Error handler
  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
      return new Error(message)
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network error: Please check your connection')
    } else {
      // Something else happened
      return new Error(error.message || 'An unexpected error occurred')
    }
  }
}

// Create and export a single instance
export const authService = new AuthService()
export default authService