import { useState } from 'react'
import RecommendationForm from '../components/RecommendationForm'
import DateCourseCard from '../components/DateCourseCard'
import TravelScheduleTimeline from '../components/TravelScheduleTimeline'
import { dateCourseApi } from '../services/api'
import type { Preference, DateCourse } from '../types'
import './HomePage.css'

function HomePage() {
  const [courses, setCourses] = useState<DateCourse[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPreference, setCurrentPreference] = useState<Preference | null>(null)

  const handleRecommend = async (preference: Preference) => {
    setIsLoading(true)
    setError(null)
    setCourses([])
    setCurrentPreference(preference)

    try {
      const response = await dateCourseApi.recommend({ preference })
      setCourses(response.courses)
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이트코스 추천에 실패했습니다.')
      console.error('Recommendation error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // 여행이 선택되었는지 확인
  const isTravelSelected = currentPreference?.interests.includes('여행') || false

  return (
    <div className="home-page">
      <div className="page-header">
        <h2>나만의 데이트코스 찾기</h2>
        <p>원하는 조건을 입력하고 AI가 추천하는 완벽한 데이트 코스를 만나보세요!</p>
      </div>

      <RecommendationForm onSubmit={handleRecommend} isLoading={isLoading} />

      {error && (
        <div className="error-message">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {courses.length > 0 && (
        <div className="results-section">
          {isTravelSelected ? (
            <TravelScheduleTimeline courses={courses} preference={currentPreference!} />
          ) : (
            <>
              <h3 className="results-title">
                추천된 데이트코스 <span className="results-count">({courses.length}개)</span>
              </h3>
              <div className="courses-grid">
                {courses.map((course, index) => (
                  <DateCourseCard key={course.id || index} course={course} />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI가 최적의 데이트코스를 찾고 있어요...</p>
        </div>
      )}
    </div>
  )
}

export default HomePage

