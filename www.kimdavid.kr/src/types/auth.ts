export interface OAuthUser {
  id: string
  email: string
  name?: string
  nickname?: string
  provider: 'kakao' | 'naver' | 'google'
  profileImage?: string
}

export interface OAuthResponse {
  user: OAuthUser
  token: string
  message: string
}

export interface AuthState {
  user: OAuthUser | null
  token: string | null
  isAuthenticated: boolean
  login: (user: OAuthUser, token: string) => void
  logout: () => void
}

