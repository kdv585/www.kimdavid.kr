import os
import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime


class CultureService:
    """문화 데이터 서비스 (영화, 전시회, 공연)"""

    def __init__(self):
        self.tmdb_api_key = os.getenv("TMDB_API_KEY", "")
        self.data_go_kr_api_key = os.getenv("DATA_GO_KR_API_KEY", "")
        self.arts_api_key = os.getenv("ARTS_API_KEY", "")

    async def get_movies(self, location: str, date: str) -> List[Dict[str, Any]]:
        """현재 상영 중인 영화 가져오기 (TMDB API)"""
        if not self.tmdb_api_key:
            print("TMDB API 키가 설정되지 않았습니다.")
            return []

        try:
            async with httpx.AsyncClient() as client:
                # 한국 영화 상영 중인 영화
                response = await client.get(
                    "https://api.themoviedb.org/3/movie/now_playing",
                    params={
                        "api_key": self.tmdb_api_key,
                        "language": "ko-KR",
                        "region": "KR",
                        "page": 1,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

                movies = []
                results = data.get("results", [])
                print(f"TMDB API 응답: {len(results)}개 영화 발견")
                
                for movie in results:
                    # 제목 가져오기 (한국어 제목 우선)
                    title = movie.get("title", "").strip()
                    original_title = movie.get("original_title", "").strip()
                    
                    # 한국어 제목이 없으면 원제목 사용
                    if not title and original_title:
                        title = original_title
                    
                    if not title:
                        print(f"제목이 없는 영화 건너뜀: {movie.get('id')}")
                        continue
                    
                    overview = movie.get("overview", "").strip()
                    if not overview:
                        overview = f"{title}를 관람하세요."
                    
                    movie_data = {
                        "id": movie.get("id"),
                        "title": title,
                        "overview": overview,
                        "release_date": movie.get("release_date", ""),
                        "poster_path": movie.get("poster_path"),
                        "vote_average": movie.get("vote_average", 0),
                        "genre_ids": movie.get("genre_ids", []),
                    }
                    movies.append(movie_data)
                    print(f"영화 추가: {title}")
                
                print(f"최종 영화 목록: {len(movies)}개")
                # 최대 15개 반환
                return movies[:15]
        except httpx.HTTPStatusError as e:
            print(f"TMDB API HTTP 에러: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"영화 데이터 가져오기 실패: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def get_exhibitions(self, location: str, date: str) -> List[Dict[str, Any]]:
        """전시회 정보 가져오기 (공공데이터포털)"""
        if not self.data_go_kr_api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                # 한국문화예술위원회 전시정보 API
                response = await client.get(
                    "http://apis.data.go.kr/1262000/ExhibitionService/getExhibitionList",
                    params={
                        "serviceKey": self.data_go_kr_api_key,
                        "numOfRows": 10,
                        "pageNo": 1,
                        "stdate": date,
                        "eddate": date,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                
                # XML 응답 파싱
                root = ET.fromstring(response.text)
                exhibitions = []
                
                # XML 네임스페이스 처리
                namespaces = {'ns': 'http://www.openapi.org/ns'}
                
                items = root.findall('.//ns:item', namespaces) or root.findall('.//item')
                for item in items[:10]:
                    exhibition = {
                        "seq": item.findtext('seq', ''),
                        "title": item.findtext('title', '') or item.findtext('exhibitionname', ''),
                        "place": item.findtext('place', '') or item.findtext('place', ''),
                        "start_date": item.findtext('startdate', '') or item.findtext('startdate', ''),
                        "end_date": item.findtext('enddate', '') or item.findtext('enddate', ''),
                        "description": item.findtext('description', '') or item.findtext('exhibitiondesc', ''),
                        "image_url": item.findtext('poster', '') or item.findtext('posterurl', ''),
                    }
                    if exhibition.get('title'):
                        exhibitions.append(exhibition)
                
                return exhibitions
        except ET.ParseError as e:
            print(f"XML 파싱 실패: {e}")
            return []
        except Exception as e:
            print(f"전시회 데이터 가져오기 실패: {e}")
            return []

    async def get_performances(
        self, location: str, date: str, genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """공연 정보 가져오기 (공공데이터포털)"""
        if not self.data_go_kr_api_key:
            return []

        performances = []
        
        # 방법 1: 공연예술 통합전산망 API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://apis.data.go.kr/1262000/PerformanceService/getPerformanceList",
                    params={
                        "serviceKey": self.data_go_kr_api_key,
                        "numOfRows": 15,
                        "pageNo": 1,
                        "stdate": date,
                        "eddate": date,
                        "genre": genre or "",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                
                # XML 응답 파싱
                try:
                    root = ET.fromstring(response.text)
                    # XML 네임스페이스 처리
                    namespaces = {'ns': 'http://www.openapi.org/ns'}
                    
                    items = root.findall('.//ns:item', namespaces) or root.findall('.//item')
                    for item in items:
                        # 다양한 필드명 시도
                        title = (item.findtext('prfnm', '') or 
                                item.findtext('title', '') or 
                                item.findtext('prfnm', '')).strip()
                        
                        if not title:
                            continue
                            
                        performance = {
                            "seq": item.findtext('seq', '') or item.findtext('mt20id', ''),
                            "title": title,
                            "place": (item.findtext('fcltynm', '') or 
                                     item.findtext('place', '') or 
                                     item.findtext('area', '')).strip(),
                            "start_date": item.findtext('prfpdfrom', '') or item.findtext('startdate', ''),
                            "end_date": item.findtext('prfpdto', '') or item.findtext('enddate', ''),
                            "description": (item.findtext('prfcast', '') or 
                                          item.findtext('description', '') or 
                                          item.findtext('pcseguidance', '')).strip(),
                            "genre": (item.findtext('genrenm', '') or 
                                     item.findtext('genre', '') or 
                                     genre or '공연').strip(),
                            "image_url": item.findtext('poster', '') or item.findtext('posterurl', ''),
                        }
                        performances.append(performance)
                except ET.ParseError as e:
                    print(f"XML 파싱 실패: {e}")
                    print(f"응답 내용: {response.text[:500]}")
        except Exception as e:
            print(f"공연 데이터 가져오기 실패 (방법 1): {e}")
        
        # 방법 2: 한국문화예술위원회 공연정보 API (대체 방법)
        if not performances and self.arts_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://www.culture.go.kr/openapi/art/performance/list",
                        params={
                            "serviceKey": self.arts_api_key,
                            "numOfRows": 15,
                            "pageNo": 1,
                            "stdate": date,
                            "eddate": date,
                        },
                        timeout=10.0,
                    )
                    response.raise_for_status()
                    # JSON 또는 XML 응답 처리
                    # (실제 API 형식에 따라 수정 필요)
            except Exception as e:
                print(f"공연 데이터 가져오기 실패 (방법 2): {e}")
        
        return performances[:15]  # 최대 15개 반환

