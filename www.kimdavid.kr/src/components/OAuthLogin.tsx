import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { oauthApi } from '../services/api'
import './OAuthLogin.css'

function OAuthLogin() {
  const [isLoading, setIsLoading] = useState<string | null>(null)
  const { login } = useAuthStore()

  const handleOAuthLogin = async (provider: 'kakao' | 'naver' | 'google') => {
    try {
      setIsLoading(provider)
      let authUrl = ''

      switch (provider) {
        case 'kakao':
          authUrl = await oauthApi.getKakaoAuthUrl()
          break
        case 'naver':
          authUrl = await oauthApi.getNaverAuthUrl()
          break
        case 'google':
          authUrl = await oauthApi.getGoogleAuthUrl()
          break
      }

      // OAuth 인증 페이지로 직접 리다이렉트
      window.location.href = authUrl
    } catch (error) {
      console.error(`${provider} 로그인 오류:`, error)
      alert(`${provider} 로그인에 실패했습니다.`)
      setIsLoading(null)
    }
  }

  return (
    <div className="oauth-login">
      <div className="oauth-buttons">
        <button
          className="oauth-button kakao"
          onClick={() => handleOAuthLogin('kakao')}
          disabled={isLoading !== null}
        >
          {isLoading === 'kakao' ? (
            <span className="loading">로그인 중...</span>
          ) : (
            <>
              <span className="oauth-icon">💬</span>
              <span>카카오 로그인</span>
            </>
          )}
        </button>

        <button
          className="oauth-button naver"
          onClick={() => handleOAuthLogin('naver')}
          disabled={isLoading !== null}
        >
          {isLoading === 'naver' ? (
            <span className="loading">로그인 중...</span>
          ) : (
            <>
              <span className="oauth-icon">N</span>
              <span>네이버 로그인</span>
            </>
          )}
        </button>

        <button
          className="oauth-button google"
          onClick={() => handleOAuthLogin('google')}
          disabled={isLoading !== null}
        >
          {isLoading === 'google' ? (
            <span className="loading">로그인 중...</span>
          ) : (
            <>
              <span className="oauth-icon">G</span>
              <span>구글 로그인</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default OAuthLogin

