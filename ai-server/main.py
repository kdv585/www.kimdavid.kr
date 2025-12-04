"""
데이트코스 추천 AI API 서버
DDD 구조로 구현된 FastAPI 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_recommend_date_course_use_case
from app.presentation.routes.date_course_routes import create_date_course_routes


def create_app() -> FastAPI:
    """애플리케이션 팩토리"""
    app = FastAPI(
        title="데이트코스 추천 AI API",
        description="DDD 구조로 구현된 데이트코스 추천 서비스",
        version="1.0.0"
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

