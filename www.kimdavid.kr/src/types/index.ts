export interface DateCourse {
  id?: string
  title: string
  description: string
  location: string
  category: string
  duration: number
  price_range: string
  tags: string[]
  rating: number
  created_at?: string
  updated_at?: string
}

export interface InterestDetail {
  interest: string
  details: string[]
}

export interface Preference {
  budget: string
  location: string
  interests: string[]
  interestDetails?: InterestDetail[] // 관심사별 세부 옵션
  date: string // YYYY-MM-DD 형식
  time_of_day: string
  weather?: string // 날짜 선택 시 자동으로 설정됨
}

export interface RecommendDateCourseRequest {
  preference: Preference
}

export interface RecommendDateCourseResponse {
  courses: DateCourse[]
  count: number
}

