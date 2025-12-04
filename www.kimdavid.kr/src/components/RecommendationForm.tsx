import { useState, useEffect } from 'react'
import type { Preference, InterestDetail } from '../types'
import { weatherApi } from '../services/weatherApi'
import './RecommendationForm.css'

interface RecommendationFormProps {
  onSubmit: (preference: Preference) => void
  isLoading: boolean
}

const BUDGET_OPTIONS = ['저렴', '보통', '비쌈']
const INTEREST_OPTIONS = [
  '카페', '맛집', '전시회', '영화', '산책', '쇼핑', '문화', '야외활동', '실내활동'
]

// 관심사별 세부 옵션 정의
const INTEREST_DETAILS: Record<string, string[]> = {
  '카페': ['뷰가 예쁜', '분위기가 좋은', '디저트가 맛있는'],
  '맛집': ['한식', '중식', '일식', '양식'],
  '전시회': ['미술', '사진', '조각', '현대미술'],
  '영화': ['로맨스', '액션', '코미디', '스릴러', '드라마', 'SF'],
  '산책': ['공원', '한강', '산', '해변', '도심'],
  '쇼핑': ['패션', '뷰티', '라이프스타일', '기념품'],
  '문화': ['공연', '뮤지컬', '연극', '콘서트'],
  '야외활동': ['등산', '자전거', '피크닉', '캠핑'],
  '실내활동': ['보드게임', '방탈출', '볼링', '당구']
}

// 오늘 날짜를 YYYY-MM-DD 형식으로 반환
const getTodayDate = (): string => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function RecommendationForm({ onSubmit, isLoading }: RecommendationFormProps) {
  const [formData, setFormData] = useState<Preference>({
    budget: '보통',
    location: '',
    interests: [],
    interestDetails: [],
    date: getTodayDate(),
    time_of_day: '오후',
    weather: '',
  })
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [selectedInterestDetails, setSelectedInterestDetails] = useState<Record<string, string[]>>({})

  // 날짜나 위치가 변경되면 날씨 자동 조회
  useEffect(() => {
    const fetchWeather = async () => {
      if (formData.location.trim() && formData.date) {
        setWeatherLoading(true)
        try {
          // 기상청 API가 설정되어 있으면 실제 API 호출, 없으면 간단한 예측
          const weather = import.meta.env.VITE_WEATHER_API_KEY
            ? await weatherApi.getWeather(formData.location, formData.date)
            : weatherApi.getSimpleWeather(formData.date)
          
          setFormData(prev => ({ ...prev, weather }))
        } catch (error) {
          console.error('날씨 조회 실패:', error)
          // 실패 시 기본값
          setFormData(prev => ({ ...prev, weather: '맑음' }))
        } finally {
          setWeatherLoading(false)
        }
      }
    }

    fetchWeather()
  }, [formData.date, formData.location])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.location.trim() && formData.interests.length > 0 && formData.date && formData.time_of_day) {
      onSubmit(formData)
    }
  }

  const toggleInterest = (interest: string) => {
    const isSelected = formData.interests.includes(interest)
    
    if (isSelected) {
      // 관심사 제거 시 세부 옵션도 제거
      const newDetails = { ...selectedInterestDetails }
      delete newDetails[interest]
      setSelectedInterestDetails(newDetails)
      
      setFormData(prev => ({
        ...prev,
        interests: prev.interests.filter(i => i !== interest),
        interestDetails: prev.interestDetails?.filter(d => d.interest !== interest) || []
      }))
    } else {
      // 관심사 추가
      setFormData(prev => ({
        ...prev,
        interests: [...prev.interests, interest]
      }))
    }
  }

  const toggleInterestDetail = (interest: string, detail: string) => {
    const currentDetails = selectedInterestDetails[interest] || []
    const isSelected = currentDetails.includes(detail)
    
    const newDetails = {
      ...selectedInterestDetails,
      [interest]: isSelected
        ? currentDetails.filter(d => d !== detail)
        : [...currentDetails, detail]
    }
    
    setSelectedInterestDetails(newDetails)
    
    // formData의 interestDetails 업데이트
    setFormData(prev => {
      const existingDetails = prev.interestDetails || []
      const otherDetails = existingDetails.filter(d => d.interest !== interest)
      const newInterestDetails: InterestDetail = {
        interest,
        details: newDetails[interest]
      }
      
      return {
        ...prev,
        interestDetails: [...otherDetails, newInterestDetails]
      }
    })
  }

  return (
    <form className="recommendation-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <label className="form-label">
          <span className="label-text">📍 위치</span>
          <input
            type="text"
            className="form-input"
            placeholder="예: 서울시 강남구"
            value={formData.location}
            onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            required
          />
        </label>
      </div>

      <div className="form-section">
        <label className="form-label">
          <span className="label-text">💰 예산</span>
          <div className="radio-group">
            {BUDGET_OPTIONS.map(budget => (
              <label key={budget} className="radio-label">
                <input
                  type="radio"
                  name="budget"
                  value={budget}
                  checked={formData.budget === budget}
                  onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
                />
                <span>{budget}</span>
              </label>
            ))}
          </div>
        </label>
      </div>

      <div className="form-section">
        <label className="form-label">
          <span className="label-text">📅 날짜</span>
          <input
            type="date"
            className="form-input"
            min={getTodayDate()}
            value={formData.date}
            onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
            required
          />
        </label>
      </div>

      <div className="form-section">
        <label className="form-label">
          <span className="label-text">🕐 시간대</span>
          <select
            className="form-select"
            value={formData.time_of_day}
            onChange={(e) => setFormData(prev => ({ ...prev, time_of_day: e.target.value }))}
            required
          >
            <option value="아침">아침</option>
            <option value="점심">점심</option>
            <option value="오후">오후</option>
            <option value="저녁">저녁</option>
            <option value="밤">밤</option>
          </select>
        </label>
      </div>

      <div className="form-section">
        <label className="form-label">
          <span className="label-text">🌤️ 날씨</span>
          <div className="weather-display">
            {weatherLoading ? (
              <span className="weather-loading">날씨 정보 조회 중...</span>
            ) : (
              <span className="weather-value">{formData.weather || '날씨 정보 없음'}</span>
            )}
          </div>
        </label>
      </div>

      <div className="form-section">
        <label className="form-label">
          <span className="label-text">🎯 관심사 (복수 선택 가능)</span>
          <div className="interest-grid">
            {INTEREST_OPTIONS.map(interest => (
              <div key={interest} className="interest-item">
                <button
                  type="button"
                  className={`interest-chip ${formData.interests.includes(interest) ? 'active' : ''}`}
                  onClick={() => toggleInterest(interest)}
                >
                  {interest}
                </button>
                {formData.interests.includes(interest) && INTEREST_DETAILS[interest] && (
                  <div className="interest-details">
                    {INTEREST_DETAILS[interest].map(detail => (
                      <button
                        key={detail}
                        type="button"
                        className={`interest-detail-chip ${
                          selectedInterestDetails[interest]?.includes(detail) ? 'active' : ''
                        }`}
                        onClick={() => toggleInterestDetail(interest, detail)}
                      >
                        {detail}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </label>
      </div>


      <button
        type="submit"
        className="submit-button"
        disabled={isLoading || !formData.location.trim() || formData.interests.length === 0 || !formData.date || !formData.time_of_day || weatherLoading}
      >
        {isLoading ? '추천 중...' : '💕 데이트코스 추천받기'}
      </button>
    </form>
  )
}

export default RecommendationForm

