"""
데이트코스 추천 AI API 서버
DDD 구조로 구현된 FastAPI 애플리케이션
"""
import sys
from pathlib import Path

# 현재 파일의 디렉토리(ai-server)를 sys.path에 추가
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies import get_recommend_date_course_use_case
from app.presentation.routes.date_course_routes import create_date_course_routes
from app.presentation.controllers.culture_controller import CultureController
import traceback
import math

# 서울 범죄 라우터 import (titanic보다 먼저 시도하여 독립적으로 로드)
seoul_crime_router = None
try:
    from app.ml_service.app.seoul_crime.seoul_router import router as seoul_crime_router
    print("✅ Seoul Crime router imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import seoul_crime router: {e}")
    seoul_crime_router = None

# 타이타닉 라우터 import (실패해도 계속 진행)
titanic_router = None
try:
    from app.ml_service.app.titanic.titanic_router import router as titanic_router
    print("✅ Titanic router imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import titanic router: {e}")
    titanic_router = None

# 미국 실업률 라우터 import
us_unemployment_router = None
try:
    from app.us_unemployment.router import router as us_unemployment_router
    print("✅ US Unemployment router imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import us_unemployment router: {e}")
    us_unemployment_router = None

# NLP 라우터 import
nlp_router = None
try:
    from app.ml_service.app.nlp.nlp_router import router as nlp_router
    print("✅ NLP router imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import nlp router: {e}")
    nlp_router = None


def create_app() -> FastAPI:
    """애플리케이션 팩토리"""
    app = FastAPI(
        title="데이트코스 추천 AI API",
        description="DDD 구조로 구현된 데이트코스 추천 서비스 및 타이타닉 ML 서비스",
        version="1.0.0",
        docs_url="/docs",  # Swagger UI 경로
        redoc_url="/redoc",  # ReDoc 경로
        openapi_url="/openapi.json"  # OpenAPI 스키마 경로
    )

    # CORS 설정 - ngrok 및 Vercel 지원
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://www.kimdavid.kr",
            "https://kimdavid.kr",
            "https://*.vercel.app",
            "https://*.ngrok-free.dev",
            "http://localhost:3030",
            "http://localhost:3000",
            "*"  # 개발 환경용
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
            "ngrok-skip-browser-warning",  # ngrok 브라우저 경고 우회
            "*"
        ],
        expose_headers=["*"],
        max_age=3600,
    )

    # 의존성 주입
    recommend_use_case = get_recommend_date_course_use_case()

    # 라우트 등록
    date_course_router = create_date_course_routes(recommend_use_case)
    app.include_router(date_course_router)
    
    # 문화 데이터 라우트 등록
    culture_controller = CultureController()
    app.include_router(culture_controller.router)
    
    # 타이타닉 ML 서비스 라우트 등록
    if titanic_router is not None:
        try:
            app.include_router(titanic_router)
            print(f"✅ Titanic router registered at prefix: {titanic_router.prefix}")
        except Exception as e:
            print(f"❌ Failed to register Titanic router: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ Titanic router not available (import failed)")
    
    # 서울 범죄 ML 서비스 라우트 등록
    if seoul_crime_router is not None:
        try:
            app.include_router(seoul_crime_router)
            print(f"✅ Seoul Crime router registered at prefix: {seoul_crime_router.prefix}")
        except Exception as e:
            print(f"❌ Failed to register Seoul Crime router: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ Seoul Crime router not available (import failed)")
    
    # 미국 실업률 ML 서비스 라우트 등록
    if us_unemployment_router is not None:
        try:
            app.include_router(us_unemployment_router)
            print(f"✅ US Unemployment router registered at prefix: {us_unemployment_router.prefix}")
        except Exception as e:
            print(f"❌ Failed to register US Unemployment router: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ US Unemployment router not available (import failed)")
    
    # NLP ML 서비스 라우트 등록
    if nlp_router is not None:
        try:
            app.include_router(nlp_router)
            print(f"✅ NLP router registered at prefix: {nlp_router.prefix}")
        except Exception as e:
            print(f"❌ Failed to register NLP router: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ NLP router not available (import failed)")

    # 전역 예외 핸들러 추가
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """모든 예외를 처리하는 전역 핸들러"""
        error_trace = traceback.format_exc()
        error_type = type(exc).__name__
        error_message = str(exc)
        
        # 에러 정보를 콘솔에 출력
        print(f"\n❌ Global Exception Handler:")
        print(f"   Path: {request.url.path}")
        print(f"   Method: {request.method}")
        print(f"   Error Type: {error_type}")
        print(f"   Error Message: {error_message}")
        print(f"   Full Traceback:\n{error_trace}")
        
        # 응답에 에러 정보 포함
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_message,
                "error_type": error_type,
                "path": request.url.path,
                "message": f"Internal server error: {error_message}",
                "traceback": error_trace.split('\n')[-20:] if len(error_trace) > 500 else error_trace.split('\n')
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """HTTP 예외 처리"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )

    @app.get("/")
    async def root():
        return {
            "message": "데이트코스 추천 AI API",
            "version": "1.0.0",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

