"""
서울 범죄 데이터 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import importlib.util

# 공통 모듈 경로 추가
current_file = Path(__file__).resolve()

# Docker 환경 확인 및 import 경로 설정
if str(current_file).startswith("/app"):
    # Docker 환경
    base_path = Path("/app")
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))
    
    # sys.path 디버깅
    print(f"🔍 Docker 환경 sys.path: {sys.path[:3]}")
    print(f"🔍 현재 파일 경로: {current_file}")
    
    imported = False
    # Docker 환경 - 실제 경로를 우선 시도 (볼륨 마운트로 인해 /app/app/seoul_crime 구조)
    try:
        from app.seoul_crime.seoul_service import SeoulService
        # common.utils를 직접 import 시도
        try:
            from app.common.utils import create_response, create_error_response
        except ImportError:
            # 직접 파일 로드
            import importlib.util
            import sys
            utils_path = Path("/app/common/utils.py")
            if utils_path.exists():
                spec = importlib.util.spec_from_file_location("common_utils", str(utils_path))
                common_utils = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(common_utils)
                create_response = common_utils.create_response
                create_error_response = common_utils.create_error_response
            else:
                raise ImportError("common/utils.py를 찾을 수 없습니다")
        imported = True
        print("✅ Docker 환경: app.seoul_crime 경로로 import 성공")
    except ImportError as e1:
        import traceback
        print(f"⚠️ app.seoul_crime 경로 import 실패: {e1}")
        print(f"⚠️ 상세 에러:\n{traceback.format_exc()}")
        try:
            from app.ml_service.app.seoul_crime.seoul_service import SeoulService
            from app.ml_service.common.utils import create_response, create_error_response
            imported = True
            print("✅ Docker 환경: app.ml_service.app.seoul_crime 경로로 import 성공")
        except ImportError as e2:
            print(f"⚠️ app.ml_service.app.seoul_crime 경로 import 실패: {e2}")
            raise ImportError(f"모든 import 경로 실패: {e1}, {e2}")
    
    if not imported:
        raise ImportError("SeoulService를 import할 수 없습니다.")
else:
    # 로컬 환경
    ai_server_path = current_file.parent.parent.parent.parent.parent
    if ai_server_path.exists() and str(ai_server_path) not in sys.path:
        sys.path.insert(0, str(ai_server_path))
    try:
        from app.ml_service.app.seoul_crime.seoul_service import SeoulService
        from app.ml_service.common.utils import create_response, create_error_response
        print("✅ 로컬 환경: app.ml_service.app.seoul_crime 경로로 import 성공")
    except ImportError as e:
        print(f"⚠️ 로컬 환경 import 실패: {e}")
        raise

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seoul_crime", tags=["seoul"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[SeoulService] = None


def get_service() -> SeoulService:
    """SeoulService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SeoulService()
    return _service_instance


@router.get("/")
@router.post("/")
async def seoul_root():
    """서울 범죄 데이터 서비스 루트 - 데이터 로드"""
    try:
        service = get_service()
        result = service.load_data()
        return create_response(
            data=result,
            message="서울 범죄 데이터가 성공적으로 로드되었습니다"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"데이터 파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 로드 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/preprocess")
@router.post("/preprocess")
async def preprocess_data():
    """
    서울 범죄 데이터 전처리 실행
    - CCTV, Crime, Pop 데이터 로드 및 머지
    - 피처 삭제, 인코딩, 결측치 처리 등 전체 전처리 파이프라인 실행
    """
    try:
        service = get_service()
        result = service.preprocess()
        return create_response(
            data=result,
            message="데이터 전처리가 완료되었습니다"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"데이터 파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/preprocess/table")
@router.post("/preprocess/table")
async def preprocess_table():
    """
    서울 범죄 데이터 전처리 결과를 JSON 형식으로 반환
    - /preprocess와 동일한 기능이지만 호환성을 위해 별도 엔드포인트 제공
    """
    try:
        service = get_service()
        result = service.preprocess()
        return create_response(
            data=result,
            message="데이터 전처리가 완료되었습니다"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"데이터 파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/heatmap")
@router.post("/heatmap")
async def create_heatmap(
    crime_type: str = Query(default="total", description="범죄 유형 (total, 살인, 강도, 강간, 절도, 폭력)"),
    save_path: Optional[str] = Query(default=None, description="저장 경로 (선택사항)")
):
    """
    서울 범죄 데이터 히트맵 생성
    
    - 범죄 유형별로 서울 지도에 히트맵을 생성합니다
    - HTML 파일로 저장되어 브라우저에서 열어볼 수 있습니다
    
    Args:
        crime_type: 범죄 유형 (total: 전체, 살인, 강도, 강간, 절도, 폭력)
        save_path: 저장 경로 (선택사항, 기본값: save/crime_heatmap_{crime_type}.html)
    """
    try:
        service = get_service()
        logger.info(f"히트맵 생성 요청: crime_type={crime_type}, save_path={save_path}")
        result = service.create_heatmap(crime_type=crime_type, save_path=save_path)
        logger.info(f"히트맵 생성 성공: {result.get('file_path', 'N/A')}")
        return create_response(
            data=result,
            message=f"{crime_type} 범죄 히트맵이 성공적으로 생성되었습니다"
        )
    except ImportError as e:
        error_msg = str(e)
        logger.error(f"ImportError 발생: {error_msg}")
        import traceback
        logger.error(traceback.format_exc())
        # 중복 메시지 제거
        if "'pip install folium'으로 설치해주세요." in error_msg:
            error_msg = error_msg.split("'pip install folium'으로 설치해주세요.")[0] + "'pip install folium'으로 설치해주세요."
        raise HTTPException(
            status_code=500,
            detail=f"필수 라이브러리가 설치되지 않았습니다: {error_msg}"
        )
    except Exception as e:
        logger.error(f"히트맵 생성 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"히트맵 생성 중 오류가 발생했습니다: {str(e)}"
        )