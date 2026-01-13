import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import { oauthApi } from '../services/api'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [isLoginMenuOpen, setIsLoginMenuOpen] = useState(false)

  const handleLogin = async (provider: 'kakao' | 'naver' | 'google') => {
    try {
      setIsLoginMenuOpen(false)
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
      
      if (!authUrl) {
        throw new Error('인증 URL을 받지 못했습니다.')
      }
      
      window.location.href = authUrl
    } catch (error: any) {
      console.error(`${provider} 로그인 오류:`, error)
      
      // 더 자세한 에러 메시지
      let errorMessage = `${provider} 로그인에 실패했습니다.`
      
      if (error.response) {
        // API 서버에서 에러 응답
        errorMessage = `서버 오류: ${error.response.status} - ${error.response.data?.error || error.response.data?.message || '알 수 없는 오류'}`
      } else if (error.request) {
        // 요청은 보냈지만 응답이 없음 (API 서버가 실행되지 않았거나 접근 불가)
        errorMessage = 'API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.'
      } else {
        // 요청 설정 중 오류
        errorMessage = error.message || errorMessage
      }
      
      alert(errorMessage)
    }
  }

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <Link to="/" className="logo-link">
                <h1 className="logo">데이트코스 짜기</h1>
                <p className="tagline">AI가 추천하는 완벽한 데이트 코스</p>
              </Link>
            </div>
            <nav className="header-nav">
              <Link
                to="/"
                className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
              >
                데이트코스
              </Link>
              <Link
                to="/rag"
                className={`nav-link ${location.pathname === '/rag' ? 'active' : ''}`}
              >
                RAG 챗봇
              </Link>
            </nav>
            <div className="header-right">
            <div className="login-wrapper">
              <button
                className="login-button"
                onClick={() => setIsLoginMenuOpen((prev) => !prev)}
              >
                로그인/회원가입
              </button>
              {isLoginMenuOpen && (
                <div className="login-menu">
                  <button onClick={() => handleLogin('kakao')}>카카오 로그인</button>
                  <button onClick={() => handleLogin('naver')}>네이버 로그인</button>
                  <button onClick={() => handleLogin('google')}>구글 로그인</button>
                  <div className="login-hint">SNS 로그인 시 자동 회원가입 처리됩니다.</div>
                </div>
              )}
            </div>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>
      <main className="main">
        <div className="container">
          {children}
        </div>
      </main>
      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 David.kr. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout

