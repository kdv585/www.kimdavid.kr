"""
타이타닉 머신러닝 모델 클래스
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
import logging
import joblib

logger = logging.getLogger(__name__)
from pathlib import Path
import sys

# 공통 모듈 경로 추가
current_file = Path(__file__).resolve()
ai_server_path = current_file.parent.parent.parent.parent.parent
if ai_server_path.exists() and str(ai_server_path) not in sys.path:
    sys.path.insert(0, str(ai_server_path))


class TitanicModels:
    """타이타닉 생존 예측 머신러닝 모델"""
    
    def __init__(self):
        self.model = None
        self.model_path = Path(__file__).parent / "titanic_model.pkl"
        self.feature_columns = None
        self.is_trained = False
    
    def create_model(self, n_estimators: int = 100, max_depth: int = 10, random_state: int = 42):
        """
        Random Forest 모델 생성
        
        Args:
            n_estimators: 트리 개수
            max_depth: 최대 깊이
            random_state: 랜덤 시드
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        logger.info(f"✅ Random Forest 모델 생성 완료 (n_estimators={n_estimators}, max_depth={max_depth})")
        return self.model
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        모델 학습
        
        Args:
            X_train: 훈련 데이터 (피처)
            y_train: 훈련 데이터 (라벨)
        """
        if self.model is None:
            self.create_model()
        
        # 피처 컬럼 저장 (예측 시 동일한 컬럼 순서 보장)
        self.feature_columns = X_train.columns.tolist()
        
        logger.info(f"📊 학습 데이터 크기: {X_train.shape}")
        logger.info(f"📊 피처 컬럼: {self.feature_columns}")
        
        # 모델 학습
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        logger.info("✅ 모델 학습 완료")
        return self.model
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        예측 수행
        
        Args:
            X: 예측할 데이터
            
        Returns:
            예측 결과 (0: 사망, 1: 생존)
        """
        if not self.is_trained or self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train() 메서드를 먼저 호출하세요.")
        
        # 피처 컬럼 순서 맞추기
        if self.feature_columns:
            missing_cols = set(self.feature_columns) - set(X.columns)
            if missing_cols:
                logger.warning(f"⚠️ 누락된 컬럼: {missing_cols}")
                for col in missing_cols:
                    X[col] = 0  # 기본값 0으로 채우기
            
            X = X[self.feature_columns]
        
        predictions = self.model.predict(X)
        logger.info(f"✅ 예측 완료: {len(predictions)}개 샘플")
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        예측 확률 반환
        
        Args:
            X: 예측할 데이터
            
        Returns:
            예측 확률 (각 클래스별 확률)
        """
        if not self.is_trained or self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train() 메서드를 먼저 호출하세요.")
        
        # 피처 컬럼 순서 맞추기
        if self.feature_columns:
            missing_cols = set(self.feature_columns) - set(X.columns)
            if missing_cols:
                for col in missing_cols:
                    X[col] = 0
            
            X = X[self.feature_columns]
        
        probabilities = self.model.predict_proba(X)
        return probabilities
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """
        모델 평가
        
        Args:
            X_test: 테스트 데이터 (피처)
            y_test: 테스트 데이터 (라벨)
            
        Returns:
            평가 지표 딕셔너리
        """
        if not self.is_trained or self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train() 메서드를 먼저 호출하세요.")
        
        # 예측
        y_pred = self.predict(X_test)
        
        # 평가 지표 계산
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # 혼동 행렬
        cm = confusion_matrix(y_test, y_pred)
        
        # 분류 리포트
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # 피처 중요도
        feature_importance = None
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        results = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "feature_importance": feature_importance
        }
        
        logger.info(f"📊 모델 평가 결과:")
        logger.info(f"  - 정확도 (Accuracy): {accuracy:.4f}")
        logger.info(f"  - 정밀도 (Precision): {precision:.4f}")
        logger.info(f"  - 재현율 (Recall): {recall:.4f}")
        logger.info(f"  - F1 점수: {f1:.4f}")
        
        return results
    
    def save_model(self, file_path: str = None):
        """모델 저장"""
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다.")
        
        if file_path is None:
            file_path = self.model_path
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, file_path)
        logger.info(f"✅ 모델 저장 완료: {file_path}")
    
    def load_model(self, file_path: str = None):
        """모델 로드"""
        if file_path is None:
            file_path = self.model_path
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {file_path}")
        
        model_data = joblib.load(file_path)
        self.model = model_data['model']
        self.feature_columns = model_data.get('feature_columns')
        self.is_trained = model_data.get('is_trained', True)
        
        logger.info(f"✅ 모델 로드 완료: {file_path}")
    