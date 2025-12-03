import { ReactNode } from 'react'
import { useAuthStore } from '../stores/authStore'
import OAuthLogin from './OAuthLogin'
import UserProfile from './UserProfile'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <h1 className="logo">💕 데이트코스 추천</h1>
              <p className="tagline">AI가 추천하는 완벽한 데이트 코스</p>
            </div>
            <div className="header-right">
              {isAuthenticated ? <UserProfile /> : <OAuthLogin />}
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

