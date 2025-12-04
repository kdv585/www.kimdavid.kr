import { useEffect } from 'react'
import { useThemeStore, type Theme } from '../stores/themeStore'
import './ThemeToggle.css'

function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const themes: { value: Theme; label: string; emoji: string }[] = [
    { value: 'light', label: '라이트', emoji: '☀️' },
    { value: 'dark', label: '다크', emoji: '🌙' },
    { value: 'kuromi', label: '쿠로미', emoji: '💜' },
    { value: 'hellokitty', label: '헬로키티', emoji: '🎀' },
    { value: 'hangyodong', label: '한교동', emoji: '🐙' },
  ]

  return (
    <div className="theme-toggle">
      {themes.map((t) => (
        <button
          key={t.value}
          className={`theme-button ${theme === t.value ? 'active' : ''}`}
          onClick={() => setTheme(t.value)}
          title={t.label}
        >
          <span className="theme-emoji">{t.emoji}</span>
          <span className="theme-label">{t.label}</span>
        </button>
      ))}
    </div>
  )
}

export default ThemeToggle

