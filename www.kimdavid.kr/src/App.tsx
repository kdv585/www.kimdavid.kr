import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import AuthCallback from './pages/AuthCallback'
import { useThemeStore } from './stores/themeStore'
import './App.css'

function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth/kakao/callback" element={<AuthCallback />} />
          <Route path="/auth/naver/callback" element={<AuthCallback />} />
          <Route path="/auth/google/callback" element={<AuthCallback />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App

