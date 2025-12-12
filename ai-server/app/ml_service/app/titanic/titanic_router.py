"""
타이타닉 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# 공통 모듈 경로 추가
# titanic_router.py 위치: ai-server/app/ml_service/app/titanic/titanic_router.py
# Docker 환경: /app/app/titanic/titanic_router.py
current_file = Path(__file__).resolve()

# Docker 환경 확인 및 import 경로 설정
if str(current_file).startswith("/app"):
    # Docker 환경: /app/app/titanic/ 또는 /app/app/ml_service/app/titanic/
    base_path = Path("/app")
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))
    
    # 여러 경로 시도
    imported = False
    try:
        from app.titanic.titanic_service import TitanicService
        from app.common.utils import create_response, create_error_response
        imported = True
        print("✅ Docker 환경: app.titanic 경로로 import 성공")
    except ImportError as e1:
        print(f"⚠️ app.titanic 경로 import 실패: {e1}")
        try:
            from app.ml_service.app.titanic.titanic_service import TitanicService
            from app.ml_service.common.utils import create_response, create_error_response
            imported = True
            print("✅ Docker 환경: app.ml_service.app.titanic 경로로 import 성공")
        except ImportError as e2:
            print(f"⚠️ app.ml_service.app.titanic 경로 import 실패: {e2}")
            # 직접 경로로 import 시도
            try:
                import importlib.util
                service_path = Path("/app/app/titanic/titanic_service.py")
                if not service_path.exists():
                    service_path = Path("/app/app/ml_service/app/titanic/titanic_service.py")
                
                if service_path.exists():
                    spec = importlib.util.spec_from_file_location("titanic_service", service_path)
                    titanic_service_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(titanic_service_module)
                    TitanicService = titanic_service_module.TitanicService
                    
                    utils_path = Path("/app/common/utils.py")
                    if not utils_path.exists():
                        utils_path = Path("/app/app/ml_service/common/utils.py")
                    if utils_path.exists():
                        spec = importlib.util.spec_from_file_location("utils", utils_path)
                        utils_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(utils_module)
                        create_response = utils_module.create_response
                        create_error_response = utils_module.create_error_response
                        imported = True
                        print("✅ 직접 경로로 import 성공")
            except Exception as e3:
                print(f"❌ 모든 import 시도 실패: {e3}")
                raise ImportError(f"모든 import 경로 실패: {e1}, {e2}, {e3}")
    
    if not imported:
        raise ImportError("TitanicService를 import할 수 없습니다.")
else:
    # 로컬 환경
    ai_server_path = current_file.parent.parent.parent.parent.parent
    if ai_server_path.exists() and str(ai_server_path) not in sys.path:
        sys.path.insert(0, str(ai_server_path))
    try:
        from app.ml_service.app.titanic.titanic_service import TitanicService
        from app.ml_service.common.utils import create_response, create_error_response
        print("✅ 로컬 환경: app.ml_service.app.titanic 경로로 import 성공")
    except ImportError as e:
        print(f"⚠️ 로컬 환경 import 실패: {e}")
        raise

router = APIRouter(prefix="/titanic", tags=["titanic"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[TitanicService] = None


def get_service() -> TitanicService:
    """TitanicService 싱글톤 인스턴스 반환"""
    global _service_instance
    try:
        if _service_instance is None:
            _service_instance = TitanicService()
        return _service_instance
    except Exception as e:
        import traceback
        error_msg = f"서비스 인스턴스 생성 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get("/")
@router.post("/")  # POST도 지원 (요청 정보 확인용)
async def titanic_root():
    """타이타닉 서비스 루트"""
    try:
        return create_response(
            data={
                "service": "mlservice",
                "module": "titanic",
                "status": "running",
                "available_endpoints": [
                    "GET /titanic/ - 서비스 상태 확인",
                    "GET /titanic/analyze - 트레인 데이터 분석",
                    "POST /titanic/preprocess - 데이터 전처리",
                    "POST /titanic/modeling - 모델 생성",
                    "POST /titanic/learning - 모델 학습",
                    "POST /titanic/evaluate - 모델 평가",
                    "POST /titanic/predict - 단일 예측",
                    "POST /titanic/predict/batch - 배치 예측",
                    "POST /titanic/predict-batch - 배치 예측 (하이픈 버전)",
                    "POST /titanic/submit - 제출 파일 생성",
                    "POST /titanic/pipeline - 전체 파이프라인 실행"
                ]
            },
        message="Titanic Service is running"
    )
    except Exception as e:
        from app.ml_service.common.utils import create_error_response
        raise HTTPException(
            status_code=500,
            detail=f"서비스 초기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/preprocess")
async def run_preprocess():
    """
    타이타닉 데이터 전처리 실행
    
    - 데이터 로드 및 기본 정보 확인
    - 불필요한 피처 제거 (SibSp, Parch, Ticket, Cabin)
    - Pclass ordinal 변환
    - Fare ordinal 변환
    - Embarked one-hot encoding
    - Gender one-hot encoding
    - Age ratio 구간화
    - Title 추출 및 one-hot encoding
    - Name 컬럼 제거
    """
    try:
        service = get_service()
        service.preprocess()
        
        return create_response(
            data={
                "status": "completed",
                "message": "데이터 전처리가 완료되었습니다."
            },
            message="Preprocessing completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/modeling")
async def run_modeling():
    """
    머신러닝 모델 생성
    
    - Random Forest 모델 생성
    - 하이퍼파라미터 설정
    """
    try:
        service = get_service()
        model = service.modeling()
        
        return create_response(
            data={
                "status": "completed",
                "message": "모델 생성이 완료되었습니다.",
                "model_type": "RandomForestClassifier"
            },
            message="Modeling completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/learning")
async def run_learning():
    """
    머신러닝 모델 학습
    
    - 전처리된 데이터로 모델 학습
    - 훈련/검증 데이터 분할
    - 모델 훈련 수행
    """
    try:
        service = get_service()
        model = service.learning()
        
        return create_response(
            data={
                "status": "completed",
                "message": "모델 학습이 완료되었습니다.",
                "is_trained": hasattr(model, 'is_trained') and model.is_trained if model else False
            },
            message="Learning completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 학습 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/evaluate")
async def run_evaluate():
    """
    머신러닝 모델 평가
    
    - 검증 데이터로 모델 성능 평가
    - 정확도, 정밀도, 재현율, F1 점수 계산
    - 혼동 행렬 및 분류 리포트 생성
    - 피처 중요도 분석
    """
    try:
        service = get_service()
        results = service.evaluate()
        
        return create_response(
            data={
                "status": "completed",
                "message": "모델 평가가 완료되었습니다.",
                "metrics": {
                    "accuracy": results["accuracy"],
                    "precision": results["precision"],
                    "recall": results["recall"],
                    "f1_score": results["f1_score"]
                },
                "confusion_matrix": results["confusion_matrix"],
                "feature_importance": results["feature_importance"]
            },
            message="Evaluation completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 평가 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/predict")
async def predict_survival(passenger: Dict[str, Any] = Body(...)):
    """
    생존 예측 (단일 승객)
    
    승객 정보를 받아 생존 여부를 예측합니다.
    
    **요청 예시:**
    ```json
    {
        "Pclass": 1,
        "Name": "Braund, Mr. Owen Harris",
        "Sex": "male",
        "Age": 22,
        "Fare": 7.25,
        "Embarked": "S"
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "prediction": 0,
        "survived": false,
        "probability": {
            "died": 0.85,
            "survived": 0.15
        }
    }
    ```
    """
    try:
        service = get_service()
        result = service.predict(passenger_data=passenger)
        
        return create_response(
            data=result,
            message="예측이 완료되었습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"예측 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/predict/batch")
@router.post("/predict-batch")  # 하이픈 버전도 지원
async def predict_survival_batch(passengers: List[Dict[str, Any]] = Body(...)):
    """
    생존 예측 (배치)
    
    여러 승객 정보를 받아 생존 여부를 일괄 예측합니다.
    
    **엔드포인트:**
    - `/titanic/predict/batch` (슬래시 버전)
    - `/titanic/predict-batch` (하이픈 버전)
    
    **요청 예시:**
    ```json
    [
        {
            "Pclass": 1,
            "Name": "Braund, Mr. Owen Harris",
            "Sex": "male",
            "Age": 22,
            "Fare": 7.25,
            "Embarked": "S"
        },
        {
            "Pclass": 3,
            "Name": "Heikkinen, Miss. Laina",
            "Sex": "female",
            "Age": 26,
            "Fare": 7.925,
            "Embarked": "S"
        }
    ]
    ```
    """
    try:
        import pandas as pd
        service = get_service()
        
        # 리스트를 DataFrame으로 변환
        df = pd.DataFrame(passengers)
        results = service.predict(X=df)
        
        return create_response(
            data={
                "count": len(results),
                "predictions": results
            },
            message=f"{len(results)}명의 승객에 대한 예측이 완료되었습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"배치 예측 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/submit")
async def run_submit():
    """
    제출 파일 생성
    
    - 테스트 데이터에 대한 예측 수행
    - submission.csv 파일 생성
    """
    try:
        service = get_service()
        submission = service.submit()
        
        return create_response(
            data={
                "status": "completed",
                "message": "제출 파일이 생성되었습니다.",
                "row_count": len(submission)
            },
            message="Submission file created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"제출 파일 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/analyze")
async def analyze_train_data():
    """
    트레인 데이터 분석 결과 조회
    
    - 기본 통계 정보 (행 수, 열 수)
    - 생존자/사망자 분포
    - 각 피처별 통계 (Pclass, Sex, Age, Fare 등)
    - 결측치 정보
    - Pclass별 생존률
    - 성별별 생존률
    - 나이 구간별 생존률
    """
    try:
        service = get_service()
        analysis_result = service.analyze_train_data()
        
        return create_response(
            data=analysis_result,
            message="트레인 데이터 분석이 완료되었습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/data/all")
async def get_all_train_data():
    """
    전체 트레인 데이터 조회
    
    train.csv의 모든 승객 데이터를 반환합니다.
    """
    try:
        import pandas as pd
        service = get_service()
        
        # 전체 데이터 로드
        train_csv_path = service._get_csv_path('train.csv')
        df_train = pd.read_csv(train_csv_path)
        
        # DataFrame을 딕셔너리 리스트로 변환
        passengers = df_train.to_dict('records')
        
        return create_response(
            data={
                "total_count": len(passengers),
                "columns": df_train.columns.tolist(),
                "passengers": passengers
            },
            message=f"전체 {len(passengers)}명의 승객 데이터를 반환했습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/data/preprocessed")
async def get_preprocessed_data():
    """
    전처리된 데이터 조회
    
    전처리가 완료된 트레인 데이터를 반환합니다.
    전처리를 먼저 실행해야 합니다.
    """
    try:
        import pandas as pd
        service = get_service()
        
        if service.processed_data is None or service.processed_data.train is None:
            raise HTTPException(
                status_code=400,
                detail="전처리된 데이터가 없습니다. 먼저 POST /titanic/preprocess를 실행하세요."
            )
        
        # 전처리된 데이터를 딕셔너리 리스트로 변환
        processed_data = service.processed_data.train.to_dict('records')
        
        return create_response(
            data={
                "total_count": len(processed_data),
                "columns": service.processed_data.train.columns.tolist(),
                "data": processed_data
            },
            message=f"전처리된 {len(processed_data)}개의 데이터를 반환했습니다."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리된 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/pipeline")
async def get_pipeline_info():
    """
    파이프라인 정보 조회 (GET)
    
    파이프라인 실행 방법과 단계를 안내합니다.
    """
    return create_response(
        data={
            "message": "파이프라인을 실행하려면 POST 메서드를 사용하세요.",
            "method": "POST",
            "endpoint": "/titanic/pipeline",
            "description": "전처리 → 모델 생성 → 학습 → 평가 → 제출 파일 생성까지 한 번에 실행합니다.",
            "steps": [
                "1. 전처리 (preprocess)",
                "2. 모델 생성 (modeling)",
                "3. 학습 (learning)",
                "4. 평가 (evaluate)",
                "5. 제출 파일 생성 (submit)"
            ]
        },
        message="파이프라인 정보"
    )


@router.post("/pipeline")
async def run_full_pipeline():
    """
    전체 ML 파이프라인 실행 (POST)
    
    전처리 → 모델 생성 → 학습 → 평가 → 제출 파일 생성까지 한 번에 실행합니다.
    """
    try:
        service = get_service()
        
        # 1. 전처리
        service.preprocess()
        
        # 2. 모델 생성
        service.modeling()
        
        # 3. 학습
        service.learning()
        
        # 4. 평가
        evaluation_results = service.evaluate()
        
        # 5. 제출 파일 생성
        submission = service.submit()
        
        return create_response(
            data={
                "status": "completed",
                "message": "전체 ML 파이프라인이 완료되었습니다.",
                "evaluation": {
                    "accuracy": evaluation_results["accuracy"],
                    "precision": evaluation_results["precision"],
                    "recall": evaluation_results["recall"],
                    "f1_score": evaluation_results["f1_score"]
                },
                "all_model_accuracies": evaluation_results.get("accuracies", {}),
                "submission": {
                    "row_count": len(submission)
                }
            },
            message="Full pipeline completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파이프라인 실행 중 오류가 발생했습니다: {str(e)}"
        )