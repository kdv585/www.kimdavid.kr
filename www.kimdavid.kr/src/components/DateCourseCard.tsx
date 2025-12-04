import { DateCourse } from '../types'
import './DateCourseCard.css'

interface DateCourseCardProps {
  course: DateCourse
}

function DateCourseCard({ course }: DateCourseCardProps) {
  const getPriceRangeColor = (range: string) => {
    switch (range) {
      case '저렴':
        return 'price-cheap'
      case '보통':
        return 'price-normal'
      case '비쌈':
        return 'price-expensive'
      default:
        return ''
    }
  }

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0 && mins > 0) {
      return `${hours}시간 ${mins}분`
    } else if (hours > 0) {
      return `${hours}시간`
    }
    return `${mins}분`
  }

  return (
    <div className="date-course-card">
      <div className="card-location-highlight">
        <span className="location-icon">📍</span>
        <span className="location-text">{course.location}</span>
      </div>
      
      <div className="card-header">
        <h3 className="card-title">{course.title}</h3>
        <div className="card-rating">
          <span className="star">⭐</span>
          <span>{course.rating.toFixed(1)}</span>
        </div>
      </div>
      
      <p className="card-description">{course.description}</p>
      
      <div className="card-info">
        <div className="info-item">
          <span className="info-label">⏱️ 소요시간</span>
          <span className="info-value">{formatDuration(course.duration)}</span>
        </div>
        <div className="info-item">
          <span className="info-label">💰 가격대</span>
          <span className={`info-value ${getPriceRangeColor(course.price_range)}`}>
            {course.price_range}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">🏷️ 카테고리</span>
          <span className="info-value">{course.category}</span>
        </div>
      </div>
      
      <div className="card-tags">
        {course.tags.map((tag, index) => (
          <span key={index} className="tag">
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}

export default DateCourseCard

