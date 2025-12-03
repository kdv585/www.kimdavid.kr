import axios from 'axios'

// 기상청 공공데이터 API (단기예보 조회서비스)
// 실제 사용 시 공공데이터포털에서 발급받은 API 키가 필요합니다
const WEATHER_API_KEY = import.meta.env.VITE_WEATHER_API_KEY || ''
const WEATHER_API_BASE = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0'

interface WeatherResponse {
  response: {
    body: {
      items: {
        item: Array<{
          category: string
          fcstValue: string
          fcstDate: string
          fcstTime: string
        }>
      }
    }
  }
}

// 지역 코드 매핑 (예시: 서울시 강남구 -> 1168010100)
const getRegionCode = (location: string): string => {
  // 간단한 매핑 (실제로는 더 정확한 지역 코드 매핑이 필요)
  if (location.includes('서울')) {
    if (location.includes('강남')) return '1168010100'
    if (location.includes('강동')) return '1174010100'
    if (location.includes('강북')) return '1130510100'
    if (location.includes('강서')) return '1150010100'
    return '1168010100' // 기본값: 강남구
  }
  // 다른 지역도 추가 가능
  return '1168010100' // 기본값
}

// 날씨 상태 변환
const convertWeatherCode = (pty: string, sky: string): string => {
  // pty: 강수형태 (0: 없음, 1: 비, 2: 비/눈, 3: 눈, 4: 소나기)
  // sky: 하늘상태 (1: 맑음, 3: 구름많음, 4: 흐림)
  
  if (pty === '1' || pty === '4') return '비'
  if (pty === '2') return '비/눈'
  if (pty === '3') return '눈'
  if (sky === '1') return '맑음'
  if (sky === '3') return '구름많음'
  if (sky === '4') return '흐림'
  return '맑음' // 기본값
}

export const weatherApi = {
  getWeather: async (location: string, date: string): Promise<string> => {
    try {
      // API 키가 없으면 기본값 반환
      if (!WEATHER_API_KEY) {
        console.warn('기상청 API 키가 설정되지 않았습니다. 기본 날씨를 반환합니다.')
        return '맑음'
      }

      const regionCode = getRegionCode(location)
      const baseDate = date.replace(/-/g, '') // YYYYMMDD 형식
      const baseTime = '0500' // 05시 기준 (단기예보)

      const response = await axios.get<WeatherResponse>(
        `${WEATHER_API_BASE}/getVilageFcst`,
        {
          params: {
            serviceKey: WEATHER_API_KEY,
            pageNo: 1,
            numOfRows: 10,
            dataType: 'JSON',
            base_date: baseDate,
            base_time: baseTime,
            nx: regionCode.substring(0, 3),
            ny: regionCode.substring(3, 6),
          },
        }
      )

      const items = response.data.response.body.items.item
      const weatherItem = items.find(item => 
        item.category === 'PTY' || item.category === 'SKY'
      )

      if (weatherItem) {
        const ptyItem = items.find(item => item.category === 'PTY')
        const skyItem = items.find(item => item.category === 'SKY')
        return convertWeatherCode(
          ptyItem?.fcstValue || '0',
          skyItem?.fcstValue || '1'
        )
      }

      return '맑음' // 기본값
    } catch (error) {
      console.error('날씨 정보 조회 실패:', error)
      // 에러 발생 시 기본값 반환
      return '맑음'
    }
  },

  // 간단한 날씨 예측 (API 없이 날짜 기반)
  getSimpleWeather: (date: string): string => {
    const selectedDate = new Date(date)
    const today = new Date()
    const diffDays = Math.floor((selectedDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

    // 간단한 로직: 오늘부터 3일 후까지는 맑음, 그 이후는 랜덤
    if (diffDays < 0) {
      return '맑음' // 과거 날짜
    } else if (diffDays <= 3) {
      return '맑음' // 가까운 미래
    } else {
      // 먼 미래는 랜덤 (실제로는 API에서 가져와야 함)
      const weathers = ['맑음', '구름많음', '흐림']
      return weathers[Math.floor(Math.random() * weathers.length)]
    }
  },
}

