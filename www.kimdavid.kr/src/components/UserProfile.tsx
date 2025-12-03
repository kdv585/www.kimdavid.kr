import { useAuthStore } from '../stores/authStore'
import './UserProfile.css'

function UserProfile() {
  const { user, logout } = useAuthStore()

  if (!user) {
    return null
  }

  const getProviderName = (provider: string) => {
    switch (provider) {
      case 'kakao':
        return '카카오'
      case 'naver':
        return '네이버'
      case 'google':
        return '구글'
      default:
        return provider
    }
  }

  return (
    <div className="user-profile">
      <div className="user-info">
        {user.profileImage && (
          <img src={user.profileImage} alt={user.name || user.nickname} className="user-avatar" />
        )}
        <div className="user-details">
          <div className="user-name">{user.name || user.nickname || user.email}</div>
          <div className="user-provider">{getProviderName(user.provider)}로 로그인</div>
        </div>
      </div>
      <button className="logout-button" onClick={logout}>
        로그아웃
      </button>
    </div>
  )
}

export default UserProfile

