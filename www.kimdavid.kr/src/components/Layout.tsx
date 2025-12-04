import { ReactNode } from 'react'
import ThemeToggle from './ThemeToggle'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <h1 className="logo">이연수 데이트코스 짜주기</h1>
              <p className="tagline">AI가 추천하는 완벽한 데이트 코스</p>
            </div>
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

