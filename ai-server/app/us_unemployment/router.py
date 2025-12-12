"""
미국 실업률 데이터 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pathlib import Path
import sys

# 공통 모듈 경로 추가
current_file = Path(__file__).resolve()

# Docker 환경 확인 및 import 경로 설정
if str(current_file).startswith("/app"):
    # Docker 환경
    base_path = Path("/app")
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))
    
    imported = False
    try:
        from app.us_unemployment.service import UnemploymentService
        from app.ml_service.common.utils import create_response, create_error_response
        imported = True
        print("✅ Docker 환경: app.us_unemployment 경로로 import 성공")
    except ImportError as e1:
        print(f"⚠️ app.us_unemployment 경로 import 실패: {e1}")
        try:
            from app.ml_service.common.utils import create_response, create_error_response
            # 직접 경로로 import 시도
            import importlib.util
            service_path = Path("/app/app/us_unemployment/service.py")
            if service_path.exists():
                spec = importlib.util.spec_from_file_location("us_unemployment_service", service_path)
                service_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(service_module)
                UnemploymentService = service_module.UnemploymentService
                imported = True
                print("✅ Docker 환경: 직접 경로로 import 성공")
            else:
                raise ImportError(f"서비스 파일을 찾을 수 없습니다: {service_path}")
        except Exception as e2:
            print(f"⚠️ 직접 경로 import 실패: {e2}")
            raise ImportError(f"모든 import 경로 실패: {e1}, {e2}")
    
    if not imported:
        raise ImportError("UnemploymentService를 import할 수 없습니다.")
else:
    # 로컬 환경
    ai_server_path = current_file.parent.parent.parent
    if ai_server_path.exists() and str(ai_server_path) not in sys.path:
        sys.path.insert(0, str(ai_server_path))
    try:
        from app.us_unemployment.service import UnemploymentService
        from app.ml_service.common.utils import create_response, create_error_response
        print("✅ 로컬 환경: app.us_unemployment 경로로 import 성공")
    except ImportError as e:
        print(f"⚠️ 로컬 환경 import 실패: {e}")
        # create_response가 없으면 기본 함수 사용
        def create_response(data, message="Success"):
            return {"success": True, "data": data, "message": message}
        def create_error_response(error, message="Error"):
            return {"success": False, "error": error, "message": message}

import logging

logger = logging.getLogger(__name__)

# 라우터 생성 - prefix를 /api/ml/usa로 설정
router = APIRouter(prefix="/api/ml/usa", tags=["us_unemployment"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[UnemploymentService] = None


def get_service() -> UnemploymentService:
    """UnemploymentService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = UnemploymentService()
    return _service_instance


@router.get("/")
@router.post("/")
async def unemployment_root():
    """미국 실업률 데이터 서비스 루트"""
    try:
        service = get_service()
        result = service.load_data()
        return create_response(
            data=result,
            message="미국 실업률 데이터 서비스가 준비되었습니다"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"데이터 파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"서비스 초기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/load")
@router.post("/load")
async def load_data(filename: Optional[str] = Query(default=None, description="데이터 파일명")):
    """
    미국 실업률 데이터 로드
    
    Args:
        filename: 데이터 파일명 (선택사항, 기본값: 자동 검색)
    
    Returns:
        로드된 데이터 정보
    """
    try:
        service = get_service()
        result = service.load_data(filename=filename)
        return create_response(
            data=result,
            message="데이터가 성공적으로 로드되었습니다"
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
    미국 실업률 데이터 전처리 실행
    
    Returns:
        전처리된 데이터 정보
    """
    try:
        service = get_service()
        result = service.preprocess()
        return create_response(
            data=result,
            message="데이터 전처리가 완료되었습니다"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/statistics")
async def get_statistics(value_column: Optional[str] = Query(default=None, description="통계를 계산할 컬럼명")):
    """
    실업률 통계 정보 조회
    
    Args:
        value_column: 통계를 계산할 컬럼명 (선택사항, 기본값: 자동 검색)
    
    Returns:
        통계 정보
    """
    try:
        service = get_service()
        result = service.get_statistics(value_column=value_column)
        return create_response(
            data=result,
            message="통계 정보가 성공적으로 계산되었습니다"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 계산 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/state/{state}")
async def get_by_state(state: str):
    """
    특정 주의 실업률 데이터 조회
    
    Args:
        state: 주 이름 또는 코드 (예: California, CA, New York)
    
    Returns:
        해당 주의 실업률 데이터
    """
    try:
        service = get_service()
        result = service.get_by_state(state)
        
        if result.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=result.get("message", f"'{state}'에 해당하는 데이터를 찾을 수 없습니다.")
            )
        
        return create_response(
            data=result,
            message=result.get("message", "데이터가 성공적으로 조회되었습니다")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"주별 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/save")
async def save_processed_data(filename: Optional[str] = Query(default=None, description="저장할 파일명")):
    """
    전처리된 데이터 저장
    
    Args:
        filename: 저장할 파일명 (선택사항)
    
    Returns:
        저장 결과 정보
    """
    try:
        service = get_service()
        result = service.save_processed_data(filename=filename)
        return create_response(
            data=result,
            message="전처리된 데이터가 성공적으로 저장되었습니다"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 저장 중 오류가 발생했습니다: {str(e)}"
        )

