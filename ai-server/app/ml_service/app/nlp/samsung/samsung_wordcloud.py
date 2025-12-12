import re
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
from konlpy.tag import Okt
import pandas as pd

logger = logging.getLogger(__name__)

class SamsungWordCloud:
    
    
    def __init__(self):
        self.okt = Okt()
        # 기본 경로 설정
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data"
        self.save_path = self.base_path / "save"

    def text_process(self):
        freq_txt = self.find_freq()
        self.draw_wordcloud()
        return {
            '전처리 결과' : '완료',
            'freq_txt' : freq_txt,
        }
        
        # NLTK 데이터 다운로드
    def read_file(self):
        self.okt.pos('삼성전자 글로벌센터 전자사업부' , stem=True)
        fname = self.data_path / 'kr-Report_2018.txt'
        if not fname.exists():
            logger.error(f"파일을 찾을 수 없습니다: {fname}")
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {fname}")
        with open(fname, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.info(f"파일 읽기 완료: {len(text)} 문자")
        return text

    def extract_hangeul(self, text: str):
        temp = text.replace('\n', ' ')
        tokenizer = re.compile("[^ ㄱ-힣]+")
        return tokenizer.sub(' ', temp)
    
    def change_token(self, text: str):
        """텍스트를 공백으로 분리하여 토큰 리스트 반환"""
        return text.split()

    def extract_noun(self):
        # 삼성전자의 스마트폰은 -> 삼성전자 스마트폰
        noun_tokens = []
        tokens = self.change_token(self.extract_hangeul(self.read_file()))
        for i in tokens:
            pos = self.okt.pos(i)
            temp = [j[0] for j in pos if j[1] == 'Noun']
            if len(''.join(temp)) > 1 :
                noun_tokens.append(''.join(temp))
        texts = ' '.join(noun_tokens)
        logger.info(texts[:100])
        return texts

    def read_stopword(self):
        self.okt.pos("삼성전자 글로벌센터 전자사업부", stem=True)
        fname = self.data_path / 'stopwords.txt'
        if not fname.exists():
            logger.warning(f"불용어 파일을 찾을 수 없습니다: {fname}")
            return ""
        with open(fname, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        # 공백으로 분리하여 리스트로 변환
        stopword_list = stopwords.split()
        logger.info(f"불용어 {len(stopword_list)}개 로드 완료")
        return stopword_list

    def remove_stopword(self):
        texts = self.extract_noun()
        tokens = self.change_token(texts)
        stopwords = self.read_stopword()
        # stopwords가 리스트인 경우와 문자열인 경우 모두 처리
        if isinstance(stopwords, str):
            stopwords = stopwords.split()
        # 불용어 제거
        texts = [text for text in tokens
                 if text not in stopwords and len(text) > 1]
        logger.info(f"불용어 제거 후 {len(texts)}개 토큰 남음")
        return texts

    def find_freq(self):
        texts = self.remove_stopword()
        freqtxt = pd.Series(dict(FreqDist(texts))).sort_values(ascending=False)
        logger.info(freqtxt[:30])
        return freqtxt

    def draw_wordcloud(self):
        try:
            texts = self.remove_stopword()
            
            if not texts or len(texts) == 0:
                logger.error("워드클라우드를 생성할 텍스트가 없습니다.")
                raise ValueError("워드클라우드를 생성할 텍스트가 없습니다.")
            
            # save 디렉토리 경로 설정
            self.save_path.mkdir(parents=True, exist_ok=True)
            
            # 폰트 경로 설정
            font_path = self.data_path / "D2Coding.ttf"
            if not font_path.exists():
                logger.warning(f"폰트 파일을 찾을 수 없습니다: {font_path}")
                font_path = None
            
            # 텍스트 결합
            text_for_wordcloud = " ".join(texts)
            logger.info(f"워드클라우드 생성 시작: {len(texts)}개 토큰")
            
            # 워드클라우드 생성
            wcloud = WordCloud(
                font_path=str(font_path) if font_path else None,
                relative_scaling=0.2,
                background_color='white',
                width=1200,
                height=1200,
                max_words=200
            ).generate(text_for_wordcloud)
            
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wordcloud_samsung_{timestamp}.png"
            filepath = self.save_path / filename
            
            # 이미지 저장
            plt.figure(figsize=(12, 12))
            plt.imshow(wcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(filepath, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            logger.info(f"워드클라우드가 저장되었습니다: {filepath}")
            
            return {
                "saved_file": str(filepath),
                "filename": filename,
                "filepath": str(filepath),
                "word_count": len(texts)
            }
        except Exception as e:
            logger.error(f"워드클라우드 생성 실패: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

