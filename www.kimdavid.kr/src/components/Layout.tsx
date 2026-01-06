import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()

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

