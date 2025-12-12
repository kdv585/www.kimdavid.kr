"""
NLP 자연어 처리 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import sys
import logging

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
        from app.nlp.emma.emma_wordcloud import NLPService
        try:
            from app.common.utils import create_response, create_error_response
        except ImportError:
            import importlib.util
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
        print("✅ Docker 환경: app.nlp 경로로 import 성공")
    except ImportError as e1:
        print(f"⚠️ app.nlp 경로 import 실패: {e1}")
        try:
            from app.ml_service.app.nlp.emma.emma_wordcloud import NLPService
            from app.ml_service.common.utils import create_response, create_error_response
            imported = True
            print("✅ Docker 환경: app.ml_service.app.nlp 경로로 import 성공")
        except ImportError as e2:
            print(f"⚠️ app.ml_service.app.nlp 경로 import 실패: {e2}")
            raise ImportError(f"모든 import 경로 실패: {e1}, {e2}")
    
    if not imported:
        raise ImportError("NLPService를 import할 수 없습니다.")
else:
    # 로컬 환경
    ai_server_path = current_file.parent.parent.parent.parent.parent
    if ai_server_path.exists() and str(ai_server_path) not in sys.path:
        sys.path.insert(0, str(ai_server_path))
    try:
        from app.ml_service.app.nlp.emma.emma_wordcloud import NLPService
        try:
            from app.ml_service.common.utils import create_response, create_error_response
        except ImportError:
            # utils가 없으면 기본 함수 사용
            def create_response(data: Any = None, message: str = "success", status_code: int = 200):
                return {"status": "success", "message": message, "data": data}
            
            def create_error_response(message: str, status_code: int = 500):
                return {"status": "error", "message": message}
        print("✅ 로컬 환경: app.ml_service.app.nlp 경로로 import 성공")
    except ImportError as e:
        print(f"⚠️ 로컬 환경 import 실패: {e}")
        raise

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml/nlp", tags=["nlp"])


class WordCloudRequest(BaseModel):
    """워드클라우드 생성 요청 모델"""
    text: str = Field(..., description="워드클라우드를 생성할 텍스트")
    width: int = Field(1000, description="이미지 너비")
    height: int = Field(600, description="이미지 높이")
    background_color: str = Field("white", description="배경색")
    max_words: int = Field(100, description="최대 단어 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Emma refused to permit us to obtain the refuse permit",
                "width": 1000,
                "height": 600,
                "background_color": "white",
                "max_words": 100
            }
        }

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[NLPService] = None


def get_service() -> NLPService:
    """NLPService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = NLPService()
    return _service_instance


@router.get("/")
@router.post("/")
async def nlp_root():
    """NLP 서비스 루트"""
    try:
        return create_response(
            data={
                "service": "mlservice",
                "module": "nlp",
                "status": "running",
                "available_endpoints": [
                    "GET /api/ml/nlp/ - 서비스 상태 확인",
                    "POST /api/ml/nlp/emma - 워드클라우드 생성 (텍스트 입력)",
                    "GET /api/ml/nlp/data/wordcloud - data 디렉토리 파일로 워드클라우드 생성 및 save 디렉토리에 저장",
                    "POST /api/ml/nlp/data/wordcloud - data 디렉토리 파일로 워드클라우드 생성 및 save 디렉토리에 저장"
                ]
            },
            message="NLP Service is running"
        )
    except Exception as e:
        logger.error(f"NLP 서비스 루트 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"서비스 초기화 중 오류가 발생했습니다: {str(e)}"
        )


def _generate_wordcloud_internal(text: str, width: int, height: int, 
                                  background_color: str, max_words: int):
    """워드클라우드 생성 내부 로직"""
    service = get_service()
    result = service.generate_wordcloud(
        text=text,
        width=width,
        height=height,
        background_color=background_color,
        max_words=max_words
    )
    
    if "error" in result:
        return create_error_response(
            message=result["error"],
            status_code=500
        )
    
    return create_response(
        data=result,
        message="워드클라우드가 성공적으로 생성되었습니다."
    )


@router.get("/emma")
async def generate_emma_wordcloud_get(
    text: str = Query(..., description="워드클라우드를 생성할 텍스트"),
    width: int = Query(1000, description="이미지 너비"),
    height: int = Query(600, description="이미지 높이"),
    background_color: str = Query("white", description="배경색"),
    max_words: int = Query(100, description="최대 단어 수")
):
    """
    워드클라우드 생성 엔드포인트 (GET)
    
    Query parameter로 요청:
    - text: 필수, 워드클라우드를 생성할 텍스트
    - width: 선택, 이미지 너비 (기본값: 1000)
    - height: 선택, 이미지 높이 (기본값: 600)
    - background_color: 선택, 배경색 (기본값: "white")
    - max_words: 선택, 최대 단어 수 (기본값: 100)
    
    예시: GET /api/ml/nlp/emma?text=Hello%20World&width=1000&height=600
    
    Returns:
        워드클라우드 정보 (base64 인코딩된 이미지 포함)
    """
    try:
        return _generate_wordcloud_internal(text, width, height, background_color, max_words)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"워드클라우드 생성 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/emma")
async def generate_emma_wordcloud_post(request: WordCloudRequest):
    """
    워드클라우드 생성 엔드포인트 (POST)
    
    JSON body로 요청:
    {
        "text": "워드클라우드를 생성할 텍스트",
        "width": 1000,
        "height": 600,
        "background_color": "white",
        "max_words": 100
    }
    
    Args:
        request: 워드클라우드 생성 요청
        
    Returns:
        워드클라우드 정보 (base64 인코딩된 이미지 포함)
    """
    try:
        return _generate_wordcloud_internal(
            text=request.text,
            width=request.width,
            height=request.height,
            background_color=request.background_color,
            max_words=request.max_words
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"워드클라우드 생성 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )


class WordCloudFromDataRequest(BaseModel):
    """data 디렉토리 파일로부터 워드클라우드 생성 요청 모델"""
    filename: Optional[str] = Field(None, description="data 디렉토리에서 읽을 파일명 (선택사항, 없으면 모든 텍스트 파일 처리)")
    width: int = Field(1000, description="이미지 너비")
    height: int = Field(600, description="이미지 높이")
    background_color: str = Field("white", description="배경색")
    max_words: int = Field(100, description="최대 단어 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "kr-Report_2018.txt",
                "width": 1000,
                "height": 600,
                "background_color": "white",
                "max_words": 100
            }
        }


@router.get("/data/wordcloud")
async def generate_wordcloud_from_data(
    filename: Optional[str] = Query(None, description="data 디렉토리에서 읽을 파일명 (선택사항, 없으면 모든 텍스트 파일 처리)"),
    width: int = Query(1000, description="이미지 너비"),
    height: int = Query(600, description="이미지 높이"),
    background_color: str = Query("white", description="배경색"),
    max_words: int = Query(100, description="최대 단어 수")
):
    """
    data 디렉토리에 있는 텍스트 파일로부터 워드클라우드 생성 및 save 디렉토리에 저장 (GET)
    
    Query parameter로 요청:
    - filename: 선택, 처리할 파일명 (없으면 모든 .txt 파일 처리, stopwords.txt 제외)
    - width: 선택, 이미지 너비 (기본값: 1000)
    - height: 선택, 이미지 높이 (기본값: 600)
    - background_color: 선택, 배경색 (기본값: "white")
    - max_words: 선택, 최대 단어 수 (기본값: 100)
    
    Returns:
        워드클라우드 정보 (base64 인코딩된 이미지 포함, save 디렉토리에 저장됨)
    """
    try:
        # data 디렉토리 경로 설정
        data_dir = current_file.parent / "data"
        
        if not data_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"data 디렉토리를 찾을 수 없습니다: {data_dir}"
            )
        
        # 처리할 파일 목록 결정
        text_files = []
        if filename:
            file_path = data_dir / filename
            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"파일을 찾을 수 없습니다: {filename}"
                )
            if file_path.suffix.lower() in ['.txt', '.csv'] and file_path.name != 'stopwords.txt':
                text_files.append(file_path)
        else:
            # 모든 텍스트 파일 찾기 (stopwords.txt 제외)
            text_files = [f for f in data_dir.glob("*.txt") 
                         if f.name != 'stopwords.txt'] + list(data_dir.glob("*.csv"))
        
        if not text_files:
            raise HTTPException(
                status_code=404,
                detail="처리할 텍스트 파일이 없습니다."
            )
        
        results = []
        for file_path in text_files:
            try:
                # 파일 읽기
                encoding = 'utf-8'
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                except UnicodeDecodeError:
                    # UTF-8 실패 시 다른 인코딩 시도
                    try:
                        with open(file_path, 'r', encoding='cp949') as f:
                            text = f.read()
                    except:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                
                if not text.strip():
                    logger.warning(f"파일이 비어있습니다: {file_path.name}")
                    continue
                
                # 워드클라우드 생성 (자동으로 save 디렉토리에 저장됨)
                result = _generate_wordcloud_internal(
                    text=text,
                    width=width,
                    height=height,
                    background_color=background_color,
                    max_words=max_words
                )
                
                if "data" in result:
                    result["data"]["source_file"] = file_path.name
                    result["data"]["source_path"] = str(file_path)
                    results.append(result["data"])
                else:
                    results.append({
                        "filename": file_path.name,
                        "error": result.get("message", "워드클라우드 생성 실패")
                    })
                    
            except Exception as e:
                logger.error(f"파일 처리 실패 {file_path.name}: {str(e)}")
                results.append({
                    "filename": file_path.name,
                    "error": str(e)
                })
        
        if not results:
            raise HTTPException(
                status_code=500,
                detail="모든 파일 처리에 실패했습니다."
            )
        
        return create_response(
            data=results if len(results) > 1 else results[0],
            message=f"{len(text_files)}개 파일에서 워드클라우드를 생성하고 save 디렉토리에 저장했습니다."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"data 디렉토리 워드클라우드 생성 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/data/wordcloud")
async def generate_wordcloud_from_data_post(request: WordCloudFromDataRequest):
    """
    data 디렉토리에 있는 텍스트 파일로부터 워드클라우드 생성 및 save 디렉토리에 저장 (POST)
    
    JSON body로 요청:
    {
        "filename": "kr-Report_2018.txt" (선택사항, 없으면 모든 텍스트 파일 처리),
        "width": 1000,
        "height": 600,
        "background_color": "white",
        "max_words": 100
    }
    
    Returns:
        워드클라우드 정보 (base64 인코딩된 이미지 포함, save 디렉토리에 저장됨)
    """
    try:
        # data 디렉토리 경로 설정
        data_dir = current_file.parent / "data"
        
        filename = request.filename
        width = request.width
        height = request.height
        background_color = request.background_color
        max_words = request.max_words
        
        if not data_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"data 디렉토리를 찾을 수 없습니다: {data_dir}"
            )
        
        # 처리할 파일 목록 결정
        text_files = []
        if filename:
            file_path = data_dir / filename
            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"파일을 찾을 수 없습니다: {filename}"
                )
            if file_path.suffix.lower() in ['.txt', '.csv'] and file_path.name != 'stopwords.txt':
                text_files.append(file_path)
        else:
            # 모든 텍스트 파일 찾기 (stopwords.txt 제외)
            text_files = [f for f in data_dir.glob("*.txt") 
                         if f.name != 'stopwords.txt'] + list(data_dir.glob("*.csv"))
        
        if not text_files:
            raise HTTPException(
                status_code=404,
                detail="처리할 텍스트 파일이 없습니다."
            )
        
        results = []
        for file_path in text_files:
            try:
                # 파일 읽기
                encoding = 'utf-8'
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                except UnicodeDecodeError:
                    # UTF-8 실패 시 다른 인코딩 시도
                    try:
                        with open(file_path, 'r', encoding='cp949') as f:
                            text = f.read()
                    except:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                
                if not text.strip():
                    logger.warning(f"파일이 비어있습니다: {file_path.name}")
                    continue
                
                # 워드클라우드 생성 (자동으로 save 디렉토리에 저장됨)
                result = _generate_wordcloud_internal(
                    text=text,
                    width=width,
                    height=height,
                    background_color=background_color,
                    max_words=max_words
                )
                
                if "data" in result:
                    result["data"]["source_file"] = file_path.name
                    result["data"]["source_path"] = str(file_path)
                    results.append(result["data"])
                else:
                    results.append({
                        "filename": file_path.name,
                        "error": result.get("message", "워드클라우드 생성 실패")
                    })
                    
            except Exception as e:
                logger.error(f"파일 처리 실패 {file_path.name}: {str(e)}")
                results.append({
                    "filename": file_path.name,
                    "error": str(e)
                })
        
        if not results:
            raise HTTPException(
                status_code=500,
                detail="모든 파일 처리에 실패했습니다."
            )
        
        return create_response(
            data=results if len(results) > 1 else results[0],
            message=f"{len(text_files)}개 파일에서 워드클라우드를 생성하고 save 디렉토리에 저장했습니다."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"data 디렉토리 워드클라우드 생성 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )

