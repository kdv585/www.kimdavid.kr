"""
타이타닉 데이터 서비스
판다스, 넘파이, 사이킷런을 사용한 데이터 처리 및 머신러닝 서비스
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any, ParamSpecArgs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
import logging
from app.titanic.titanic_method import TitanicMethod

logger = logging.getLogger(__name__)
from app.titanic.titanic_dataset import TitanicDataSet
from app.titanic.titanic_model import TitanicModels

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TitanicService:
    """타이타닉 데이터 처리 및 머신러닝 서비스"""
    
    def __init__(self):
        # CSV 파일 경로 설정 (app/titanic/ 디렉토리)
        current_file = Path(__file__).resolve()
        # app/titanic/titanic_service.py -> app/titanic/
        titanic_dir = current_file.parent
        self.train_csv_path = titanic_dir / "train.csv"
        self.test_csv_path = titanic_dir / "test.csv"
        
        # 전처리된 데이터 저장
        self.processed_data = None
        self.y_train = None
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train_split = None
        self.y_test_split = None
    
    def _get_csv_path(self, filename: str) -> Path:
        """
        CSV 파일의 전체 경로를 반환
        Args:
            filename: CSV 파일명 (train.csv 또는 test.csv)
        Returns:
            CSV 파일의 Path 객체
        """
        if filename == "train.csv":
            return self.train_csv_path
        elif filename == "test.csv":
            return self.test_csv_path
        else:
            # 기본적으로 app/titanic 폴더에서 찾기
            current_file = Path(__file__).resolve()
            titanic_dir = current_file.parent
            return titanic_dir / filename

    def preprocess(self) -> Dict[str, Any]:
        """
        타이타닉 데이터 전처리 실행
        Returns:
            전처리 결과 정보 딕셔너리
        """
        logger.info("😎😎 전처리 시작")
        the_method = TitanicMethod()

        train_csv_path = self._get_csv_path('train.csv')
        df_train = the_method.read_csv(str(train_csv_path))
        this_train = the_method.create_df(df_train, 'Survived')
        logger.info(f'1. Train 의 type: {type(this_train)}')
        logger.info(f'2. Train 의 column: {list(this_train.columns)}')
        print('\n' + '='*80)
        print('3. Train 의 상위 5개 행:')
        print('='*80)
        print(this_train.head(5).to_string())
        print('='*80 + '\n')
        logger.info(f'4. Train 의 null 의 갯수: {the_method.check_null(this_train)}개')

        test_csv_path = self._get_csv_path('test.csv')
        df_test = the_method.read_csv(str(test_csv_path))
        this_test = the_method.create_df(df_test, 'Survived')
        logger.info(f'1. Test 의 type: {type(this_test)}')
        logger.info(f'2. Test 의 column: {list(this_test.columns)}')
        print('\n' + '='*80)
        print('3. Test 의 상위 5개 행:')
        print('='*80)
        print(this_test.head(5).to_string())
        print('='*80 + '\n')
        logger.info(f'4. Test 의 null 의 갯수: {the_method.check_null(this_test)}개')
        
        this = TitanicDataSet()

        this.train = this_train
        this.test = this_test

        drop_features = ['SibSp', 'Parch', 'Cabin', 'Ticket']
        this = the_method.drop_feature(this, *drop_features)
        this = the_method.pclass_ordinal(this)
        this = the_method.gender_nominal(this)
        this = the_method.extract_title_from_name(this)  # Name에서 Title 추출
        this = the_method.title_nominal(this)
        this = the_method.age_ratio(this)
        this = the_method.fare_ordinal(this)
        this = the_method.embarked_ordinal(this)
        drop_name = ['Name', 'Sex', 'Age', 'Fare']  # 원본 컬럼 제거
        this = the_method.drop_feature(this, *drop_name)
        
        # 전처리된 데이터 저장
        self.processed_data = this
        self.y_train = the_method.create_label(df_train, 'Survived')

        logger.info("😎😎😎 트레인 전처리 완료")
        logger.info(f'1. Train 의 type: {type(this.train)}')
        logger.info(f'2. Train 의 column: {list(this.train.columns)}')
        print('\n' + '='*80)
        print('3. Train 의 상위 5개 행 (전처리 후):')
        print('='*80)
        print(this.train.head(5).to_string())
        print('='*80 + '\n')
        logger.info(f'4. Train 의 null 의 갯수: {the_method.check_null(this)}개')

        logger.info("👽👽👽 테스트 전처리 완료")
        logger.info(f'1. Test 의 type: {type(this.test)}')
        logger.info(f'2. Test 의 column: {list(this.test.columns)}')
        print('\n' + '='*80)
        print('3. Test 의 상위 5개 행 (전처리 후):')
        print('='*80)
        print(this.test.head(5).to_string())
        print('='*80 + '\n')
        logger.info(f'4. Test 의 null 의 갯수: {the_method.check_null(this)}개')
        
        # 전처리 결과 정보 반환
        return {
            "status": "success",
            "train_rows": len(this.train),
            "test_rows": len(this.test),
            "columns": this.train.columns.tolist(),
            "column_count": len(this.train.columns),
            "null_count": the_method.check_null(this),
            "sample_data": this.train.head(5).to_dict(orient="records"),
            "dtypes": this.train.dtypes.astype(str).to_dict()
        }
        
    def modeling(self):
        """모델 생성"""
        logger.info("😎😎 모델링 시작")
        
        if self.processed_data is None:
            raise ValueError("전처리된 데이터가 없습니다. preprocess()를 먼저 실행하세요.")
        
        # 모델 생성
        self.model = TitanicModels()
        self.model.create_model(n_estimators=100, max_depth=10, random_state=42)
        
        logger.info("😎😎 모델링 완료")
        return self.model

    def create_k_fold(self):
        """K-Fold 교차 검증 생성"""
        k_fold = KFold(n_splits=10, shuffle=True, random_state=0)
        return k_fold
    
    def accuracy_by_logistic_regression(self, model, dummy):
        """로지스틱 회귀 K-Fold 교차 검증"""
        logger.info(">>> 로지스틱 회귀 방식 검증")
        k_fold = self.create_k_fold()
        clf = LogisticRegression(random_state=42, max_iter=1000)
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_knn(self, model, dummy):
        """KNN K-Fold 교차 검증"""
        logger.info(">>> KNN 방식 검증")
        clf = KNeighborsClassifier(n_neighbors=13)
        scoring = 'accuracy'
        k_fold = self.create_k_fold()
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_dtree(self, model, dummy):
        """결정트리 K-Fold 교차 검증"""
        logger.info(">>> 결정트리 방식 검증")
        k_fold = self.create_k_fold()
        clf = DecisionTreeClassifier(random_state=42)
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_rforest(self, model, dummy):
        """랜덤포레스트 K-Fold 교차 검증"""
        logger.info(">>> 랜덤포레스트 방식 검증")
        k_fold = self.create_k_fold()
        clf = RandomForestClassifier(n_estimators=13, random_state=42)
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_nb(self, model, dummy):
        """나이브베이즈 K-Fold 교차 검증"""
        logger.info(">>> 나이브베이즈 방식 검증")
        clf = GaussianNB()
        k_fold = self.create_k_fold()
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_svm(self, model, dummy):
        """SVM K-Fold 교차 검증"""
        logger.info(">>> SVM 방식 검증")
        k_fold = self.create_k_fold()
        clf = SVC(random_state=42, probability=True)
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    
    def accuracy_by_lightgbm(self, model, dummy):
        """LightGBM K-Fold 교차 검증"""
        if not LIGHTGBM_AVAILABLE:
            return None
        logger.info(">>> LightGBM 방식 검증")
        k_fold = self.create_k_fold()
        clf = lgb.LGBMClassifier(random_state=42, verbose=-1)
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold, n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy

    def learning(self):
        """모델 학습 - K-Fold 교차 검증으로 여러 모델 평가"""
        logger.info("😎😎 학습 시작")
        
        if self.processed_data is None:
            raise ValueError("전처리된 데이터가 없습니다. preprocess()를 먼저 실행하세요.")
        
        # 훈련 데이터 준비
        X_train = self.processed_data.train.copy()
        
        # 라벨 준비 (Survived)
        if isinstance(self.y_train, pd.Series):
            y_train = self.y_train
        elif isinstance(self.y_train, pd.DataFrame):
            y_train = self.y_train.iloc[:, 0]  # Survived 컬럼
        else:
            raise ValueError("라벨 데이터 형식이 올바르지 않습니다.")
        
        # 숫자 컬럼만 선택
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns
        X_train = X_train[numeric_cols]
        
        # 훈련/검증 데이터 분할 (최종 평가용)
        self.X_train, self.X_test, self.y_train_split, self.y_test_split = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        logger.info(f"📊 전체 데이터 크기: {X_train.shape}")
        logger.info(f"📊 훈련 데이터 크기: {self.X_train.shape}")
        logger.info(f"📊 검증 데이터 크기: {self.X_test.shape}")
        logger.info(f"📊 라벨 (Survived) 분포: {y_train.value_counts().to_dict()}")
        logger.info("="*80)
        logger.info("📊 K-Fold 교차 검증 (10-fold) 시작")
        logger.info("="*80)
        
        # K-Fold 교차 검증으로 모든 모델 평가
        accuracies = {}
        models = {}
        
        # 1. 로지스틱 회귀
        lr_accuracy = self.accuracy_by_logistic_regression(X_train, y_train)
        accuracies['logistic_regression'] = lr_accuracy / 100.0  # 0~1 범위로 변환
        logger.info(f'✅ 로지스틱 회귀 활용한 검증 정확도: {lr_accuracy}%')
        print(f'✅ 로지스틱 회귀 활용한 검증 정확도: {lr_accuracy}%')
        
        # 2. KNN
        knn_accuracy = self.accuracy_by_knn(X_train, y_train)
        accuracies['knn'] = knn_accuracy / 100.0
        logger.info(f'✅ KNN 활용한 검증 정확도: {knn_accuracy}%')
        print(f'✅ KNN 활용한 검증 정확도: {knn_accuracy}%')
        
        # 3. 결정트리
        dtree_accuracy = self.accuracy_by_dtree(X_train, y_train)
        accuracies['decision_tree'] = dtree_accuracy / 100.0
        logger.info(f'✅ 결정트리 활용한 검증 정확도: {dtree_accuracy}%')
        print(f'✅ 결정트리 활용한 검증 정확도: {dtree_accuracy}%')
        
        # 4. 랜덤 포레스트
        rf_accuracy = self.accuracy_by_rforest(X_train, y_train)
        accuracies['random_forest'] = rf_accuracy / 100.0
        logger.info(f'✅ 랜덤포레스트 활용한 검증 정확도: {rf_accuracy}%')
        print(f'✅ 랜덤포레스트 활용한 검증 정확도: {rf_accuracy}%')
        
        # 5. 나이브베이즈
        nb_accuracy = self.accuracy_by_nb(X_train, y_train)
        accuracies['naive_bayes'] = nb_accuracy / 100.0
        logger.info(f'✅ 나이브베이즈 활용한 검증 정확도: {nb_accuracy}%')
        print(f'✅ 나이브베이즈 활용한 검증 정확도: {nb_accuracy}%')
        
        # 6. SVM
        svm_accuracy = self.accuracy_by_svm(X_train, y_train)
        accuracies['svm'] = svm_accuracy / 100.0
        logger.info(f'✅ SVM 활용한 검증 정확도: {svm_accuracy}%')
        print(f'✅ SVM 활용한 검증 정확도: {svm_accuracy}%')
        
        # 7. LightGBM
        if LIGHTGBM_AVAILABLE:
            lgb_accuracy = self.accuracy_by_lightgbm(X_train, y_train)
            if lgb_accuracy is not None:
                accuracies['lightgbm'] = lgb_accuracy / 100.0
                logger.info(f'✅ LightGBM 활용한 검증 정확도: {lgb_accuracy}%')
                print(f'✅ LightGBM 활용한 검증 정확도: {lgb_accuracy}%')
            else:
                accuracies['lightgbm'] = None
        else:
            logger.warning("⚠️ LightGBM이 설치되지 않았습니다. pip install lightgbm으로 설치하세요.")
            print("⚠️ LightGBM이 설치되지 않았습니다. pip install lightgbm으로 설치하세요.")
            accuracies['lightgbm'] = None
        
        # 최고 성능 모델로 최종 학습
        best_model_name = max([k for k, v in accuracies.items() if v is not None], 
                             key=lambda k: accuracies[k])
        
        logger.info("="*80)
        logger.info("📊 모델별 K-Fold 교차 검증 정확도 요약:")
        logger.info("="*80)
        print('\n' + '='*80)
        print("📊 모델별 K-Fold 교차 검증 정확도 요약:")
        print('='*80)
        model_names_kr = {
            'logistic_regression': '로지스틱 회귀',
            'knn': 'KNN',
            'decision_tree': '결정트리',
            'random_forest': '랜덤 포레스트',
            'naive_bayes': '나이브베이즈',
            'svm': 'SVM',
            'lightgbm': 'LightGBM'
        }
        for model_name, acc in accuracies.items():
            if acc is not None:
                kr_name = model_names_kr.get(model_name, model_name)
                logger.info(f"  {kr_name:15s}: {acc*100:.2f}%")
                print(f"  {kr_name:15s}: {acc*100:.2f}%")
        logger.info("="*80)
        logger.info(f"🏆 최고 성능 모델: {model_names_kr.get(best_model_name, best_model_name)} (정확도: {accuracies[best_model_name]*100:.2f}%)")
        print('='*80)
        print(f"🏆 최고 성능 모델: {model_names_kr.get(best_model_name, best_model_name)} (정확도: {accuracies[best_model_name]*100:.2f}%)")
        print('='*80 + '\n')
        
        # 최고 성능 모델로 최종 학습 (전체 데이터 사용)
        logger.info(f"📚 최고 성능 모델 ({best_model_name})로 최종 학습 중...")
        if best_model_name == 'logistic_regression':
            final_model = LogisticRegression(random_state=42, max_iter=1000)
        elif best_model_name == 'knn':
            final_model = KNeighborsClassifier(n_neighbors=13)
        elif best_model_name == 'decision_tree':
            final_model = DecisionTreeClassifier(random_state=42)
        elif best_model_name == 'random_forest':
            final_model = RandomForestClassifier(n_estimators=13, random_state=42)
        elif best_model_name == 'naive_bayes':
            final_model = GaussianNB()
        elif best_model_name == 'svm':
            final_model = SVC(random_state=42, probability=True)
        elif best_model_name == 'lightgbm' and LIGHTGBM_AVAILABLE:
            final_model = lgb.LGBMClassifier(random_state=42, verbose=-1)
        else:
            final_model = RandomForestClassifier(n_estimators=13, random_state=42)
        
        final_model.fit(self.X_train, self.y_train_split)
        self.model = final_model
        self.models = models
        self.accuracies = accuracies
        
        logger.info("😎😎 학습 완료")
        
        return self.model

    def evaluate(self):
        """모델 평가 및 정확도 테스트"""
        logger.info("😎😎 평가 시작")
        
        if self.X_test is None or self.y_test_split is None:
            raise ValueError("검증 데이터가 없습니다. learning()을 먼저 실행하세요.")
        
        # 모든 모델의 정확도 출력
        if hasattr(self, 'accuracies') and self.accuracies:
            logger.info("="*80)
            logger.info("📊 모든 모델의 검증 정확도:")
            logger.info("="*80)
            print('\n' + '='*80)
            print("📊 모든 모델의 검증 정확도:")
            print('='*80)
            model_names_kr = {
                'logistic_regression': '로지스틱 회귀',
                'knn': 'KNN',
                'decision_tree': '결정트리',
                'random_forest': '랜덤 포레스트',
                'naive_bayes': '나이브베이즈',
                'lightgbm': 'LightGBM',
                'svm': 'SVM'
            }
            for model_name, acc in self.accuracies.items():
                if acc is not None:
                    kr_name = model_names_kr.get(model_name, model_name)
                    logger.info(f"  {kr_name:15s}: {acc:.4f} ({acc*100:.2f}%)")
                    print(f"  {kr_name:15s}: {acc:.4f} ({acc*100:.2f}%)")
            logger.info("="*80)
            print('='*80 + '\n')
        
        # 최고 성능 모델로 예측
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. learning()을 먼저 실행하세요.")
        
        # 사망자 수 예측 결과 분석
        predictions = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test_split, predictions)
        
        death_count = int((predictions == 0).sum())
        survival_count = int((predictions == 1).sum())
        actual_death_count = int((self.y_test_split == 0).sum())
        actual_survival_count = int((self.y_test_split == 1).sum())
        
        # 정확도 상세 정보
        logger.info("="*80)
        logger.info("📊 최종 모델 평가 결과:")
        logger.info("="*80)
        print('\n' + '='*80)
        print("📊 최종 모델 평가 결과:")
        print('='*80)
        logger.info(f"  전체 정확도: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  전체 정확도: {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"  예측된 사망자 수: {death_count}명")
        print(f"  예측된 사망자 수: {death_count}명")
        logger.info(f"  실제 사망자 수: {actual_death_count}명")
        print(f"  실제 사망자 수: {actual_death_count}명")
        logger.info(f"  예측된 생존자 수: {survival_count}명")
        print(f"  예측된 생존자 수: {survival_count}명")
        logger.info(f"  실제 생존자 수: {actual_survival_count}명")
        print(f"  실제 생존자 수: {actual_survival_count}명")
        
        # 사망자/생존자별 정확도
        if actual_death_count > 0:
            death_accuracy = float((predictions == 0).sum() / actual_death_count)
            logger.info(f"  사망자 예측 정확도: {death_accuracy:.4f} ({death_accuracy*100:.2f}%)")
            print(f"  사망자 예측 정확도: {death_accuracy:.4f} ({death_accuracy*100:.2f}%)")
        
        if actual_survival_count > 0:
            survival_accuracy = float((predictions == 1).sum() / actual_survival_count)
            logger.info(f"  생존자 예측 정확도: {survival_accuracy:.4f} ({survival_accuracy*100:.2f}%)")
            print(f"  생존자 예측 정확도: {survival_accuracy:.4f} ({survival_accuracy*100:.2f}%)")
        
        logger.info("="*80)
        print('='*80 + '\n')
        
        # 추가 지표 계산
        from sklearn.metrics import precision_score, recall_score, f1_score
        
        precision = precision_score(self.y_test_split, predictions, average='weighted', zero_division=0)
        recall = recall_score(self.y_test_split, predictions, average='weighted', zero_division=0)
        f1 = f1_score(self.y_test_split, predictions, average='weighted', zero_division=0)
        
        results = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "accuracies": self.accuracies if hasattr(self, 'accuracies') else {},
            "death_prediction": {
                "predicted_death": death_count,
                "predicted_survival": survival_count,
                "actual_death": actual_death_count,
                "actual_survival": actual_survival_count,
                "death_accuracy": float((predictions == 0).sum() / actual_death_count) if actual_death_count > 0 else 0.0,
                "survival_accuracy": float((predictions == 1).sum() / actual_survival_count) if actual_survival_count > 0 else 0.0
            }
        }
        
        logger.info("😎😎 평가 완료")

        return results

    def submit(self):
        """Kaggle 제출 파일 생성"""
        logger.info("😎😎 Kaggle 제출 파일 생성 시작")
        print('\n' + '='*80)
        print("😎😎 Kaggle 제출 파일 생성 시작")
        print('='*80)
        
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. learning()을 먼저 실행하세요.")
        
        # sklearn 모델인지 확인 (is_trained 속성이 없음)
        if hasattr(self.model, 'is_trained') and not self.model.is_trained:
            raise ValueError("모델이 학습되지 않았습니다. learning()을 먼저 실행하세요.")
        
        if self.processed_data is None or self.processed_data.test is None:
            raise ValueError("전처리된 테스트 데이터가 없습니다. preprocess()를 먼저 실행하세요.")
        
        # 테스트 데이터 준비
        X_test = self.processed_data.test.copy()
        
        # 숫자 컬럼만 선택
        numeric_cols = X_test.select_dtypes(include=[np.number]).columns
        X_test = X_test[numeric_cols]
        
        logger.info(f"📊 테스트 데이터 크기: {X_test.shape}")
        print(f"📊 테스트 데이터 크기: {X_test.shape}")
        
        # 예측 수행
        logger.info("🔮 예측 수행 중...")
        print("🔮 예측 수행 중...")
        predictions = self.model.predict(X_test)
        
        # 예측값을 정수형으로 변환 (0 또는 1)
        predictions = predictions.astype(int)
        
        # 원본 테스트 데이터에서 PassengerId 가져오기
        df_test_original = pd.read_csv(self.test_csv_path)
        passenger_ids = df_test_original['PassengerId'].values
        
        # Kaggle 제출 형식에 맞게 DataFrame 생성
        submission = pd.DataFrame({
            'PassengerId': passenger_ids,
            'Survived': predictions
        })
        
        # 파일 저장 경로 (app/titanic/submission.csv)
        output_path = Path(__file__).parent / "submission.csv"
        submission.to_csv(output_path, index=False)
        
        # 사망자 수 통계
        death_count = int((predictions == 0).sum())
        survival_count = int((predictions == 1).sum())
        total_count = len(predictions)
        
        # 결과 출력
        logger.info("="*80)
        logger.info("📊 Kaggle 제출 파일 생성 완료")
        logger.info("="*80)
        logger.info(f"✅ 파일 경로: {output_path}")
        logger.info(f"📊 총 예측 개수: {total_count}명")
        logger.info(f"📊 예측된 사망자 수: {death_count}명 ({death_count/total_count*100:.2f}%)")
        logger.info(f"📊 예측된 생존자 수: {survival_count}명 ({survival_count/total_count*100:.2f}%)")
        logger.info("="*80)
        
        print("="*80)
        print("📊 Kaggle 제출 파일 생성 완료")
        print("="*80)
        print(f"✅ 파일 경로: {output_path}")
        print(f"📊 총 예측 개수: {total_count}명")
        print(f"📊 예측된 사망자 수: {death_count}명 ({death_count/total_count*100:.2f}%)")
        print(f"📊 예측된 생존자 수: {survival_count}명 ({survival_count/total_count*100:.2f}%)")
        print("="*80)
        
        # 상위 10개 예측 결과 미리보기
        logger.info("\n📋 제출 파일 상위 10개 행 미리보기:")
        print("\n📋 제출 파일 상위 10개 행 미리보기:")
        print(submission.head(10).to_string(index=False))
        print()
        
        logger.info("😎😎 제출 완료")
        print("😎😎 제출 완료\n")
        
        return submission
    
    def analyze_train_data(self) -> Dict[str, Any]:
        """
        트레인 데이터 분석
        
        Returns:
            분석 결과 딕셔너리
        """
        logger.info("📊 트레인 데이터 분석 시작")
        import pandas as pd
        
        # 원본 데이터 로드
        df_train = pd.read_csv(self.train_csv_path)
        
        # 기본 정보
        total_rows = len(df_train)
        total_cols = len(df_train.columns)
        
        # 생존자/사망자 분포
        if 'Survived' in df_train.columns:
            survival_counts = df_train['Survived'].value_counts().to_dict()
            survival_rate = (df_train['Survived'].sum() / total_rows) * 100
        else:
            survival_counts = {}
            survival_rate = None
        
        # 각 컬럼별 통계
        column_stats = {}
        for col in df_train.columns:
            if df_train[col].dtype in ['int64', 'float64']:
                column_stats[col] = {
                    "type": "numeric",
                    "null_count": int(df_train[col].isnull().sum()),
                    "null_percentage": float((df_train[col].isnull().sum() / total_rows) * 100),
                    "mean": float(df_train[col].mean()) if df_train[col].dtype == 'float64' else None,
                    "median": float(df_train[col].median()) if df_train[col].dtype == 'float64' else None,
                    "min": float(df_train[col].min()),
                    "max": float(df_train[col].max()),
                    "std": float(df_train[col].std()) if df_train[col].dtype == 'float64' else None,
                }
            else:
                value_counts = df_train[col].value_counts().head(10).to_dict()
                column_stats[col] = {
                    "type": "categorical",
                    "null_count": int(df_train[col].isnull().sum()),
                    "null_percentage": float((df_train[col].isnull().sum() / total_rows) * 100),
                    "unique_count": int(df_train[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in value_counts.items()}
                }
        
        # Pclass별 생존률
        pclass_survival = {}
        if 'Pclass' in df_train.columns and 'Survived' in df_train.columns:
            for pclass in sorted(df_train['Pclass'].unique()):
                pclass_data = df_train[df_train['Pclass'] == pclass]
                pclass_survival[int(pclass)] = {
                    "total": int(len(pclass_data)),
                    "survived": int(pclass_data['Survived'].sum()),
                    "survival_rate": float((pclass_data['Survived'].sum() / len(pclass_data)) * 100)
                }
        
        # 성별별 생존률
        gender_survival = {}
        sex_col = None
        for col in ['Sex', 'sex', 'Gender', 'gender']:
            if col in df_train.columns:
                sex_col = col
                break
        
        if sex_col and 'Survived' in df_train.columns:
            for gender in df_train[sex_col].unique():
                gender_data = df_train[df_train[sex_col] == gender]
                gender_survival[str(gender)] = {
                    "total": int(len(gender_data)),
                    "survived": int(gender_data['Survived'].sum()),
                    "survival_rate": float((gender_data['Survived'].sum() / len(gender_data)) * 100)
                }
        
        # 나이 구간별 생존률
        age_survival = {}
        if 'Age' in df_train.columns and 'Survived' in df_train.columns:
            age_bins = [0, 12, 18, 30, 50, 100]
            age_labels = ['0-12', '13-18', '19-30', '31-50', '50+']
            df_train_copy = df_train.copy()
            df_train_copy['AgeGroup'] = pd.cut(df_train_copy['Age'], bins=age_bins, labels=age_labels, include_lowest=True)
            for age_group in age_labels:
                age_data = df_train_copy[df_train_copy['AgeGroup'] == age_group]
                if len(age_data) > 0:
                    age_survival[age_group] = {
                        "total": int(len(age_data)),
                        "survived": int(age_data['Survived'].sum()),
                        "survival_rate": float((age_data['Survived'].sum() / len(age_data)) * 100)
                    }
        
        # 전체 결측치 정보
        null_info = {}
        for col in df_train.columns:
            null_count = int(df_train[col].isnull().sum())
            if null_count > 0:
                null_info[col] = {
                    "null_count": null_count,
                    "null_percentage": float((null_count / total_rows) * 100)
                }
        
        analysis_result = {
            "basic_info": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "columns": df_train.columns.tolist()
            },
            "survival_distribution": {
                "counts": {str(k): int(v) for k, v in survival_counts.items()},
                "survival_rate": float(survival_rate) if survival_rate is not None else None,
                "total": total_rows
            },
            "column_statistics": column_stats,
            "pclass_survival": pclass_survival,
            "gender_survival": gender_survival,
            "age_survival": age_survival,
            "null_information": null_info,
            "data_types": {col: str(dtype) for col, dtype in df_train.dtypes.items()}
        }
        
        logger.info("📊 트레인 데이터 분석 완료")
        return analysis_result