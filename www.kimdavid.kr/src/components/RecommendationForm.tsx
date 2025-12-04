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
  '카페', '맛집', '전시회', '영화', '산책', '쇼핑', '문화', '야외활동', '실내활동', '여행'
]

// 관심사별 세부 옵션 정의
const INTEREST_DETAILS: Record<string, string[]> = {
  '카페': ['뷰가 예쁜', '분위기가 좋은', '디저트가 맛있는'],
  '맛집': ['한식', '중식', '일식', '양식', '태국', '베트남'],
  '전시회': ['미술', '사진', '조각', '현대미술'],
  '영화': ['로맨스', '액션', '코미디', '스릴러', '드라마', 'SF', '느와르', '애니메이션'],
  '산책': ['공원', '한강', '산', '해변', '도심'],
  '쇼핑': ['패션', '뷰티', '라이프스타일', '기념품'],
  '문화': ['공연', '뮤지컬', '연극', '콘서트'],
  '야외활동': ['등산', '자전거', '피크닉', '캠핑'],
  '실내활동': ['보드게임', '방탈출', '볼링', '당구', '노래방', '오락실', '수공예', '연수집'],
  '여행': ['국내', '해외', '일정']
}

// 여행 세부 옵션
const TRAVEL_DOMESTIC_OPTIONS = ['휴양(산)', '휴양(바다)', '관광']
const TRAVEL_ABROAD_OPTIONS = ['휴양', '관광']

// 오늘 날짜를 YYYY-MM-DD 형식으로 반환
const getTodayDate = (): string => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function RecommendationForm({ onSubmit, isLoading }: RecommendationFormProps) {
  // Component for date course recommendation form
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
  const [travelAbroadSelected, setTravelAbroadSelected] = useState<string[]>([])
  const [travelDomesticSelected, setTravelDomesticSelected] = useState<string[]>([])
  const [travelScheduleDates, setTravelScheduleDates] = useState({ startDate: '', endDate: '' })

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
      // 여행이 선택되고 일정이 선택되었을 때 출발/도착 날짜 포함
      const isTravelWithSchedule = formData.interests.includes('여행') &&
        selectedInterestDetails['여행']?.includes('일정') &&
        travelScheduleDates.startDate &&
        travelScheduleDates.endDate

      const submitData = {
        ...formData,
        ...(isTravelWithSchedule && {
          travelStartDate: travelScheduleDates.startDate,
          travelEndDate: travelScheduleDates.endDate
        })
      }

      onSubmit(submitData)
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

    // 여행의 해외/국내 특수 처리
    if (interest === '여행') {
      if (detail === '해외' && isSelected) {
        setTravelAbroadSelected([])
      } else if (detail === '국내' && isSelected) {
        setTravelDomesticSelected([])
      }
    }

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

      // 해외 선택 시 동남아/유럽/아메리카도 포함
      let finalDetails = newDetails[interest]
      if (interest === '여행' && newDetails[interest].includes('해외') && travelAbroadSelected.length > 0) {
        finalDetails = [...newDetails[interest], ...travelAbroadSelected]
      }

      const newInterestDetails: InterestDetail = {
        interest,
        details: finalDetails
      }

      return {
        ...prev,
        interestDetails: [...otherDetails, newInterestDetails]
      }
    })
  }

  const toggleTravelAbroad = (region: string) => {
    const newSelected = travelAbroadSelected.includes(region)
      ? travelAbroadSelected.filter(r => r !== region)
      : [...travelAbroadSelected, region]

    setTravelAbroadSelected(newSelected)

    // formData 업데이트
    setFormData(prev => {
      const existingDetails = prev.interestDetails || []
      const otherDetails = existingDetails.filter(d => d.interest !== '여행')

      const travelBaseDetails = selectedInterestDetails['여행'] || []
      const newTravelDetails: InterestDetail = {
        interest: '여행',
        details: [...travelBaseDetails, ...newSelected]
      }

      return {
        ...prev,
        interestDetails: [...otherDetails, newTravelDetails]
      }
    })
  }

  const toggleTravelDomestic = (option: string) => {
    const newSelected = travelDomesticSelected.includes(option)
      ? travelDomesticSelected.filter(o => o !== option)
      : [...travelDomesticSelected, option]

    setTravelDomesticSelected(newSelected)

    // formData 업데이트
    setFormData(prev => {
      const existingDetails = prev.interestDetails || []
      const otherDetails = existingDetails.filter(d => d.interest !== '여행')

      const travelBaseDetails = selectedInterestDetails['여행'] || []
      const newTravelDetails: InterestDetail = {
        interest: '여행',
        details: [...travelBaseDetails, ...newSelected]
      }

      return {
        ...prev,
        interestDetails: [...otherDetails, newTravelDetails]
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
                        className={`interest-detail-chip ${selectedInterestDetails[interest]?.includes(detail) ? 'active' : ''
                          }`}
                        onClick={() => toggleInterestDetail(interest, detail)}
                      >
                        {detail}
                      </button>
                    ))}
                    {/* 여행의 국내 선택 시 추가 옵션 */}
                    {interest === '여행' && selectedInterestDetails[interest]?.includes('국내') && (
                      <div className="travel-domestic-options">
                        {TRAVEL_DOMESTIC_OPTIONS.map(option => (
                          <button
                            key={option}
                            type="button"
                            className={`interest-detail-chip ${travelDomesticSelected.includes(option) ? 'active' : ''}`}
                            onClick={() => toggleTravelDomestic(option)}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}
                    {/* 여행의 해외 선택 시 추가 옵션 */}
                    {interest === '여행' && selectedInterestDetails[interest]?.includes('해외') && (
                      <div className="travel-abroad-options">
                        {TRAVEL_ABROAD_OPTIONS.map(region => (
                          <button
                            key={region}
                            type="button"
                            className={`interest-detail-chip ${travelAbroadSelected.includes(region) ? 'active' : ''}`}
                            onClick={() => toggleTravelAbroad(region)}
                          >
                            {region}
                          </button>
                        ))}
                      </div>
                    )}
                    {/* 여행의 일정 선택 시 출발/도착 날짜 선택 */}
                    {interest === '여행' && selectedInterestDetails[interest]?.includes('일정') && (
                      <div className="travel-schedule-date">
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
                          <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                              출발 날짜
                            </label>
                            <input
                              type="date"
                              className="form-input"
                              min={getTodayDate()}
                              value={travelScheduleDates.startDate}
                              onChange={(e) => {
                                const startDate = e.target.value
                                setTravelScheduleDates(prev => {
                                  // 도착 날짜가 출발 날짜보다 이전이면 초기화
                                  const newDates = { ...prev, startDate }
                                  if (prev.endDate && prev.endDate < startDate) {
                                    newDates.endDate = ''
                                  }
                                  return newDates
                                })
                              }}
                              style={{ width: '100%' }}
                            />
                          </div>
                          <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                              도착 날짜
                            </label>
                            <input
                              type="date"
                              className="form-input"
                              min={travelScheduleDates.startDate || getTodayDate()}
                              value={travelScheduleDates.endDate}
                              onChange={(e) => setTravelScheduleDates(prev => ({ ...prev, endDate: e.target.value }))}
                              disabled={!travelScheduleDates.startDate}
                              style={{ width: '100%' }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
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

