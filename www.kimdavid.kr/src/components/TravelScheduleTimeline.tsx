import { DateCourse, Preference } from '../types'
import './TravelScheduleTimeline.css'

interface TravelScheduleTimelineProps {
  courses: DateCourse[]
  preference: Preference
}

function TravelScheduleTimeline({ courses, preference }: TravelScheduleTimelineProps) {
  // 날짜 범위 생성 함수
  const getDateRange = (startDate: string, endDate: string): string[] => {
    if (!startDate || !endDate) return [preference.date]
    const dates: string[] = []
    const start = new Date(startDate)
    const end = new Date(endDate)
    
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      dates.push(new Date(d).toISOString().split('T')[0])
    }
    return dates
  }

  // 날짜 포맷팅 함수
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const weekdays = ['일', '월', '화', '수', '목', '금', '토']
    const weekday = weekdays[date.getDay()]
    return `${month}월 ${day}일 (${weekday})`
  }

  // 시간대 목록 (아침부터 밤까지)
  const timeSlots = ['아침', '점심', '오후', '저녁', '밤']

  // 출발/도착 날짜 가져오기
  const getTravelDates = (): { startDate: string; endDate: string } => {
    if (preference.travelStartDate && preference.travelEndDate) {
      return {
        startDate: preference.travelStartDate,
        endDate: preference.travelEndDate
      }
    }
    // 출발/도착 날짜가 없으면 단일 날짜 사용
    return {
      startDate: preference.date,
      endDate: preference.date
    }
  }

  // 날짜 기반 시드 생성 함수
  const getDateSeed = (dateString: string): number => {
    let hash = 0
    for (let i = 0; i < dateString.length; i++) {
      const char = dateString.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32bit integer
    }
    return Math.abs(hash)
  }

  // 날짜별로 코스 그룹화 (각 날짜마다 다른 코스 조합, 중복 최소화)
  const groupCoursesByDate = (courses: DateCourse[], dates: string[]): Record<string, DateCourse[]> => {
    const grouped: Record<string, DateCourse[]> = {}
    dates.forEach(date => {
      grouped[date] = []
    })
    
    if (courses.length === 0) {
      return grouped
    }
    
    // 각 날짜에 시간대 수만큼 코스 배치
    const coursesPerDay = timeSlots.length
    
    dates.forEach((date, dateIndex) => {
      // 각 날짜마다 다른 코스 조합을 만들기 위해 날짜를 시드로 사용
      const dateSeed = getDateSeed(date)
      
      // 날짜별로 다른 시작 인덱스와 스텝 사용
      const startOffset = dateSeed % courses.length
      const step = Math.max(1, Math.floor(courses.length / coursesPerDay) || 1)
      
      // 각 날짜마다 다른 코스 선택
      const selectedCourses: DateCourse[] = []
      const usedInDay = new Set<number>()
      
      for (let i = 0; i < coursesPerDay; i++) {
        // 각 날짜마다 다른 패턴으로 코스 선택
        let courseIndex = (startOffset + (i * step) + (dateIndex * 3) + (i * 2)) % courses.length
        
        // 같은 날짜 내에서 중복 방지
        let attempts = 0
        while (usedInDay.has(courseIndex) && attempts < courses.length) {
          courseIndex = (courseIndex + 1) % courses.length
          attempts++
        }
        
        usedInDay.add(courseIndex)
        selectedCourses.push(courses[courseIndex])
      }
      
      grouped[date] = selectedCourses
    })
    
    return grouped
  }

  // 시간대별로 코스 분배 (각 시간대에 최소 1개씩 배치)
  const distributeCoursesByTimeSlot = (courses: DateCourse[]): Record<string, DateCourse[]> => {
    const distributed: Record<string, DateCourse[]> = {}
    timeSlots.forEach(slot => {
      distributed[slot] = []
    })
    
    if (courses.length === 0) {
      return distributed
    }
    
    // 각 시간대에 최소 1개씩 배치
    timeSlots.forEach((slot, slotIndex) => {
      if (courses.length > slotIndex) {
        distributed[slot].push(courses[slotIndex])
      }
    })
    
    // 남은 코스를 시간대별로 순환 배치
    for (let i = timeSlots.length; i < courses.length; i++) {
      const slotIndex = i % timeSlots.length
      const slot = timeSlots[slotIndex]
      distributed[slot].push(courses[i])
    }
    
    return distributed
  }

  const { startDate, endDate } = getTravelDates()
  const dates = getDateRange(startDate, endDate)
  const coursesByDate = groupCoursesByDate(courses, dates)

  return (
    <div className="travel-schedule-timeline">
      <h3 className="timeline-title">
        ✈️ 여행 일정 계획표
      </h3>
      <div className="schedule-days">
        {dates.map((date) => {
          const dayCourses = coursesByDate[date] || []
          const coursesByTime = distributeCoursesByTimeSlot(dayCourses)
          
          return (
            <div key={date} className="schedule-day-card">
              <div className="day-header">
                <span className="day-date">{formatDate(date)}</span>
                <span className="day-location">📍 {preference.location}</span>
              </div>
              <div className="day-schedule">
                {timeSlots.map((timeSlot) => {
                  const slotCourses = coursesByTime[timeSlot] || []
                  
                  return (
                    <div key={timeSlot} className="time-slot">
                      <div className="time-slot-label">
                        <span className="time-icon">
                          {timeSlot === '아침' && '🌅'}
                          {timeSlot === '점심' && '☀️'}
                          {timeSlot === '오후' && '🌤️'}
                          {timeSlot === '저녁' && '🌙'}
                          {timeSlot === '밤' && '🌃'}
                        </span>
                        <span className="time-text">{timeSlot}</span>
                      </div>
                      <div className="time-slot-content">
                        {slotCourses.length > 0 ? (
                          slotCourses.map((course, index) => (
                            <div key={course.id || index} className="schedule-item">
                              <div className="schedule-item-title">{course.title}</div>
                              <div className="schedule-item-description">{course.description}</div>
                              <div className="schedule-item-meta">
                                <span className="schedule-item-duration">⏱️ {Math.floor(course.duration / 60)}시간</span>
                                <span className="schedule-item-price">💰 {course.price_range}</span>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="schedule-item-empty">
                            {timeSlot} 일정을 입력하세요
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TravelScheduleTimeline

