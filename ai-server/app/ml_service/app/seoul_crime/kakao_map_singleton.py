import os
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

class KakaoMapSingleton:
    _instance = None  # 싱글턴 인스턴스를 저장할 클래스 변수
    _dotenv_loaded = False  # .env 파일 로드 여부

    def __new__(cls):
        if cls._instance is None:  # 인스턴스가 없으면 생성
            cls._instance = super(KakaoMapSingleton, cls).__new__(cls)
            cls._instance._api_key = cls._instance._retrieve_api_key()  # API 키 가져오기
            cls._instance._base_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        return cls._instance  # 기존 인스턴스 반환

    @classmethod
    def _load_env_file(cls):
        """프로젝트 루트의 .env 파일을 로드하는 메서드"""
        if cls._dotenv_loaded:
            return
        
        import logging
        logger = logging.getLogger(__name__)
        
        # 현재 파일의 경로에서 프로젝트 루트 찾기
        current_file = Path(__file__).resolve()
        
        # Docker 환경 확인 (/app으로 시작하면 Docker)
        if str(current_file).startswith("/app"):
            # Docker 환경: 볼륨 마운트로 ./ai-server:/app
            # 프로젝트 루트의 .env 파일은 볼륨 마운트 범위 밖이므로 접근 불가
            # docker-compose.yaml에서 환경 변수로 전달되므로 .env 파일 로드는 생략
            # 환경 변수에서 직접 읽음 (이미 docker-compose.yaml에서 전달됨)
            logger.info("Docker 환경: 환경 변수에서 API 키를 읽습니다 (docker-compose.yaml에서 전달됨)")
            cls._dotenv_loaded = True
            return
        else:
            # 로컬 환경: ai-server/app/ml_service/app/seoul_crime/kakao_map_singleton.py
            # 프로젝트 루트는 ai-server의 상위 디렉토리
            ai_server_root = current_file.parent.parent.parent.parent.parent
            project_root = ai_server_root.parent
            env_file = project_root / ".env"
        
        # .env 파일이 존재하면 로드
        if env_file.exists():
            load_dotenv(env_file, override=False)  # override=False: 기존 환경 변수 우선
            cls._dotenv_loaded = True
            logger.info(f"✅ .env 파일 로드 완료: {env_file}")
        else:
            logger.warning(f"⚠️ .env 파일을 찾을 수 없습니다: {env_file}")
            logger.info("환경 변수에서 API 키를 확인합니다...")

    def _retrieve_api_key(self):
        """API 키를 환경 변수 또는 .env 파일에서 가져오는 내부 메서드"""
        # .env 파일 로드 (한 번만)
        self._load_env_file()
        
        # 환경 변수에서 API 키 가져오기
        api_key = os.getenv("KAKAO_REST_API_KEY", "")
        
        import logging
        logger = logging.getLogger(__name__)
        
        if not api_key:
            logger.warning("KAKAO_REST_API_KEY 환경 변수가 설정되지 않았습니다.")
            logger.warning("프로젝트 루트의 .env 파일에 KAKAO_REST_API_KEY를 추가하거나, docker-compose.yaml의 environment에 설정하세요.")
            # 에러를 발생시키지 않고 빈 문자열 반환 (나중에 403 에러로 처리)
            return ""
        
        logger.info(f"카카오맵 API 키 로드 완료 (길이: {len(api_key)})")
        return api_key

    def get_api_key(self):
        """저장된 API 키 반환"""
        return self._api_key

    def geocode(self, address: str, language: str = 'ko') -> List[Dict[str, Any]]:
        """
        주소를 위도, 경도로 변환하는 메서드 (카카오 로컬 API 사용)
        
        Args:
            address: 검색할 주소
            language: 언어 설정 (기본값: 'ko')
        
        Returns:
            구글맵 API와 호환되는 형식의 리스트
        """
        if not self._api_key:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("카카오맵 API 키가 설정되지 않았습니다.")
            return []
        
        try:
            headers = {
                "Authorization": f"KakaoAK {self._api_key}"
            }
            params = {
                "query": address
            }
            
            response = requests.get(self._base_url, headers=headers, params=params, timeout=5)
            
            # 403 에러인 경우 상세 정보 로깅
            if response.status_code == 403:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"카카오맵 API 403 Forbidden: API 키가 없거나 잘못되었습니다. (주소: {address})")
                logger.error(f"API 키 존재 여부: {bool(self._api_key)}, API 키 길이: {len(self._api_key) if self._api_key else 0}")
                try:
                    error_data = response.json()
                    logger.error(f"에러 응답: {error_data}")
                    # OPEN_MAP_AND_LOCAL service disabled 에러인 경우 안내 메시지 추가
                    if 'OPEN_MAP_AND_LOCAL' in str(error_data):
                        logger.error("⚠️ 카카오 로컬 API(주소 검색) 서비스가 비활성화되어 있습니다.")
                        logger.error("해결 방법:")
                        logger.error("1. 카카오 개발자 콘솔(https://developers.kakao.com) 접속")
                        logger.error("2. 내 애플리케이션 → 해당 앱 선택")
                        logger.error("3. 앱 키 → REST API 키 확인 (현재 사용 중인 키와 일치하는지 확인)")
                        logger.error("4. 카카오맵 → 사용 설정 → 상태 ON 확인")
                        logger.error("5. .env 파일의 KAKAO_REST_API_KEY가 올바른 앱의 REST API 키인지 확인")
                except:
                    logger.error(f"에러 응답 텍스트: {response.text[:200]}")
                return []
            
            response.raise_for_status()
            
            data = response.json()
            
            # 디버깅: API 응답 로깅
            import logging
            logger = logging.getLogger(__name__)
            if not data.get("documents") or len(data.get("documents", [])) == 0:
                logger.debug(f"검색 쿼리: {address}, API 응답: {data}")
            
            # 카카오 키워드 검색 API 응답을 구글맵 API 형식으로 변환
            results = []
            if data.get("documents"):
                for doc in data.get("documents", []):
                    # 카카오 키워드 검색 API 응답 형식
                    # 도로명 주소 우선, 없으면 지번 주소
                    formatted_address = doc.get("road_address_name", "") or doc.get("address_name", "")
                    
                    # 좌표 정보
                    x = float(doc.get("x", 0))  # 경도 (longitude)
                    y = float(doc.get("y", 0))  # 위도 (latitude)
                    
                    # 구글맵 API 형식으로 변환
                    result = {
                        "formatted_address": formatted_address,
                        "geometry": {
                            "location": {
                                "lat": y,  # 위도
                                "lng": x   # 경도
                            }
                        }
                    }
                    results.append(result)
            
            return results
            
        except requests.exceptions.HTTPError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"카카오맵 API HTTP 에러 발생: {e.response.status_code} - {str(e)}")
            if e.response.status_code == 403:
                logger.error("403 Forbidden: API 키를 확인하세요. .env 파일에 KAKAO_REST_API_KEY가 설정되어 있는지 확인하세요.")
            return []
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"카카오맵 API 호출 중 오류 발생: {str(e)}")
            return []
