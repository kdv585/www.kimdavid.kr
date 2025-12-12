"""
Titanic Service - FastAPI 애플리케이션
"""
import sys
import csv
import os
import logging
import importlib.util
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# 공통 모듈 경로 추가 (최우선)
current_file = Path(__file__).resolve()
base_dir = current_file.parent  # /app (Docker) 또는 ml_service (로컬)

# 경로 추가
base_path_str = str(base_dir)
if base_path_str not in sys.path:
    sys.path.insert(0, base_path_str)

# Docker 환경 확인 및 /app 경로 추가
if os.path.exists("/app"):
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")
    
    # Docker 환경에서 app.ml_service 경로도 추가
    app_ml_service_path = "/app"
    if app_ml_service_path not in sys.path:
        sys.path.insert(0, app_ml_service_path)

# 설정 로드 (경로 설정 후)
try:
    from app.config import TitanicServiceConfig
    config = TitanicServiceConfig()
except Exception as e:
    # config.py를 찾을 수 없는 경우 기본값 사용
    class Config:
        service_name = "mlservice"
        service_version = "1.0.0"
        port = 9010
    config = Config()

# 라우터 및 공통 모듈 import
titanic_router = None
seoul_crime_router = None
nlp_router = None
LoggingMiddleware = None
LOGGING_MIDDLEWARE_AVAILABLE = False

try:
    # Docker 환경: /app/app/titanic/titanic_router.py
    # 로컬 환경: app/ml_service/app/titanic/titanic_router.py
    try:
        # Docker 환경 - 실제 경로를 우선 시도 (볼륨 마운트로 인해 /app/app/seoul_crime 구조)
        from app.titanic.titanic_router import router as titanic_router
        from app.seoul_crime.seoul_router import router as seoul_crime_router
        from app.nlp.nlp_router import router as nlp_router
        # common 모듈 직접 로드
        try:
            from app.common.middleware import LoggingMiddleware
            from app.common.utils import setup_logging
        except ImportError:
            import importlib.util
            from pathlib import Path
            # middleware 직접 로드
            middleware_path = Path("/app/common/middleware.py")
            if middleware_path.exists():
                spec = importlib.util.spec_from_file_location("common_middleware", str(middleware_path))
                common_middleware = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(common_middleware)
                LoggingMiddleware = common_middleware.LoggingMiddleware
            else:
                LoggingMiddleware = None
            # utils 직접 로드
            utils_path = Path("/app/common/utils.py")
            if utils_path.exists():
                spec = importlib.util.spec_from_file_location("common_utils", str(utils_path))
                common_utils = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(common_utils)
                setup_logging = common_utils.setup_logging
            else:
                import logging
                def setup_logging(name):
                    return logging.getLogger(name)
        print("✅ Docker 환경 경로로 import 성공")
    except ImportError as e1:
        print(f"⚠️ Docker 환경 경로 import 실패: {e1}")
        # app.ml_service 경로 시도
        try:
            from app.ml_service.app.titanic.titanic_router import router as titanic_router
            from app.ml_service.app.seoul_crime.seoul_router import router as seoul_crime_router
            from app.ml_service.app.nlp.nlp_router import router as nlp_router
            from app.ml_service.common.middleware import LoggingMiddleware
            from app.ml_service.common.utils import setup_logging
            print("✅ app.ml_service 경로로 import 성공")
        except ImportError as e2:
            print(f"⚠️ app.ml_service 경로 import 실패: {e2}")
            # 직접 경로로 import 시도 (Docker 환경)
            try:
                import importlib.util
                from pathlib import Path
                
                # NLP 라우터 직접 로드
                nlp_router_path = Path("/app/app/nlp/nlp_router.py")
                if nlp_router_path.exists():
                    spec = importlib.util.spec_from_file_location("nlp_router", str(nlp_router_path))
                    nlp_router_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(nlp_router_module)
                    nlp_router = nlp_router_module.router
                    print("✅ 직접 경로로 NLP 라우터 import 성공")
                else:
                    nlp_router = None
                    print("⚠️ NLP 라우터 파일을 찾을 수 없습니다")
            except Exception as e3:
                print(f"⚠️ 직접 경로 import 실패: {e3}")
                nlp_router = None
    
    if titanic_router is not None:
        LOGGING_MIDDLEWARE_AVAILABLE = True
        print(f"✅ 타이타닉 라우터 import 성공: {titanic_router.prefix}")
    else:
        raise ImportError("titanic_router가 None입니다")
    
    if seoul_crime_router is not None:
        print(f"✅ 서울 범죄 라우터 import 성공: {seoul_crime_router.prefix}")
    else:
        print("⚠️ seoul_crime_router가 None입니다 (선택적)")
    
    if nlp_router is not None:
        print(f"✅ NLP 라우터 import 성공: {nlp_router.prefix}")
    else:
        print("⚠️ nlp_router가 None입니다 (선택적)")
        
except ImportError as e:
    # 모듈을 찾을 수 없는 경우 기본값 사용
    import logging
    from fastapi import APIRouter
    titanic_router = APIRouter(prefix="/titanic")
    seoul_crime_router = None
    nlp_router = None
    LoggingMiddleware = None
    LOGGING_MIDDLEWARE_AVAILABLE = False
    print(f"❌ Import 실패, 기본 라우터 사용: {str(e)}")
    def setup_logging(name):
        return logging.getLogger(name)

# 로깅 설정
logger = setup_logging(config.service_name)

# FastAPI 앱 생성
app = FastAPI(
    title="Titanic Service API",
    description="""
    ## 타이타닉 데이터 서비스 API
    
    머신러닝을 활용한 타이타닉 승객 데이터 분석 및 생존 예측 서비스입니다.
    
    ### 주요 기능
    - 승객 데이터 조회 및 통계 분석
    - 머신러닝 모델 훈련 (Random Forest)
    - 승객 생존 예측
    - 배치 예측 지원
    
    ### 기술 스택
    - **Framework**: FastAPI
    - **ML Library**: scikit-learn, pandas, numpy
    - **Model**: Random Forest Classifier
    
    ### API 문서
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI Schema: `/openapi.json`
    """,
    version=config.service_version,
    contact={
        "name": "ML Service Team",
        "email": "support@labzang.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 관련 API",
        },
    ],
    openapi_tags=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 및 머신러닝 예측 기능",
        },
    ],
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어 추가 (LoggingMiddleware가 올바르게 import되었는지 확인)
if LOGGING_MIDDLEWARE_AVAILABLE and LoggingMiddleware is not None:
    try:
        app.add_middleware(LoggingMiddleware)
        logger.info("LoggingMiddleware가 성공적으로 추가되었습니다.")
    except Exception as e:
        logger.warning(f"미들웨어 추가 중 오류 발생: {str(e)}. 미들웨어를 건너뜁니다.")
else:
    logger.warning("LoggingMiddleware를 사용할 수 없습니다. 미들웨어를 건너뜁니다.")

# 라우터 등록
try:
    if titanic_router is not None:
        app.include_router(titanic_router)
        logger.info(f"✅ 타이타닉 라우터가 성공적으로 등록되었습니다. (prefix: {titanic_router.prefix})")
        # 등록된 라우트 확인
        titanic_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if '/titanic' in route.path:
                    titanic_routes.append(f"{list(route.methods)} {route.path}")
                    logger.info(f"  - 등록된 라우트: {list(route.methods)} {route.path}")
        
        if not titanic_routes:
            logger.warning("⚠️ /titanic 경로의 라우트가 등록되지 않았습니다!")
        else:
            logger.info(f"✅ 총 {len(titanic_routes)}개의 타이타닉 라우트가 등록되었습니다.")
    else:
        logger.error("❌ 타이타닉 라우터가 None입니다. import에 실패했을 수 있습니다.")
        # 대체 라우터 생성
        from fastapi import APIRouter
        titanic_router = APIRouter(prefix="/titanic")
        app.include_router(titanic_router)
        logger.warning("⚠️ 빈 라우터를 등록했습니다. 엔드포인트가 작동하지 않을 수 있습니다.")
except Exception as e:
    logger.error(f"❌ 타이타닉 라우터 등록 중 오류 발생: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    # 최소한 빈 라우터라도 등록
    try:
        from fastapi import APIRouter
        fallback_router = APIRouter(prefix="/titanic")
        app.include_router(fallback_router)
        logger.warning("⚠️ 대체 라우터를 등록했습니다.")
    except:
        pass

# 서울 범죄 라우터 등록
try:
    if seoul_crime_router is not None:
        app.include_router(seoul_crime_router)
        logger.info(f"✅ 서울 범죄 라우터가 성공적으로 등록되었습니다. (prefix: {seoul_crime_router.prefix})")
        # 등록된 라우트 확인
        seoul_crime_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if '/seoul_crime' in route.path:
                    seoul_crime_routes.append(f"{list(route.methods)} {route.path}")
                    logger.info(f"  - 등록된 라우트: {list(route.methods)} {route.path}")
        
        if not seoul_crime_routes:
            logger.warning("⚠️ /seoul_crime 경로의 라우트가 등록되지 않았습니다!")
        else:
            logger.info(f"✅ 총 {len(seoul_crime_routes)}개의 서울 범죄 라우트가 등록되었습니다.")
    else:
        logger.warning("⚠️ 서울 범죄 라우터가 None입니다. import에 실패했을 수 있습니다.")
except Exception as e:
    logger.error(f"❌ 서울 범죄 라우터 등록 중 오류 발생: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# NLP 라우터 등록
try:
    if nlp_router is not None:
        app.include_router(nlp_router)
        logger.info(f"✅ NLP 라우터가 성공적으로 등록되었습니다. (prefix: {nlp_router.prefix})")
        # 등록된 라우트 확인
        nlp_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if '/nlp' in route.path:
                    nlp_routes.append(f"{list(route.methods)} {route.path}")
                    logger.info(f"  - 등록된 라우트: {list(route.methods)} {route.path}")
        
        if not nlp_routes:
            logger.warning("⚠️ /nlp 경로의 라우트가 등록되지 않았습니다!")
        else:
            logger.info(f"✅ 총 {len(nlp_routes)}개의 NLP 라우트가 등록되었습니다.")
    else:
        logger.warning("⚠️ NLP 라우터가 None입니다. import에 실패했을 수 있습니다.")
except Exception as e:
    logger.error(f"❌ NLP 라우터 등록 중 오류 발생: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# 정적 파일 서빙 (히트맵 HTML 파일)
try:
    # save 디렉토리 경로 설정
    current_file = Path(__file__).resolve()
    if str(current_file).startswith("/app"):
        # Docker 환경 - 실제 파일 위치 확인
        # 볼륨 마운트로 인해 /app/app/seoul_crime/save 구조
        save_dir = Path("/app/app/seoul_crime/save")
        if not save_dir.exists():
            # 대체 경로 시도
            save_dir = Path("/app/app/ml_service/app/seoul_crime/save")
    else:
        # 로컬 환경
        save_dir = current_file.parent / "app" / "ml_service" / "app" / "seoul_crime" / "save"
    
    # 디렉토리가 존재하면 마운트
    if save_dir.exists():
        app.mount("/static/heatmap", StaticFiles(directory=str(save_dir)), name="heatmap")
        logger.info(f"✅ 히트맵 정적 파일 서빙 활성화: /static/heatmap -> {save_dir}")
    else:
        # 디렉토리가 없으면 생성
        save_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/static/heatmap", StaticFiles(directory=str(save_dir)), name="heatmap")
        logger.info(f"✅ 히트맵 디렉토리 생성 및 정적 파일 서빙 활성화: /static/heatmap -> {save_dir}")
except Exception as e:
    logger.warning(f"⚠️ 정적 파일 서빙 설정 중 오류 발생: {str(e)}")

# 전역 예외 핸들러 추가
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    import traceback
    logger.error(f"예상치 못한 오류 발생: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if logger.level <= logging.DEBUG else "서버 내부 오류가 발생했습니다.",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

# CSV 파일 경로 (Docker 환경에서는 app/titanic/train.csv)
CSV_FILE_PATH = Path(__file__).parent / "app" / "titanic" / "train.csv"
if not CSV_FILE_PATH.exists():
    # 로컬 환경에서의 경로 시도
    CSV_FILE_PATH = Path(__file__).parent / "app" / "ml_service" / "app" / "titanic" / "train.csv"


def load_top_10_passengers():
    """train.csv에서 상위 10명의 승객 정보를 로드"""
    passengers = []
    
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 10:  # 상위 10명만
                    break
                passengers.append({
                    "PassengerId": row.get("PassengerId", ""),
                    "Survived": row.get("Survived", ""),
                    "Pclass": row.get("Pclass", ""),
                    "Name": row.get("Name", ""),
                    "Sex": row.get("Sex", ""),
                    "Age": row.get("Age", ""),
                    "SibSp": row.get("SibSp", ""),
                    "Parch": row.get("Parch", ""),
                    "Ticket": row.get("Ticket", ""),
                    "Fare": row.get("Fare", ""),
                    "Cabin": row.get("Cabin", ""),
                    "Embarked": row.get("Embarked", "")
                })
    except FileNotFoundError:
        logger.error(f"CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return []
    except Exception as e:
        logger.error(f"CSV 파일 읽기 오류: {e}")
        return []
    
    return passengers


@app.get("/")
async def root():
    """루트 엔드포인트"""
    # 등록된 라우트 확인
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else []
            })
    
    return {
        "service": config.service_name,
        "version": config.service_version,
        "message": "ML Service API",
        "registered_routes": routes,
        "titanic_routes": [r for r in routes if '/titanic' in r['path']],
        "seoul_crime_routes": [r for r in routes if '/seoul_crime' in r['path']]
    }


@app.get("/passengers/top10")
async def get_top_10_passengers():
    """상위 10명의 승객 정보를 반환"""
    passengers = load_top_10_passengers()
    
    if not passengers:
        return JSONResponse(
            status_code=404,
            content={"error": "승객 데이터를 찾을 수 없습니다."}
        )
    
    return {
        "count": len(passengers),
        "passengers": passengers
    }


@app.get("/passengers/top10/print")
async def print_top_10_passengers():
    """상위 10명의 승객 정보를 터미널에 출력"""
    passengers = load_top_10_passengers()
    
    if not passengers:
        logger.warning("출력할 승객 데이터가 없습니다.")
        return {"message": "출력할 승객 데이터가 없습니다."}
    
    # 터미널에 출력
    print("\n" + "="*80)
    print("타이타닉 승객 상위 10명")
    print("="*80)
    
    for i, passenger in enumerate(passengers, 1):
        print(f"\n[{i}] {passenger['Name']}")
        print(f"    PassengerId: {passenger['PassengerId']}")
        print(f"    Survived: {passenger['Survived']} ({'생존' if passenger['Survived'] == '1' else '사망'})")
        print(f"    Pclass: {passenger['Pclass']}")
        print(f"    Sex: {passenger['Sex']}")
        print(f"    Age: {passenger['Age']}")
        print(f"    Fare: {passenger['Fare']}")
        print(f"    Embarked: {passenger['Embarked']}")
    
    print("\n" + "="*80)
    logger.info(f"상위 10명의 승객 정보를 터미널에 출력했습니다.")
    
    return {
        "message": "상위 10명의 승객 정보를 터미널에 출력했습니다.",
        "count": len(passengers)
    }


@app.get("/passengers/all")
async def get_all_passengers():
    """전체 승객 데이터 반환"""
    passengers = load_all_passengers()
    
    if not passengers:
        return JSONResponse(
            status_code=404,
            content={"error": "승객 데이터를 찾을 수 없습니다."}
        )
    
    return {
        "count": len(passengers),
        "passengers": passengers
    }


@app.get("/passengers/all/print")
async def print_all_passengers_endpoint():
    """전체 승객 데이터를 터미널에 출력"""
    print_all_passengers()
    
    passengers = load_all_passengers()
    return {
        "message": f"전체 {len(passengers)}명의 승객 정보를 터미널에 출력했습니다.",
        "count": len(passengers)
    }


def load_all_passengers():
    """전체 승객 데이터 로드"""
    passengers = []
    
    try:
        import pandas as pd
        df = pd.read_csv(CSV_FILE_PATH)
        
        # 전체 데이터를 딕셔너리 리스트로 변환
        for _, row in df.iterrows():
            passengers.append({
                "PassengerId": str(row.get("PassengerId", "")),
                "Survived": str(row.get("Survived", "")),
                "Pclass": str(row.get("Pclass", "")),
                "Name": str(row.get("Name", "")),
                "Sex": str(row.get("Sex", "")),
                "Age": str(row.get("Age", "")) if pd.notna(row.get("Age")) else "",
                "SibSp": str(row.get("SibSp", "")),
                "Parch": str(row.get("Parch", "")),
                "Ticket": str(row.get("Ticket", "")),
                "Fare": str(row.get("Fare", "")) if pd.notna(row.get("Fare")) else "",
                "Cabin": str(row.get("Cabin", "")) if pd.notna(row.get("Cabin")) else "",
                "Embarked": str(row.get("Embarked", "")) if pd.notna(row.get("Embarked")) else ""
            })
    except FileNotFoundError:
        logger.error(f"CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return []
    except Exception as e:
        logger.error(f"CSV 파일 읽기 오류: {e}")
        return []
    
    return passengers


def load_all_passengers_summary():
    """전체 승객 데이터 요약 정보 로드"""
    try:
        import pandas as pd
        df = pd.read_csv(CSV_FILE_PATH)
        
        total_count = len(df)
        survived_count = int(df['Survived'].sum()) if 'Survived' in df.columns else 0
        survival_rate = (survived_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_count": total_count,
            "survived_count": survived_count,
            "died_count": total_count - survived_count,
            "survival_rate": round(survival_rate, 2),
            "columns": df.columns.tolist()
        }
    except FileNotFoundError:
        logger.error(f"CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return None
    except Exception as e:
        logger.error(f"CSV 파일 읽기 오류: {e}")
        return None


def print_all_passengers():
    """전체 승객 데이터를 터미널에 출력"""
    passengers = load_all_passengers()
    
    if not passengers:
        logger.warning("출력할 승객 데이터가 없습니다.")
        return
    
    # 터미널에 출력
    print("\n" + "="*80)
    print(f"타이타닉 승객 전체 데이터 ({len(passengers)}명)")
    print("="*80)
    
    for i, passenger in enumerate(passengers, 1):
        print(f"\n[{i}] {passenger['Name']}")
        print(f"    PassengerId: {passenger['PassengerId']}")
        print(f"    Survived: {passenger['Survived']} ({'생존' if passenger['Survived'] == '1' else '사망'})")
        print(f"    Pclass: {passenger['Pclass']}")
        print(f"    Sex: {passenger['Sex']}")
        print(f"    Age: {passenger['Age']}")
        print(f"    Fare: {passenger['Fare']}")
        print(f"    Embarked: {passenger['Embarked']}")
    
    print("\n" + "="*80)
    logger.info(f"전체 {len(passengers)}명의 승객 정보를 터미널에 출력했습니다.")


@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info(f"{config.service_name} v{config.service_version} started")
    
    # 전체 데이터 요약 정보 출력
    summary = load_all_passengers_summary()
    if summary:
        print("\n" + "="*80)
        print("타이타닉 데이터셋 전체 요약")
        print("="*80)
        print(f"전체 승객 수: {summary['total_count']}명")
        print(f"생존자: {summary['survived_count']}명 ({summary['survival_rate']}%)")
        print(f"사망자: {summary['died_count']}명 ({100 - summary['survival_rate']:.2f}%)")
        print(f"컬럼 수: {len(summary['columns'])}개")
        print(f"컬럼 목록: {', '.join(summary['columns'])}")
        print("="*80)
        logger.info(f"전체 {summary['total_count']}명의 승객 데이터가 로드되었습니다.")
        
        # 전체 데이터 출력 (요약만 출력, 전체 리스트는 너무 길 수 있으므로)
        # 전체 데이터를 보려면 GET /passengers/all 엔드포인트 사용
    else:
        logger.warning("데이터 요약 정보를 로드할 수 없습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info(f"{config.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)