import axios from 'axios'
import type { RecommendDateCourseRequest, RecommendDateCourseResponse } from '../types'
import type { OAuthResponse } from '../types/auth'

// Render 배포 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://date-course-ai-server.onrender.com'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터: 토큰 자동 추가
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 응답 인터셉터: 401 에러 시 로그아웃
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export const dateCourseApi = {
  recommend: async (request: RecommendDateCourseRequest): Promise<RecommendDateCourseResponse> => {
    const response = await apiClient.post<RecommendDateCourseResponse>(
      '/api/v1/date-courses/recommend',
      request
    )
    return response.data
  },
}

// 문화 데이터 API
export const cultureApi = {
  getMovies: async (location: string, date: string) => {
    const response = await apiClient.get('/api/v1/culture/movies', {
      params: { location, date },
    })
    return response.data.movies || []
  },
  getExhibitions: async (location: string, date: string) => {
    const response = await apiClient.get('/api/v1/culture/exhibitions', {
      params: { location, date },
    })
    return response.data.exhibitions || []
  },
  getPerformances: async (location: string, date: string, genre?: string) => {
    const response = await apiClient.get('/api/v1/culture/performances', {
      params: { location, date, genre },
    })
    return response.data.performances || []
  },
}

export const oauthApi = {
  getKakaoAuthUrl: async (): Promise<string> => {
    const response = await apiClient.get<{ authUrl: string }>('/api/auth/kakao')
    return response.data.authUrl
  },
  getNaverAuthUrl: async (): Promise<string> => {
    const response = await apiClient.get<{ authUrl: string }>('/api/auth/naver')
    return response.data.authUrl
  },
  getGoogleAuthUrl: async (): Promise<string> => {
    const response = await apiClient.get<{ authUrl: string }>('/api/auth/google')
    return response.data.authUrl
  },
  handleCallback: async (provider: 'kakao' | 'naver' | 'google', code: string): Promise<OAuthResponse> => {
    const response = await apiClient.get<OAuthResponse>(
      `/api/auth/${provider}/callback`,
      { params: { code } }
    )
    return response.data
  },
}

export default apiClient

