"""
미국 실업률 데이터 서비스 (OOP 구조)
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

# Import 경로 설정 (Docker/로컬 환경 모두 지원)
current_file = Path(__file__).resolve()
if str(current_file).startswith("/app"):
    # Docker 환경
    try:
        from app.ml_service.common.utils import setup_logging
    except ImportError:
        try:
            from app.common.utils import setup_logging
        except ImportError:
            import logging
            def setup_logging(name):
                return logging.getLogger(name)
else:
    # 로컬 환경
    try:
        ai_server_path = current_file.parent.parent.parent
        if str(ai_server_path) not in sys.path:
            sys.path.insert(0, str(ai_server_path))
        from app.ml_service.common.utils import setup_logging
    except ImportError:
        import logging
        def setup_logging(name):
            return logging.getLogger(name)

try:
    logger = setup_logging("us_unemployment_service")
except (ImportError, NameError):
    import logging
    logger = logging.getLogger("us_unemployment_service")


class UnemploymentData:
    """실업률 데이터 클래스 (데이터 모델)"""
    
    def __init__(self):
        self._data_dir: Optional[Path] = None
        self._save_dir: Optional[Path] = None
        self._raw_data: Optional[pd.DataFrame] = None
        self._processed_data: Optional[pd.DataFrame] = None
    
    @property
    def data_dir(self) -> Path:
        """데이터 디렉토리 경로"""
        if self._data_dir is None:
            current_file = Path(__file__).resolve()
            if str(current_file).startswith("/app"):
                # Docker 환경
                self._data_dir = Path("/app/app/us_unemployment/data")
            else:
                # 로컬 환경
                self._data_dir = current_file.parent / "data"
            self._data_dir.mkdir(parents=True, exist_ok=True)
        return self._data_dir
    
    @data_dir.setter
    def data_dir(self, path: Path):
        self._data_dir = Path(path)
    
    @property
    def save_dir(self) -> Path:
        """저장 디렉토리 경로"""
        if self._save_dir is None:
            current_file = Path(__file__).resolve()
            if str(current_file).startswith("/app"):
                # Docker 환경
                self._save_dir = Path("/app/app/us_unemployment/save")
            else:
                # 로컬 환경
                self._save_dir = current_file.parent / "save"
            self._save_dir.mkdir(parents=True, exist_ok=True)
        return self._save_dir
    
    @save_dir.setter
    def save_dir(self, path: Path):
        self._save_dir = Path(path)
    
    @property
    def raw_data(self) -> Optional[pd.DataFrame]:
        """원본 데이터"""
        return self._raw_data
    
    @raw_data.setter
    def raw_data(self, data: pd.DataFrame):
        self._raw_data = data
    
    @property
    def processed_data(self) -> Optional[pd.DataFrame]:
        """전처리된 데이터"""
        return self._processed_data
    
    @processed_data.setter
    def processed_data(self, data: pd.DataFrame):
        self._processed_data = data


class UnemploymentMethod:
    """실업률 데이터 처리 메서드 클래스"""
    
    def __init__(self):
        self.logger = logger
    
    def read_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """CSV 파일 읽기"""
        try:
            df = pd.read_csv(file_path, **kwargs)
            self.logger.info(f"CSV 파일 로드 완료: {file_path}, shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"CSV 파일 읽기 실패: {file_path}, 오류: {str(e)}")
            raise
    
    def read_json(self, file_path: str, **kwargs) -> pd.DataFrame:
        """JSON 파일 읽기"""
        try:
            df = pd.read_json(file_path, **kwargs)
            self.logger.info(f"JSON 파일 로드 완료: {file_path}, shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"JSON 파일 읽기 실패: {file_path}, 오류: {str(e)}")
            raise
    
    def merge_data(self, left: pd.DataFrame, right: pd.DataFrame, 
                   on: Optional[str] = None, 
                   left_on: Optional[str] = None, 
                   right_on: Optional[str] = None,
                   how: str = 'inner') -> pd.DataFrame:
        """두 DataFrame 병합"""
        try:
            if on:
                merged = pd.merge(left, right, on=on, how=how, suffixes=('', '_y'))
            elif left_on and right_on:
                merged = pd.merge(left, right, left_on=left_on, right_on=right_on, 
                                how=how, suffixes=('', '_y'))
            else:
                raise ValueError("on 또는 left_on/right_on 파라미터가 필요합니다.")
            
            # 중복 컬럼 제거
            duplicate_cols = [col for col in merged.columns if col.endswith('_y')]
            for col in duplicate_cols:
                original_col = col[:-2]
                if original_col in merged.columns:
                    if merged[original_col].equals(merged[col]):
                        merged = merged.drop(columns=[col])
            
            self.logger.info(f"데이터 병합 완료: shape={merged.shape}")
            return merged
        except Exception as e:
            self.logger.error(f"데이터 병합 실패: {str(e)}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 정리 (결측치 처리, 타입 변환 등)"""
        try:
            df_cleaned = df.copy()
            
            # 결측치 확인
            missing_count = df_cleaned.isnull().sum()
            if missing_count.sum() > 0:
                self.logger.warning(f"결측치 발견: {missing_count[missing_count > 0].to_dict()}")
            
            # 숫자형 컬럼의 결측치를 0으로 채우기 (선택적)
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df_cleaned[col].isnull().sum() > 0:
                    df_cleaned[col] = df_cleaned[col].fillna(0)
            
            self.logger.info(f"데이터 정리 완료: shape={df_cleaned.shape}")
            return df_cleaned
        except Exception as e:
            self.logger.error(f"데이터 정리 실패: {str(e)}")
            raise
    
    def calculate_statistics(self, df: pd.DataFrame, 
                            value_column: str) -> Dict[str, Any]:
        """통계 계산"""
        try:
            if value_column not in df.columns:
                raise ValueError(f"컬럼 '{value_column}'을 찾을 수 없습니다.")
            
            stats = {
                'mean': float(df[value_column].mean()),
                'median': float(df[value_column].median()),
                'std': float(df[value_column].std()),
                'min': float(df[value_column].min()),
                'max': float(df[value_column].max()),
                'count': int(len(df)),
                'null_count': int(df[value_column].isnull().sum())
            }
            
            self.logger.info(f"통계 계산 완료: {value_column}")
            return stats
        except Exception as e:
            self.logger.error(f"통계 계산 실패: {str(e)}")
            raise


class UnemploymentService:
    """미국 실업률 데이터 서비스 클래스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.data = UnemploymentData()
        self.method = UnemploymentMethod()
        self.logger = logger
    
    def load_data(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        실업률 데이터 로드
        
        Args:
            filename: 데이터 파일명 (None이면 기본 파일 검색)
        
        Returns:
            로드된 데이터 정보 딕셔너리
        """
        try:
            data_dir = self.data.data_dir
            self.logger.info(f"데이터 로드 시작: {data_dir}")
            
            # 파일명이 지정되지 않으면 기본 파일 검색
            if filename is None:
                # 일반적인 실업률 데이터 파일명들
                possible_files = ['unemployment.csv', 'us_unemployment.csv', 'data.csv']
                filename = None
                for fname in possible_files:
                    file_path = data_dir / fname
                    if file_path.exists():
                        filename = fname
                        break
                
                if filename is None:
                    # 디렉토리의 첫 번째 CSV 파일 사용
                    csv_files = list(data_dir.glob("*.csv"))
                    if csv_files:
                        filename = csv_files[0].name
                    else:
                        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_dir}")
            
            file_path = data_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # CSV 파일 로드
            df = self.method.read_csv(str(file_path))
            
            # 데이터 저장
            self.data.raw_data = df
            
            self.logger.info(f"데이터 로드 완료: shape={df.shape}, columns={df.columns.tolist()}")
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "shape": list(df.shape),
                "columns": df.columns.tolist(),
                "data": df.head(10).to_dict(orient='records'),
                "message": "데이터가 성공적으로 로드되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"데이터 로드 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def preprocess(self) -> Dict[str, Any]:
        """
        실업률 데이터 전처리
        
        Returns:
            전처리된 데이터 정보 딕셔너리
        """
        try:
            if self.data.raw_data is None:
                raise ValueError("먼저 load_data()를 호출하여 데이터를 로드해주세요.")
            
            self.logger.info("데이터 전처리 시작")
            
            # 원본 데이터 복사
            df = self.data.raw_data.copy()
            
            # 데이터 정리
            df_cleaned = self.method.clean_data(df)
            
            # 전처리된 데이터 저장
            self.data.processed_data = df_cleaned
            
            self.logger.info(f"전처리 완료: shape={df_cleaned.shape}")
            
            return {
                "status": "success",
                "original_shape": list(df.shape),
                "processed_shape": list(df_cleaned.shape),
                "columns": df_cleaned.columns.tolist(),
                "data": df_cleaned.head(10).to_dict(orient='records'),
                "message": "데이터 전처리가 완료되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"전처리 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def get_statistics(self, value_column: Optional[str] = None) -> Dict[str, Any]:
        """
        실업률 통계 정보 조회
        
        Args:
            value_column: 통계를 계산할 컬럼명 (None이면 자동 검색)
        
        Returns:
            통계 정보 딕셔너리
        """
        try:
            df = self.data.processed_data
            if df is None:
                df = self.data.raw_data
                if df is None:
                    raise ValueError("먼저 load_data()를 호출하여 데이터를 로드해주세요.")
            
            # 값 컬럼 자동 검색
            if value_column is None:
                # 'unemployment', 'rate', 'value' 등의 키워드가 포함된 컬럼 검색
                possible_cols = [col for col in df.columns 
                                if any(keyword in col.lower() 
                                      for keyword in ['unemployment', 'rate', 'value', 'percent'])]
                if possible_cols:
                    value_column = possible_cols[0]
                else:
                    # 숫자형 컬럼 중 첫 번째 사용
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        value_column = numeric_cols[0]
                    else:
                        raise ValueError("통계를 계산할 수 있는 숫자형 컬럼을 찾을 수 없습니다.")
            
            # 통계 계산
            stats = self.method.calculate_statistics(df, value_column)
            
            return {
                "status": "success",
                "value_column": value_column,
                "statistics": stats,
                "message": "통계 정보가 성공적으로 계산되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"통계 계산 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def get_by_state(self, state: str) -> Dict[str, Any]:
        """
        특정 주의 실업률 데이터 조회
        
        Args:
            state: 주 이름 또는 코드
        
        Returns:
            해당 주의 실업률 데이터
        """
        try:
            df = self.data.processed_data
            if df is None:
                df = self.data.raw_data
                if df is None:
                    raise ValueError("먼저 load_data()를 호출하여 데이터를 로드해주세요.")
            
            # 주 컬럼 찾기
            state_col = None
            for col in df.columns:
                if 'state' in col.lower() or '주' in col.lower():
                    state_col = col
                    break
            
            if state_col is None:
                raise ValueError("주 정보를 포함한 컬럼을 찾을 수 없습니다.")
            
            # 해당 주의 데이터 필터링
            state_data = df[df[state_col].str.contains(state, case=False, na=False)]
            
            if len(state_data) == 0:
                return {
                    "status": "not_found",
                    "state": state,
                    "message": f"'{state}'에 해당하는 데이터를 찾을 수 없습니다."
                }
            
            return {
                "status": "success",
                "state": state,
                "count": len(state_data),
                "data": state_data.to_dict(orient='records'),
                "message": f"'{state}'의 데이터가 성공적으로 조회되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"주별 데이터 조회 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def save_processed_data(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        전처리된 데이터 저장
        
        Args:
            filename: 저장할 파일명 (None이면 기본 파일명 사용)
        
        Returns:
            저장 결과 정보
        """
        try:
            if self.data.processed_data is None:
                raise ValueError("전처리된 데이터가 없습니다. 먼저 preprocess()를 호출해주세요.")
            
            save_dir = self.data.save_dir
            if filename is None:
                filename = "processed_unemployment.csv"
            
            file_path = save_dir / filename
            
            # CSV로 저장
            self.data.processed_data.to_csv(str(file_path), index=False, encoding='utf-8')
            
            self.logger.info(f"전처리된 데이터 저장 완료: {file_path}")
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "message": "전처리된 데이터가 성공적으로 저장되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"데이터 저장 중 오류 발생: {str(e)}", exc_info=True)
            raise

