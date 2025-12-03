import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { oauthApi } from '../services/api'
import './AuthCallback.css'

function AuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('로그인 처리 중...')

  useEffect(() => {
    const code = searchParams.get('code')
    const provider = window.location.pathname.includes('kakao') 
      ? 'kakao' 
      : window.location.pathname.includes('naver')
      ? 'naver'
      : 'google'

    if (!code) {
      setStatus('error')
      setMessage('인증 코드를 받지 못했습니다.')
      return
    }

    const handleAuth = async () => {
      try {
        const response = await oauthApi.handleCallback(provider, code)
        login(response.user, response.token)
        setStatus('success')
        setMessage(`${response.user.provider} 로그인 성공!`)
        
        // 2초 후 메인 페이지로 이동
        setTimeout(() => {
          navigate('/')
        }, 2000)
      } catch (error) {
        console.error('인증 오류:', error)
        setStatus('error')
        setMessage('로그인 처리 중 오류가 발생했습니다.')
      }
    }

    handleAuth()
  }, [searchParams, login, navigate])

  return (
    <div className="auth-callback">
      <div className="callback-content">
        {status === 'loading' && (
          <>
            <div className="spinner"></div>
            <p>{message}</p>
          </>
        )}
        {status === 'success' && (
          <>
            <div className="success-icon">✅</div>
            <p>{message}</p>
            <p className="redirect-message">잠시 후 메인 페이지로 이동합니다...</p>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="error-icon">❌</div>
            <p>{message}</p>
            <button onClick={() => navigate('/')} className="back-button">
              메인으로 돌아가기
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default AuthCallback

