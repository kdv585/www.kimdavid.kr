# ************
# NLTK 자연어 처리 패키지
# ************
"""
https://datascienceschool.net/view-notebook/118731eec74b4ad3bdd2f89bab077e1b/
NLTK(Natural Language Toolkit) 패키지는 
교육용으로 개발된 자연어 처리 및 문서 분석용 파이썬 패키지다. 
다양한 기능 및 예제를 가지고 있으며 실무 및 연구에서도 많이 사용된다.
NLTK 패키지가 제공하는 주요 기능은 다음과 같다.
말뭉치
토큰 생성
형태소 분석
품사 태깅
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging

# 한국어 NLP 서비스 import (선택적)
try:
    import sys
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from korean_nlp_service import get_korean_nlp_service
    KOREAN_NLP_AVAILABLE = True
except ImportError:
    KOREAN_NLP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("한국어 NLP 서비스를 사용할 수 없습니다. 기본 토큰화를 사용합니다.")


class NLPService:
    """
    NLTK를 활용한 자연어 처리 서비스 클래스
    
    주요 기능:
    - 말뭉치 처리
    - 토큰 생성
    - 형태소 분석 (어간 추출, 원형 복원)
    - 품사 태깅
    - 텍스트 분석
    - 빈도 분석
    - 워드클라우드 생성
    """
    
    def __init__(self, download_books: bool = True, quiet: bool = True):
        """
        NLPService 초기화
        
        Args:
            download_books: NLTK 책 데이터 다운로드 여부
            quiet: 다운로드 시 출력 억제 여부
        """
        # Logger 초기화 (먼저 정의)
        logger = logging.getLogger(__name__)
        
        # NLTK 데이터 다운로드
        if download_books:
            try:
                nltk.download('punkt', quiet=quiet)
                nltk.download('punkt_tab', quiet=quiet)
                nltk.download('averaged_perceptron_tagger', quiet=quiet)
                nltk.download('averaged_perceptron_tagger_eng', quiet=quiet)
                nltk.download('wordnet', quiet=quiet)
                nltk.download('stopwords', quiet=quiet)
                nltk.download('omw-1.4', quiet=quiet)
                # book 데이터는 선택사항이므로 실패해도 계속 진행
                try:
                    nltk.download('book', quiet=quiet)
                except:
                    pass
            except Exception as e:
                logger.warning(f"NLTK 데이터 다운로드 중 일부 실패: {e}")
        
        # 형태소 분석기 초기화
        self.porter_stemmer = PorterStemmer()
        self.lancaster_stemmer = LancasterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # 정규식 토크나이저 초기화
        self.regex_tokenizer = RegexpTokenizer("[\w]+")
        self.regexp_tokenizer = self.regex_tokenizer  # 호환성을 위한 별칭
        
        # Stopwords 초기화
        self.stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        
        # data 디렉토리의 stopwords.txt 파일 읽기
        try:
            stopwords_file = Path(__file__).parent.parent / "data" / "stopwords.txt"
            if stopwords_file.exists():
                with open(stopwords_file, 'r', encoding='utf-8') as f:
                    stopwords_text = f.read()
                    # 공백으로 구분된 단어들을 리스트로 변환
                    file_stopwords = stopwords_text.split()
                    # 기존 stopwords에 추가 (중복 제거)
                    self.stopwords = list(set(self.stopwords + file_stopwords))
                    logger.info(f"stopwords.txt에서 {len(file_stopwords)}개의 불용어를 로드했습니다.")
        except Exception as e:
            logger.warning(f"stopwords.txt 파일을 읽는 중 오류가 발생했습니다: {e}")
    
    # *********
    # 말뭉치 관련 메서드
    # *********
    
    def get_corpus_fileids(self, corpus_name: str = 'gutenberg'):
        """
        말뭉치의 파일 ID 목록을 반환
        
        Args:
            corpus_name: 말뭉치 이름 (기본값: 'gutenberg')
            
        Returns:
            파일 ID 리스트
        """
        corpus = getattr(nltk.corpus, corpus_name, None)
        if corpus is None:
            raise ValueError(f"말뭉치 '{corpus_name}'을 찾을 수 없습니다.")
        return corpus.fileids()
    
    def get_corpus_raw(self, corpus_name: str, fileid: str):
        """
        말뭉치의 원문을 반환
        
        Args:
            corpus_name: 말뭉치 이름
            fileid: 파일 ID
            
        Returns:
            원문 문자열
        """
        corpus = getattr(nltk.corpus, corpus_name, None)
        if corpus is None:
            raise ValueError(f"말뭉치 '{corpus_name}'을 찾을 수 없습니다.")
        return corpus.raw(fileid)
    
    # ************
    # 토큰 생성 메서드
    # ************
    
    def tokenize_sentences(self, text: str) -> list:
        """
        문장 단위로 토큰화
        
        Args:
            text: 입력 텍스트
            
        Returns:
            문장 리스트
        """
        return sent_tokenize(text)
    
    def tokenize_words(self, text: str) -> list:
        """
        단어 단위로 토큰화
        
        Args:
            text: 입력 텍스트
            
        Returns:
            단어 토큰 리스트
        """
        return word_tokenize(text)
    
    def tokenize_regex(self, text: str, pattern: str = "[\w]+") -> list:
        """
        정규식을 사용한 토큰화
        
        Args:
            text: 입력 텍스트
            pattern: 정규식 패턴 (기본값: "[\w]+")
            
        Returns:
            토큰 리스트
        """
        tokenizer = RegexpTokenizer(pattern)
        return tokenizer.tokenize(text)
    
    # ***************
    # 형태소 분석 메서드
    # ***************
    
    def stem_porter(self, words: list) -> list:
        """
        Porter Stemmer를 사용한 어간 추출
        
        Args:
            words: 단어 리스트
            
        Returns:
            어간 추출된 단어 리스트
        """
        return [self.porter_stemmer.stem(word) for word in words]
    
    def stem_lancaster(self, words: list) -> list:
        """
        Lancaster Stemmer를 사용한 어간 추출
        
        Args:
            words: 단어 리스트
            
        Returns:
            어간 추출된 단어 리스트
        """
        return [self.lancaster_stemmer.stem(word) for word in words]
    
    def lemmatize(self, words: list, pos: str = None) -> list:
        """
        원형 복원 (Lemmatization)
        
        Args:
            words: 단어 리스트
            pos: 품사 태그 (선택사항)
            
        Returns:
            원형 복원된 단어 리스트
        """
        if pos:
            return [self.lemmatizer.lemmatize(word, pos=pos) for word in words]
        return [self.lemmatizer.lemmatize(word) for word in words]
    
    # **********
    # POS tagging 메서드
    # **********
    
    def get_pos_tag_info(self, tag: str):
        """
        품사 태그에 대한 설명을 출력
        
        Args:
            tag: 품사 태그
        """
        nltk.help.upenn_tagset(tag)
    
    def pos_tag(self, tokens: list) -> list:
        """
        품사 태깅
        
        Args:
            tokens: 토큰 리스트
            
        Returns:
            (토큰, 품사) 튜플 리스트
        """
        return pos_tag(tokens)
    
    def extract_pos(self, tagged_list: list, pos_tag: str) -> list:
        """
        특정 품사의 토큰만 추출
        
        Args:
            tagged_list: 품사 태깅된 리스트
            pos_tag: 추출할 품사 태그
            
        Returns:
            해당 품사의 토큰 리스트
        """
        return [t[0] for t in tagged_list if t[1] == pos_tag]
    
    def remove_tags(self, tagged_list: list) -> list:
        """
        품사 태그 제거
        
        Args:
            tagged_list: 품사 태깅된 리스트
            
        Returns:
            태그가 제거된 토큰 리스트
        """
        return untag(tagged_list)
    
    def create_pos_tokenizer(self, tagged_list: list):
        """
        품사 정보를 포함한 토크나이저 함수 생성
        
        Args:
            tagged_list: 품사 태깅된 리스트
            
        Returns:
            토크나이저 함수
        """
        def tokenizer(doc):
            return ["/".join(p) for p in tagged_list]
        return tokenizer
    
    # ***********
    # Text 클래스 관련 메서드
    # ***********
    
    def create_text(self, tokens: list, name: str = "Text") -> Text:
        """
        NLTK Text 객체 생성
        
        Args:
            tokens: 토큰 리스트
            name: 텍스트 이름
            
        Returns:
            Text 객체
        """
        return Text(tokens, name=name)
    
    def plot_word_frequency(self, text: Text, num_words: int = 20, show: bool = True):
        """
        단어 빈도 그래프 그리기
        
        Args:
            text: Text 객체
            num_words: 표시할 단어 수
            show: 그래프 표시 여부
        """
        text.plot(num_words)
        if show:
            plt.show()
    
    def plot_dispersion(self, text: Text, words: list, show: bool = True):
        """
        단어 분산 플롯
        
        Args:
            text: Text 객체
            words: 분석할 단어 리스트
            show: 그래프 표시 여부
        """
        text.dispersion_plot(words)
        if show:
            plt.show()
    
    def find_concordance(self, text: Text, word: str, lines: int = 5):
        """
        단어의 사용 위치 찾기
        
        Args:
            text: Text 객체
            word: 찾을 단어
            lines: 표시할 줄 수
        """
        text.concordance(word, lines=lines)
    
    def find_similar_words(self, text: Text, word: str, num: int = 10):
        """
        유사한 문맥에서 사용된 단어 찾기
        
        Args:
            text: Text 객체
            word: 기준 단어
            num: 반환할 단어 수
        """
        text.similar(word, num=num)
    
    def find_collocations(self, text: Text, num: int = 10):
        """
        연어(collocation) 찾기
        
        Args:
            text: Text 객체
            num: 반환할 연어 수
        """
        text.collocations(num=num)
    
    # ***********
    # FreqDist 관련 메서드
    # ***********
    
    def create_freqdist(self, tokens: list) -> FreqDist:
        """
        빈도 분포 객체 생성
        
        Args:
            tokens: 토큰 리스트
            
        Returns:
            FreqDist 객체
        """
        return FreqDist(tokens)
    
    def get_freq_stats(self, freqdist: FreqDist, word: str = None) -> dict:
        """
        빈도 통계 정보 반환
        
        Args:
            freqdist: FreqDist 객체
            word: 특정 단어 (선택사항)
            
        Returns:
            통계 정보 딕셔너리
        """
        stats = {
            'total_count': freqdist.N(),
        }
        
        if word:
            stats['word_count'] = freqdist[word]
            stats['word_frequency'] = freqdist.freq(word)
        
        return stats
    
    def get_most_common(self, freqdist: FreqDist, num: int = 10) -> list:
        """
        가장 빈번한 단어 반환
        
        Args:
            freqdist: FreqDist 객체
            num: 반환할 단어 수
            
        Returns:
            (단어, 빈도) 튜플 리스트
        """
        return freqdist.most_common(num)
    
    def extract_names_from_corpus(self, corpus_text: str, stopwords: list = None) -> FreqDist:
        """
        말뭉치에서 고유명사(NNP) 추출하여 빈도 분포 생성
        
        Args:
            corpus_text: 말뭉치 텍스트
            stopwords: 제외할 단어 리스트
            
        Returns:
            고유명사 빈도 분포 객체
        """
        if stopwords is None:
            stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
        
        tokens = self.tokenize_regex(corpus_text)
        tagged_tokens = self.pos_tag(tokens)
        names = [t[0] for t in tagged_tokens 
                if t[1] == "NNP" and t[0] not in stopwords]
        
        return self.create_freqdist(names)
    
    # ***********
    # 워드클라우드 메서드
    # ***********
    
    def generate_wordcloud_from_freqdist(self, freqdist: FreqDist, 
                          width: int = 1000, 
                          height: int = 600,
                          background_color: str = "white",
                          random_state: int = 0,
                          show: bool = True) -> WordCloud:
        """
        워드클라우드 생성
        
        Args:
            freqdist: 빈도 분포 객체
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            random_state: 랜덤 시드
            show: 그래프 표시 여부
            
        Returns:
            WordCloud 객체
        """
        wc = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state
        )
        wc.generate_from_frequencies(freqdist)
        
        if show:
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.show()
        
        return wc
    
    def generate_wordcloud_from_text(self, text: str,
                                    width: int = 1000,
                                    height: int = 600,
                                    background_color: str = "white",
                                    random_state: int = 0,
                                    show: bool = True) -> WordCloud:
        """
        텍스트로부터 직접 워드클라우드 생성
        
        Args:
            text: 입력 텍스트
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            random_state: 랜덤 시드
            show: 그래프 표시 여부
            
        Returns:
            WordCloud 객체
        """
        wc = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state
        )
        wc.generate(text)
        
        if show:
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.show()
        
        return wc
    
    def generate_wordcloud(self, text: str, width: int = 1000, height: int = 600,
                          background_color: str = "white", max_words: int = 100) -> Dict[str, Any]:
        """
        워드클라우드 생성 (API용)
        
        Args:
            text: 입력 텍스트
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            max_words: 최대 단어 수
            
        Returns:
            워드클라우드 정보를 포함한 딕셔너리
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 한국어 텍스트 감지 (한글 유니코드 범위 체크)
            has_korean = any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in text[:1000])
            
            if has_korean and KOREAN_NLP_AVAILABLE:
                # 한국어 NLP 서비스 사용
                try:
                    korean_nlp = get_korean_nlp_service(analyzer='kiwi')
                    # BoW 생성 (명사 중심)
                    bow = korean_nlp.create_bow_from_nouns(
                        text,
                        min_length=2,
                        remove_stopwords=True
                    )
                    freq_dist = FreqDist(bow)
                    logger.info(f"한국어 형태소 분석 완료: {len(bow)}개 단어")
                except Exception as e:
                    logger.warning(f"한국어 형태소 분석 실패, 기본 토큰화 사용: {e}")
                    # 폴백: 기본 토큰화
                    tokens = self.regexp_tokenizer.tokenize(text)
                    filtered_tokens = [word for word in tokens 
                                     if len(word) > 1 and word not in self.stopwords]
                    freq_dist = FreqDist(filtered_tokens)
            elif has_korean:
                # 한국어지만 NLP 서비스 없음: 기본 토큰화
                logger.info("한국어 텍스트이지만 형태소 분석기가 없어 기본 토큰화 사용")
                tokens = self.regexp_tokenizer.tokenize(text)
                filtered_tokens = [word for word in tokens 
                                 if len(word) > 1 and word not in self.stopwords]
                freq_dist = FreqDist(filtered_tokens)
            else:
                # 영어 텍스트의 경우: 품사 태깅으로 고유명사만 추출
                pos_tagged = pos_tag(tokens)
                proper_nouns = [word for word, tag in pos_tagged
                              if tag == 'NNP' and word not in self.stopwords]
                
                # 고유명사가 3개 미만이면 모든 단어 사용 (워드클라우드 품질 향상)
                if len(proper_nouns) < 3:
                    # 모든 단어 사용하되, 불용어 제거
                    filtered_tokens = [word.lower() for word in tokens 
                                     if word.lower() not in [sw.lower() for sw in self.stopwords]]
                    freq_dist = FreqDist(filtered_tokens)
                else:
                    freq_dist = FreqDist(proper_nouns)
            # 워드클라우드 생성
            # 한글 폰트 경로 설정
            font_path = None
            if has_korean:
                font_file = Path(__file__).parent.parent / "data" / "D2Coding.ttf"
                if font_file.exists():
                    font_path = str(font_file)
                    logger.info(f"한글 폰트 사용: {font_path}")
                else:
                    logger.warning("D2Coding.ttf 폰트 파일을 찾을 수 없습니다. 한글이 제대로 표시되지 않을 수 있습니다.")
            
            wc = WordCloud(
                width=width,
                height=height,
                background_color=background_color,
                max_words=max_words,
                random_state=42,
                font_path=font_path if font_path else None
            )
            # 빈도수 딕셔너리로 워드클라우드 생성
            freq_dict = dict(freq_dist.most_common(max_words))
            wordcloud = wc.generate_from_frequencies(freq_dict)
            # 이미지를 base64로 인코딩
            img_buffer = io.BytesIO()
            plt.figure(figsize=(width/100, height/100))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # 파일로 저장
            save_dir = Path(__file__).parent.parent / "save"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wordcloud_{timestamp}.png"
            filepath = save_dir / filename
            
            # 파일 저장
            img_buffer.seek(0)
            with open(filepath, 'wb') as f:
                f.write(img_buffer.getvalue())
            
            logger.info(f"워드클라우드가 저장되었습니다: {filepath}")
            
            return {
                "status": "success",
                "word_count": len(freq_dict),
                "most_common": list(freq_dict.items())[:10],
                "image_base64": img_base64,
                "saved_file": str(filepath),
                "filename": filename,
                "config": {
                    "width": width,
                    "height": height,
                    "background_color": background_color,
                    "max_words": max_words
                }
            }
        except Exception as e:
            logger.error(f"워드클라우드 생성 실패: {str(e)}")
            return {"error": str(e)}


# 사용 예제
if __name__ == "__main__":
    # 서비스 인스턴스 생성
    nlp = NLPService()
    
    # 말뭉치 예제
    fileids = nlp.get_corpus_fileids('gutenberg')
    print(f"Gutenberg 말뭉치 파일: {fileids[:5]}")
    
    emma_raw = nlp.get_corpus_raw('gutenberg', 'austen-emma.txt')
    print(f"\n엠마 원문 일부:\n{emma_raw[:200]}")
    
    # 토큰화 예제
    sentences = nlp.tokenize_sentences(emma_raw[:1000])
    print(f"\n문장 수: {len(sentences)}")
    print(f"첫 번째 문장: {sentences[0] if sentences else 'N/A'}")
    
    words = nlp.tokenize_words(emma_raw[50:100])
    print(f"\n단어 토큰: {words}")
    
    # 형태소 분석 예제
    test_words = ['lives', 'crying', 'flies', 'dying']
    porter_stems = nlp.stem_porter(test_words)
    print(f"\nPorter Stemming: {porter_stems}")
    
    lemmas = nlp.lemmatize(test_words)
    print(f"Lemmatization: {lemmas}")
    
    # POS 태깅 예제
    sentence = "Emma refused to permit us to obtain the refuse permit"
    tokens = nlp.tokenize_words(sentence)
    tagged = nlp.pos_tag(tokens)
    print(f"\nPOS 태깅: {tagged}")
    
    nouns = nlp.extract_pos(tagged, "NN")
    print(f"명사만 추출: {nouns}")
    
    # Text 클래스 예제
    emma_tokens = nlp.tokenize_regex(emma_raw)
    text = nlp.create_text(emma_tokens, name="Emma")
    
    # 빈도 분석 예제
    stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
    fd_names = nlp.extract_names_from_corpus(emma_raw, stopwords)
    
    stats = nlp.get_freq_stats(fd_names, "Emma")
    print(f"\n빈도 통계: {stats}")
    
    most_common = nlp.get_most_common(fd_names, 5)
    print(f"가장 빈번한 단어: {most_common}")
    
    # 워드클라우드 생성 (표시하지 않음)
    # wc = nlp.generate_wordcloud(fd_names, show=False)
