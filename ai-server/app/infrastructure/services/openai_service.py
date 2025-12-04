import os
import json
import random
from typing import List, Dict, Any
from datetime import datetime
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference
from app.domain.services.ai_service import AIService


class OpenAIService(AIService):
    """OpenAI 기반 AI 서비스 구현"""

    def __init__(
        self, 
        api_key: str = None, 
        model: str = "gpt-4",
        culture_service = None,
        place_service = None
    ):
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.model = model or os.getenv("AI_MODEL", "gpt-4")
        self.base_url = "https://api.openai.com/v1"
        
        # 지역별 장소 데이터
        self.places_db = self._init_places_database()
        
        # 문화 데이터 서비스 (주입되거나 새로 생성)
        if culture_service is None:
            from app.infrastructure.services.culture_service import CultureService
            self.culture_service = CultureService()
        else:
            self.culture_service = culture_service
        
        # 실제 장소 데이터 서비스 (주입되거나 새로 생성)
        if place_service is None:
            from app.infrastructure.services.place_service import PlaceService
            self.place_service = PlaceService()
        else:
            self.place_service = place_service

    def _should_use_openai(self) -> bool:
        """
        OpenAI API 사용 여부 결정
        - 환경 변수 USE_OPENAI가 명시적으로 설정되어 있으면 그 값 사용
        - 설정되지 않았으면 자동 판단:
          * 로컬 환경 (localhost, 127.0.0.1, docker 내부) → false
          * 프로덕션 환경 (kimdavid.kr 등) → true
        """
        use_openai_env = os.getenv("USE_OPENAI", "").lower().strip()
        
        # 명시적으로 설정된 경우
        if use_openai_env in ["true", "false"]:
            result = use_openai_env == "true"
            print(f"ℹ️ 환경 변수 설정: USE_OPENAI={use_openai_env} → OpenAI 사용: {result}")
            return result
        
        # 자동 판단: 프로덕션 도메인 체크
        # kimdavid.kr 또는 실제 도메인에서 실행 중이면 OpenAI 사용
        host = os.getenv("HOST", "").lower()
        api_base_url = os.getenv("API_BASE_URL", "").lower()
        environment = os.getenv("ENVIRONMENT", "").lower()
        
        # 프로덕션 환경 감지
        is_production = (
            "kimdavid.kr" in host or
            "kimdavid.kr" in api_base_url or
            environment in ["production", "prod", "prd"] or
            os.getenv("RENDER", "").lower() == "true" or  # Render 배포 환경
            os.getenv("AWS_EXECUTION_ENV", "") != "" or  # AWS 배포 환경
            os.getenv("VERCEL", "").lower() == "true"  # Vercel 배포 환경
        )
        
        # 로컬 환경 감지
        is_local = (
            host in ["localhost", "127.0.0.1", "0.0.0.0", ""] or
            "localhost" in api_base_url or
            "127.0.0.1" in api_base_url or
            environment in ["local", "dev", "development", "test"]
        )
        
        # 판단 결과
        if is_production and not is_local:
            result = True
            print(f"ℹ️ 환경 자동 감지: 프로덕션 환경 → OpenAI 사용: {result}")
        else:
            result = False
            print(f"ℹ️ 환경 자동 감지: 로컬 환경 → OpenAI 사용: {result}")
        
        return result

    def _init_places_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """한국 주요 지역별 데이트 장소 데이터베이스"""
        return {
            "홍대": [
                {"name": "연트럴파크", "category": "카페", "price": "보통", "tags": ["카페", "브런치"], "rating": 4.5, "duration": 90},
                {"name": "앤트러사이트 홍대", "category": "카페", "price": "보통", "tags": ["카페", "디저트"], "rating": 4.3, "duration": 60},
                {"name": "놀부보쌈 홍대점", "category": "식당", "price": "보통", "tags": ["맛집", "한식"], "rating": 4.2, "duration": 90},
                {"name": "홍대 피카소거리", "category": "산책", "price": "저렴", "tags": ["공원", "산책", "문화"], "rating": 4.0, "duration": 60},
                {"name": "무브홀", "category": "공연장", "price": "보통", "tags": ["문화", "공연"], "rating": 4.4, "duration": 120},
            ],
            "합정": [
                {"name": "카페 보통", "category": "카페", "price": "보통", "tags": ["카페", "브런치"], "rating": 4.6, "duration": 90},
                {"name": "앨리웨이", "category": "식당", "price": "보통", "tags": ["맛집", "양식"], "rating": 4.5, "duration": 100},
                {"name": "망원한강공원", "category": "공원", "price": "저렴", "tags": ["공원", "산책", "야외활동"], "rating": 4.7, "duration": 120},
                {"name": "성미산", "category": "산책", "price": "저렴", "tags": ["공원", "산책", "자연"], "rating": 4.3, "duration": 90},
            ],
            "강남": [
                {"name": "테라로사 강남", "category": "카페", "price": "비쌈", "tags": ["카페", "디저트"], "rating": 4.5, "duration": 80},
                {"name": "미쉐린 가이드 레스토랑", "category": "식당", "price": "비쌈", "tags": ["맛집", "고급"], "rating": 4.8, "duration": 120},
                {"name": "코엑스 별마당도서관", "category": "문화", "price": "저렴", "tags": ["문화", "쇼핑"], "rating": 4.6, "duration": 90},
                {"name": "봉은사", "category": "관광", "price": "저렴", "tags": ["문화", "산책"], "rating": 4.4, "duration": 60},
            ],
            "여의도": [
                {"name": "여의도 한강공원", "category": "공원", "price": "저렴", "tags": ["공원", "산책", "야외활동"], "rating": 4.7, "duration": 120},
                {"name": "63빌딩 스카이아트", "category": "전망대", "price": "보통", "tags": ["전망", "데이트"], "rating": 4.5, "duration": 90},
                {"name": "더현대 서울", "category": "쇼핑", "price": "비쌈", "tags": ["쇼핑", "카페"], "rating": 4.6, "duration": 120},
            ],
            "성수": [
                {"name": "대림창고", "category": "카페", "price": "보통", "tags": ["카페", "문화"], "rating": 4.5, "duration": 80},
                {"name": "어니언", "category": "카페", "price": "보통", "tags": ["카페", "디저트"], "rating": 4.6, "duration": 70},
                {"name": "성수연방", "category": "카페", "price": "보통", "tags": ["카페", "갤러리"], "rating": 4.4, "duration": 90},
                {"name": "서울숲", "category": "공원", "price": "저렴", "tags": ["공원", "산책", "자연"], "rating": 4.8, "duration": 120},
            ],
            "이태원": [
                {"name": "이태원 앤틱 가구 거리", "category": "쇼핑", "price": "보통", "tags": ["쇼핑", "문화"], "rating": 4.3, "duration": 90},
                {"name": "트라비", "category": "식당", "price": "비쌈", "tags": ["맛집", "양식"], "rating": 4.7, "duration": 100},
                {"name": "남산타워", "category": "전망대", "price": "보통", "tags": ["전망", "데이트"], "rating": 4.6, "duration": 120},
            ],
        }

    async def recommend_date_courses(
        self,
        preference: Preference,
        existing_courses: List[DateCourse]
    ) -> List[DateCourse]:
        """
        AI를 통한 데이트코스 추천
        
        실제 데이터(영화, 전시회 등)를 먼저 가져온 후,
        OpenAI API로 보강하거나 기본 로직 사용
        """
        # 기존 코스가 있으면 우선 반환
        if existing_courses:
            return existing_courses[:3]

        # 1. 실제 데이터 먼저 가져오기 (영화, 전시회, 공연 등)
        real_data_courses = await self._generate_smart_recommendations(preference)
        
        # 실제 데이터가 있으면 우선 사용
        if real_data_courses:
            print(f"✅ 실제 데이터 기반 코스 {len(real_data_courses)}개 생성 완료")
            
            # OpenAI API 사용 여부 확인
            use_openai = self._should_use_openai()
            
            # OpenAI API로 보강 (선택적, USE_OPENAI=true일 때만)
            if use_openai and self.api_key and self.api_key != "" and len(real_data_courses) < 5:
                try:
                    print("🤖 OpenAI API로 추가 추천 생성 시도...")
                    ai_courses = await self._call_openai_api(preference)
                    if ai_courses:
                        # 실제 데이터와 AI 추천을 합침 (중복 제거)
                        combined = real_data_courses + ai_courses
                        # 제목 기준으로 중복 제거
                        seen_titles = set()
                        unique_courses = []
                        for course in combined:
                            if course.title not in seen_titles:
                                seen_titles.add(course.title)
                                unique_courses.append(course)
                        return unique_courses[:10]
                except Exception as e:
                    print(f"⚠️ OpenAI API 호출 실패, 실제 데이터만 사용: {str(e)}")
            else:
                if not use_openai:
                    print("ℹ️ OpenAI API 사용 비활성화됨 (USE_OPENAI=false 또는 미설정)")
                elif not self.api_key or self.api_key == "":
                    print("ℹ️ OpenAI API 키가 설정되지 않아 실제 데이터만 사용합니다.")
            
            return real_data_courses[:10]
        
        # 실제 데이터가 없으면 OpenAI API 또는 기본 로직 사용
        use_openai = self._should_use_openai()
        
        if use_openai and self.api_key and self.api_key != "":
            try:
                print("🤖 실제 데이터가 없어 OpenAI API로 추천 생성 시도...")
                ai_courses = await self._call_openai_api(preference)
                if ai_courses:
                    return ai_courses
            except Exception as e:
                print(f"⚠️ OpenAI API 호출 실패, 기본 로직 사용: {str(e)}")
        else:
            if not use_openai:
                print("ℹ️ OpenAI API 사용 비활성화됨, 기본 로직 사용")

        # 기본 추천 로직: 지역/관심사/예산 기반
        return await self._generate_smart_recommendations(preference)

    async def _generate_smart_recommendations(self, preference: Preference) -> List[DateCourse]:
        """지역/관심사/예산 기반 스마트 추천"""
        courses = []
        
        # 관심사에 따라 실제 데이터 가져오기
        if '영화' in preference.interests:
            movies = await self.culture_service.get_movies(preference.location, preference.date)
            print(f"영화 데이터 가져옴: {len(movies)}개")  # 디버깅용
            
            if not movies:
                print("⚠️ 영화 데이터가 없습니다. TMDB API 키를 확인하세요.")
                print(f"TMDB API 키 존재 여부: {bool(self.culture_service.tmdb_api_key)}")
            else:
                print(f"✅ 영화 데이터 {len(movies)}개 수신 성공")
            
            movie_courses_count = 0
            for idx, movie in enumerate(movies[:10]):  # 최대 10개로 증가
                movie_title = movie.get('title', '').strip()
                if not movie_title:
                    print(f"⚠️ 제목이 없는 영화 건너뜀: ID={movie.get('id')}, 원제목={movie.get('original_title', 'N/A')}")
                    continue
                
                print(f"✅ 영화 코스 생성: '{movie_title}'")
                    
                course = DateCourse(
                    id=f"movie_{movie.get('id')}_{datetime.now().timestamp()}",
                    title=movie_title,  # 실제 영화 제목 사용
                    description=(movie.get('overview', '') or f"{movie_title}를 관람하세요.").strip(),
                    location=preference.location,
                    category='영화',
                    duration=120,  # 영화는 보통 2시간
                    price_range='보통',
                    tags=['영화', '데이트'],
                    rating=min(movie.get('vote_average', 0) / 2, 5.0),  # TMDB는 10점 만점, 5점 만점으로 변환
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                courses.append(course)
                movie_courses_count += 1
                print(f"   → 코스 추가 완료: ID={course.id}, 제목='{course.title}'")
            
            print(f"✅ 생성된 영화 코스: {movie_courses_count}개 (전체 courses: {len(courses)}개)")
        
        if '전시회' in preference.interests:
            exhibitions = await self.culture_service.get_exhibitions(preference.location, preference.date)
            print(f"전시회 데이터 가져옴: {len(exhibitions)}개")  # 디버깅용
            for idx, exhibition in enumerate(exhibitions[:5]):  # 최대 5개
                exhibition_title = exhibition.get('title', '').strip()
                if not exhibition_title:
                    continue
                    
                course = DateCourse(
                    id=f"exhibition_{exhibition.get('seq', idx)}_{datetime.now().timestamp()}",
                    title=exhibition_title,  # 실제 전시회 제목 사용
                    description=(exhibition.get('description', '') or f"{exhibition_title}를 관람하세요.").strip(),
                    location=exhibition.get('place', preference.location) or preference.location,
                    category='전시회',
                    duration=90,  # 전시회는 보통 1.5시간
                    price_range='보통',
                    tags=['전시회', '문화'],
                    rating=4.5,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                courses.append(course)
        
        if '문화' in preference.interests:
            # 문화 세부 옵션 확인
            genre = None
            if preference.interest_details:
                culture_details = preference.interest_details.get('문화', [])
                if culture_details:
                    genre_map = {
                        '뮤지컬': '뮤지컬',
                        '연극': '연극',
                        '콘서트': '콘서트',
                        '공연': '공연'
                    }
                    for detail in culture_details:
                        if detail in genre_map:
                            genre = genre_map[detail]
                            break
            
            performances = await self.culture_service.get_performances(preference.location, preference.date, genre)
            print(f"공연 데이터 가져옴: {len(performances)}개")  # 디버깅용
            for idx, performance in enumerate(performances[:5]):  # 최대 5개
                performance_title = performance.get('title', '').strip()
                if not performance_title:
                    continue
                    
                course = DateCourse(
                    id=f"performance_{performance.get('seq', idx)}_{datetime.now().timestamp()}",
                    title=performance_title,  # 실제 공연 제목 사용
                    description=(performance.get('description', '') or f"{performance_title}를 관람하세요.").strip(),
                    location=performance.get('place', preference.location) or preference.location,
                    category=performance.get('genre', '문화') or '문화',
                    duration=120,  # 공연은 보통 2시간
                    price_range='비쌈',
                    tags=[performance.get('genre', '문화') or '문화', '공연'],
                    rating=4.5,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                courses.append(course)
        
        # 다른 관심사에 대한 실제 데이터 가져오기
        for interest in preference.interests:
            if interest in ['영화', '전시회', '문화']:
                continue  # 이미 처리됨
            
            places = []
            
            if interest == '카페':
                places = await self.place_service.get_cafes(preference.location)
            elif interest == '맛집':
                # 맛집 세부 옵션 확인
                cuisine_type = None
                if preference.interest_details:
                    restaurant_details = preference.interest_details.get('맛집', [])
                    if restaurant_details:
                        cuisine_type = restaurant_details[0]  # 첫 번째 옵션 사용
                places = await self.place_service.get_restaurants(preference.location, cuisine_type)
            elif interest == '산책':
                places = await self.place_service.get_parks(preference.location)
            elif interest == '쇼핑':
                places = await self.place_service.get_shopping(preference.location)
            elif interest == '실내활동':
                # 실내활동 세부 옵션 확인
                activity_type = None
                if preference.interest_details:
                    indoor_details = preference.interest_details.get('실내활동', [])
                    if indoor_details:
                        activity_type = indoor_details[0]
                places = await self.place_service.get_indoor_activities(preference.location, activity_type)
            elif interest == '야외활동':
                # 야외활동 세부 옵션 확인
                activity_type = None
                if preference.interest_details:
                    outdoor_details = preference.interest_details.get('야외활동', [])
                    if outdoor_details:
                        activity_type = outdoor_details[0]
                places = await self.place_service.get_outdoor_activities(preference.location, activity_type)
            
            # 실제 장소 데이터를 DateCourse로 변환
            for idx, place in enumerate(places[:3]):  # 각 관심사당 최대 3개
                # 가격대 추정 (카테고리별)
                price_range = '보통'
                if interest == '카페':
                    price_range = '저렴'
                elif interest in ['맛집', '쇼핑']:
                    price_range = '보통'
                elif interest in ['실내활동', '야외활동']:
                    price_range = '저렴'
                
                # 소요시간 추정
                duration_map = {
                    '카페': 60,
                    '맛집': 90,
                    '산책': 120,
                    '쇼핑': 180,
                    '실내활동': 120,
                    '야외활동': 180,
                }
                duration = duration_map.get(interest, 120)
                
                course = DateCourse(
                    id=f"{interest}_{place.get('id', idx)}_{datetime.now().timestamp()}",
                    title=place.get('name', f"{interest} 장소"),
                    description=f"{place.get('address', preference.location)}에 위치한 {place.get('name', interest)}입니다. {place.get('category', '')}",
                    location=place.get('address', preference.location),
                    category=interest,
                    duration=duration,
                    price_range=price_range,
                    tags=[interest, place.get('category', '')],
                    rating=place.get('rating', 4.0),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                courses.append(course)
        
        # 실제 데이터가 있으면 반환
        print(f"=== 최종 코스 목록 ===")
        print(f"총 코스 개수: {len(courses)}")
        for idx, course in enumerate(courses):
            print(f"코스 {idx+1}: {course.title} ({course.category})")
        print(f"===================")
        
        if courses:
            return courses[:10]  # 최대 10개
        
        # 실제 데이터가 없으면 기존 로직 사용
        location_places = self._get_places_for_location(preference.location)
        filtered_places = self._filter_by_preferences(location_places, preference)
        recommended_places = self._compose_course_by_time(filtered_places, preference.time_of_day)
        
        # DateCourse 엔티티로 변환
        for idx, place in enumerate(recommended_places[:3]):
            course = DateCourse(
                id=f"rec_{idx}_{datetime.now().timestamp()}",
                title=f"{place['name']} 데이트",
                description=self._generate_description(place, preference),
                location=preference.location,
                category=place['category'],
                duration=place['duration'],
                price_range=place['price'],
                tags=place['tags'],
                rating=place['rating'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            courses.append(course)
        
        return courses if courses else [self._create_fallback_course(preference)]

    def _get_places_for_location(self, location: str) -> List[Dict[str, Any]]:
        """지역에 맞는 장소 가져오기"""
        # 정확히 일치하는 지역
        if location in self.places_db:
            return self.places_db[location]
        
        # 부분 일치하는 지역 찾기
        for key in self.places_db.keys():
            if key in location or location in key:
                return self.places_db[key]
        
        # 일치하는 지역이 없으면 모든 장소 반환
        all_places = []
        for places in self.places_db.values():
            all_places.extend(places)
        return all_places

    def _filter_by_preferences(self, places: List[Dict[str, Any]], preference: Preference) -> List[Dict[str, Any]]:
        """관심사와 예산에 맞게 필터링"""
        filtered = []
        
        for place in places:
            # 예산 체크
            if place['price'] != preference.budget:
                # 예산이 다르면 점수 감소하지만 제외하지는 않음
                place_score = 0.5
            else:
                place_score = 1.0
            
            # 관심사 체크
            for interest in preference.interests:
                if interest in place['tags'] or interest in place['category']:
                    place_score += 1.0
                    
                    # 세부 옵션 체크 (추가 점수)
                    if preference.interest_details and interest in preference.interest_details:
                        details = preference.interest_details[interest]
                        for detail in details:
                            # 세부 옵션이 태그나 카테고리에 포함되면 추가 점수
                            if detail in place['tags'] or detail.lower() in str(place.get('name', '')).lower():
                                place_score += 0.5
            
            if place_score > 0:
                filtered.append({**place, 'score': place_score})
        
        # 점수순으로 정렬
        filtered.sort(key=lambda x: x.get('score', 0), reverse=True)
        return filtered

    def _compose_course_by_time(self, places: List[Dict[str, Any]], time_of_day: str) -> List[Dict[str, Any]]:
        """시간대에 맞는 코스 구성"""
        time_category_map = {
            "아침": ["카페", "브런치", "산책"],
            "점심": ["식당", "맛집", "카페"],
            "오후": ["카페", "쇼핑", "문화", "갤러리", "공원"],
            "저녁": ["식당", "맛집", "전망대", "공연"],
            "밤": ["바", "전망대", "야경"]
        }
        
        preferred_categories = time_category_map.get(time_of_day, ["카페", "식당"])
        
        # 시간대에 맞는 장소 우선 선택
        prioritized = []
        for place in places:
            priority = 0
            for cat in preferred_categories:
                if cat in place['category'] or cat in place['tags']:
                    priority += 2
            
            if priority > 0:
                prioritized.append({**place, 'time_priority': priority})
            else:
                prioritized.append({**place, 'time_priority': 0})
        
        # 시간대 우선순위와 점수를 합산하여 정렬
        prioritized.sort(key=lambda x: (x.get('time_priority', 0) + x.get('score', 0)), reverse=True)
        
        return prioritized

    def _generate_description(self, place: Dict[str, Any], preference: Preference) -> str:
        """장소 설명 생성"""
        weather_msg = f"날씨: {preference.weather}" if preference.weather else ""
        tags_msg = f"추천 이유: {', '.join(place['tags'][:3])}"
        
        # 세부 옵션 메시지 추가
        detail_msg = ""
        if preference.interest_details:
            for interest in preference.interests:
                if interest in preference.interest_details and preference.interest_details[interest]:
                    details = preference.interest_details[interest]
                    if any(detail in place['tags'] or detail.lower() in str(place.get('name', '')).lower() 
                           for detail in details):
                        detail_msg = f"선택하신 세부 옵션({', '.join(details)})에 맞는 장소입니다. "
        
        return (f"{place['name']}에서 특별한 시간을 보내세요. "
                f"{preference.time_of_day} 시간대에 어울리는 {place['category']} 장소입니다. "
                f"{detail_msg}{tags_msg}. {weather_msg}")

    def _create_fallback_course(self, preference: Preference) -> DateCourse:
        """기본 대체 코스 생성"""
        return DateCourse(
            id=None,
            title=f"{preference.location} 추천 데이트 코스",
            description=f"{preference.location} 지역의 {preference.time_of_day} 시간대 데이트 코스입니다. 예산: {preference.budget}, 관심사: {', '.join(preference.interests)}",
            location=preference.location,
            category=preference.interests[0] if preference.interests else "일반",
            duration=120,
            price_range=preference.budget,
            tags=preference.interests,
            rating=4.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    async def _call_openai_api(self, preference: Preference) -> List[DateCourse]:
        """OpenAI API를 호출하여 데이트 코스 추천"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            prompt = self._build_prompt(preference)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 한국의 데이트 코스 추천 전문가입니다. 사용자의 선호도에 맞는 실제 존재하는 장소와 활동을 추천해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                # JSON 블록 추출 (```json ... ``` 형식일 수 있음)
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                data = json.loads(content)
                
                # 응답 형식에 따라 처리
                courses_data = data.get("courses", [data]) if isinstance(data, dict) else data
                
                courses = []
                for course_data in courses_data[:3]:  # 최대 3개
                    if isinstance(course_data, dict):
                        course = DateCourse(
                            id=f"ai_{datetime.now().timestamp()}_{len(courses)}",
                            title=course_data.get("title", f"{preference.location} 데이트"),
                            description=course_data.get("description", "AI 추천 데이트 코스"),
                            location=course_data.get("location", preference.location),
                            category=course_data.get("category", preference.interests[0] if preference.interests else "일반"),
                            duration=course_data.get("duration", 120),
                            price_range=course_data.get("price_range", preference.budget),
                            tags=course_data.get("tags", preference.interests),
                            rating=float(course_data.get("rating", 4.5)),
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        courses.append(course)
                
                return courses if courses else None
                
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 기반으로 처리
                print(f"JSON 파싱 실패, 텍스트 응답: {content[:200]}")
                
                # 간단한 텍스트 기반 코스 생성
                course = DateCourse(
                    id=f"ai_text_{datetime.now().timestamp()}",
                    title=f"AI 추천: {preference.location} 데이트",
                    description=content[:500],  # 첫 500자만 사용
                    location=preference.location,
                    category=preference.interests[0] if preference.interests else "일반",
                    duration=120,
                    price_range=preference.budget,
                    tags=preference.interests,
                    rating=4.5,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                return [course]
                
        except Exception as e:
            print(f"OpenAI API 호출 중 오류: {str(e)}")
            return None

    def _build_prompt(self, preference: Preference) -> str:
        """AI 프롬프트 생성 (OpenAI API용)"""
        # 세부 옵션 텍스트 생성
        detail_text = ""
        if preference.interest_details:
            detail_lines = []
            for interest, details in preference.interest_details.items():
                if details:
                    detail_lines.append(f"  - {interest}: {', '.join(details)}")
            if detail_lines:
                detail_text = "\n세부 선호사항:\n" + "\n".join(detail_lines)
        
        return f"""다음 조건에 맞는 데이트 코스를 3개 추천해주세요:

조건:
- 위치: {preference.location}
- 날짜: {preference.date}
- 시간대: {preference.time_of_day}
- 예산: {preference.budget}
- 관심사: {', '.join(preference.interests)}{detail_text}
- 날씨: {preference.weather or '맑음'}

각 추천 코스에 대해 다음 정보를 JSON 배열 형식으로 제공해주세요:

```json
[
  {{
    "title": "코스 제목 (예: 홍대 감성 카페 투어)",
    "description": "코스에 대한 상세 설명 (어떤 장소들을 방문하고 무엇을 할 수 있는지)",
    "location": "주요 위치",
    "category": "카테고리 (카페/맛집/문화/공원 등)",
    "duration": 소요시간_분단위_숫자,
    "price_range": "저렴/보통/비쌈",
    "tags": ["태그1", "태그2", "태그3"],
    "rating": 4.5
  }}
]
```

실제 존재하는 장소와 활동을 추천해주세요."""

