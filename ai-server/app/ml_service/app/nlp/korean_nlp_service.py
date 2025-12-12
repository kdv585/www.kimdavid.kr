"""
한국어 NLP 서비스
KoNLPy와 Kiwipiepy를 사용한 한국어 형태소 분석 및 BoW 생성
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
import pickle

logger = logging.getLogger(__name__)


class KoreanNLPService:
    """
    한국어 NLP 서비스 클래스
    
    주요 기능:
    - 형태소 분석 (Okt, Mecab, Komoran, Kiwi 지원)
    - BoW(Bag of Words) 생성
    - 불용어 처리
    - 품사 태깅 및 필터링
    """
    
    def __init__(self, analyzer: str = 'kiwi', use_cache: bool = True):
        """
        한국어 NLP 서비스 초기화
        
        Args:
            analyzer: 사용할 형태소 분석기 ('kiwi', 'okt', 'mecab', 'komoran', 'hannanum', 'kkma')
            use_cache: 분석 결과 캐싱 여부
        """
        self.analyzer_name = analyzer.lower()
        self.use_cache = use_cache
        self.analyzer = None
        self.stopwords = []
        
        # 분석기 초기화
        self._init_analyzer()
        
        # 불용어 로드
        self._load_stopwords()
        
        logger.info(f"한국어 NLP 서비스 초기화 완료: {self.analyzer_name}")
    
    def _init_analyzer(self):
        """형태소 분석기 초기화"""
        try:
            if self.analyzer_name == 'kiwi':
                # Kiwipiepy (가장 빠르고 최신)
                try:
                    from kiwipiepy import Kiwi
                    self.analyzer = Kiwi()
                    logger.info("Kiwi 형태소 분석기 로드 성공")
                except ImportError as e:
                    logger.warning(f"Kiwipiepy가 설치되지 않았습니다: {e}. Okt로 대체합니다.")
                    self.analyzer_name = 'okt'
                    self._init_okt()
                except Exception as e:
                    logger.warning(f"Kiwipiepy 초기화 실패: {e}. Okt로 대체합니다.")
                    self.analyzer_name = 'okt'
                    self._init_okt()
            
            elif self.analyzer_name == 'okt':
                self._init_okt()
            
            elif self.analyzer_name == 'mecab':
                from konlpy.tag import Mecab
                self.analyzer = Mecab()
                logger.info("Mecab 형태소 분석기 로드 성공")
            
            elif self.analyzer_name == 'komoran':
                from konlpy.tag import Komoran
                self.analyzer = Komoran()
                logger.info("Komoran 형태소 분석기 로드 성공")
            
            elif self.analyzer_name == 'hannanum':
                from konlpy.tag import Hannanum
                self.analyzer = Hannanum()
                logger.info("Hannanum 형태소 분석기 로드 성공")
            
            elif self.analyzer_name == 'kkma':
                from konlpy.tag import Kkma
                self.analyzer = Kkma()
                logger.info("Kkma 형태소 분석기 로드 성공")
            
            else:
                logger.warning(f"알 수 없는 분석기: {self.analyzer_name}. Okt로 대체합니다.")
                self._init_okt()
                
        except ImportError as e:
            logger.error(f"형태소 분석기 로드 실패: {e}")
            logger.warning("기본 정규식 토크나이저를 사용합니다.")
            self.analyzer = None
    
    def _init_okt(self):
        """Okt 초기화"""
        try:
            from konlpy.tag import Okt
            self.analyzer = Okt()
            logger.info("Okt 형태소 분석기 로드 성공")
        except ImportError:
            logger.error("KoNLPy가 설치되지 않았습니다.")
            self.analyzer = None
    
    def _load_stopwords(self):
        """불용어 로드"""
        try:
            stopwords_file = Path(__file__).parent / "data" / "stopwords.txt"
            if stopwords_file.exists():
                with open(stopwords_file, 'r', encoding='utf-8') as f:
                    stopwords_text = f.read()
                    self.stopwords = stopwords_text.split()
                    logger.info(f"불용어 {len(self.stopwords)}개 로드 완료")
        except Exception as e:
            logger.warning(f"불용어 로드 실패: {e}")
            self.stopwords = []
    
    def morphs(self, text: str, stem: bool = False) -> List[str]:
        """
        형태소 분석
        
        Args:
            text: 입력 텍스트
            stem: 어간 추출 여부 (Kiwi에서만 지원)
            
        Returns:
            형태소 리스트
        """
        if self.analyzer is None:
            # 기본 공백 분리
            return text.split()
        
        try:
            if self.analyzer_name == 'kiwi':
                result = self.analyzer.tokenize(text)
                return [token.form for token in result]
            else:
                # KoNLPy 분석기들
                return self.analyzer.morphs(text)
        except Exception as e:
            logger.error(f"형태소 분석 실패: {e}")
            return text.split()
    
    def nouns(self, text: str) -> List[str]:
        """
        명사 추출
        
        Args:
            text: 입력 텍스트
            
        Returns:
            명사 리스트
        """
        if self.analyzer is None:
            return text.split()
        
        try:
            if self.analyzer_name == 'kiwi':
                result = self.analyzer.tokenize(text)
                return [token.form for token in result if token.tag.startswith('N')]
            else:
                return self.analyzer.nouns(text)
        except Exception as e:
            logger.error(f"명사 추출 실패: {e}")
            return text.split()
    
    def pos(self, text: str) -> List[Tuple[str, str]]:
        """
        품사 태깅
        
        Args:
            text: 입력 텍스트
            
        Returns:
            (형태소, 품사) 튜플 리스트
        """
        if self.analyzer is None:
            return [(word, 'UNKNOWN') for word in text.split()]
        
        try:
            if self.analyzer_name == 'kiwi':
                result = self.analyzer.tokenize(text)
                return [(token.form, token.tag) for token in result]
            else:
                return self.analyzer.pos(text)
        except Exception as e:
            logger.error(f"품사 태깅 실패: {e}")
            return [(word, 'UNKNOWN') for word in text.split()]
    
    def create_bow(self, text: str, 
                   pos_filter: Optional[List[str]] = None,
                   min_length: int = 2,
                   remove_stopwords: bool = True) -> Dict[str, int]:
        """
        BoW(Bag of Words) 생성
        
        Args:
            text: 입력 텍스트
            pos_filter: 품사 필터 (예: ['NNG', 'NNP', 'VV'] - 명사, 동사만)
            min_length: 최소 형태소 길이
            remove_stopwords: 불용어 제거 여부
            
        Returns:
            단어-빈도 딕셔너리
        """
        # 품사 태깅
        pos_tagged = self.pos(text)
        
        # 필터링
        filtered_words = []
        for word, pos_tag in pos_tagged:
            # 길이 필터
            if len(word) < min_length:
                continue
            
            # 품사 필터
            if pos_filter and not any(pos_tag.startswith(p) for p in pos_filter):
                continue
            
            # 불용어 필터
            if remove_stopwords and word in self.stopwords:
                continue
            
            filtered_words.append(word)
        
        # 빈도 계산
        bow = Counter(filtered_words)
        return dict(bow)
    
    def create_bow_from_nouns(self, text: str,
                             min_length: int = 2,
                             remove_stopwords: bool = True) -> Dict[str, int]:
        """
        명사만으로 BoW 생성
        
        Args:
            text: 입력 텍스트
            min_length: 최소 형태소 길이
            remove_stopwords: 불용어 제거 여부
            
        Returns:
            단어-빈도 딕셔너리
        """
        nouns = self.nouns(text)
        
        # 필터링
        filtered_words = [
            word for word in nouns
            if len(word) >= min_length 
            and (not remove_stopwords or word not in self.stopwords)
        ]
        
        # 빈도 계산
        bow = Counter(filtered_words)
        return dict(bow)
    
    def save_bow(self, bow: Dict[str, int], filepath: Path):
        """
        BoW를 파일로 저장
        
        Args:
            bow: BoW 딕셔너리
            filepath: 저장 경로
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(bow, f)
            logger.info(f"BoW 저장 완료: {filepath}")
        except Exception as e:
            logger.error(f"BoW 저장 실패: {e}")
    
    def load_bow(self, filepath: Path) -> Dict[str, int]:
        """
        BoW를 파일에서 로드
        
        Args:
            filepath: 로드 경로
            
        Returns:
            BoW 딕셔너리
        """
        try:
            with open(filepath, 'rb') as f:
                bow = pickle.load(f)
            logger.info(f"BoW 로드 완료: {filepath}")
            return bow
        except Exception as e:
            logger.error(f"BoW 로드 실패: {e}")
            return {}


# 싱글톤 인스턴스
_korean_nlp_instance: Optional[KoreanNLPService] = None


def get_korean_nlp_service(analyzer: str = 'kiwi') -> KoreanNLPService:
    """
    한국어 NLP 서비스 싱글톤 인스턴스 반환
    
    Args:
        analyzer: 사용할 형태소 분석기
        
    Returns:
        KoreanNLPService 인스턴스
    """
    global _korean_nlp_instance
    if _korean_nlp_instance is None:
        _korean_nlp_instance = KoreanNLPService(analyzer=analyzer)
    return _korean_nlp_instance


# 사용 예제
if __name__ == "__main__":
    # 서비스 초기화
    nlp = KoreanNLPService(analyzer='kiwi')
    
    # 예제 텍스트
    text = """
    삼성전자는 한국의 대표적인 전자제품 제조 회사입니다.
    스마트폰, 반도체, 디스플레이 등 다양한 제품을 생산합니다.
    """
    
    # 형태소 분석
    print("형태소:", nlp.morphs(text))
    
    # 명사 추출
    print("\n명사:", nlp.nouns(text))
    
    # 품사 태깅
    print("\n품사 태깅:", nlp.pos(text))
    
    # BoW 생성 (명사만)
    bow = nlp.create_bow_from_nouns(text)
    print("\nBoW (명사):", bow)
    
    # BoW 생성 (명사+동사)
    bow_full = nlp.create_bow(text, pos_filter=['N', 'V'])
    print("\nBoW (명사+동사):", bow_full)
