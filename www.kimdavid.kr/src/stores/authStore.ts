import { create } from 'zustand'
import type { AuthState, OAuthUser } from '../types/auth'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

// localStorage에서 초기 상태 로드
const loadInitialState = () => {
  if (typeof window === 'undefined') {
    return { user: null, token: null, isAuthenticated: false }
  }

  const token = localStorage.getItem(TOKEN_KEY)
  const userStr = localStorage.getItem(USER_KEY)

  if (token && userStr) {
    try {
      const user = JSON.parse(userStr) as OAuthUser
      return { user, token, isAuthenticated: true }
    } catch (error) {
      console.error('Failed to parse user from localStorage:', error)
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }

  return { user: null, token: null, isAuthenticated: false }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...loadInitialState(),
  login: (user: OAuthUser, token: string) => {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    set({ user, token, isAuthenticated: true })
  },
  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    set({ user: null, token: null, isAuthenticated: false })
  },
}))

