# 한국어 NLP 설정 가이드

## 개요
한국어 텍스트에서 BoW(Bag of Words)를 생성하기 위한 형태소 분석 라이브러리 설정 가이드입니다.

## 추천 라이브러리

### 1. Kiwipiepy (최우선 추천)
- **장점**: 가장 빠름, 설치 간단, 최신 기술
- **단점**: 상대적으로 새로운 라이브러리
- **설치**: `pip install kiwipiepy`

### 2. KoNLPy
여러 형태소 분석기를 포함한 파이썬 패키지:

#### Okt (Open Korean Text)
- **장점**: 빠르고 가벼움, Java 불필요
- **단점**: 정확도가 상대적으로 낮음
- **추천**: 일반적인 텍스트, 빠른 처리 필요 시

#### Mecab
- **장점**: 가장 빠름, 정확도 높음
- **단점**: 설치 복잡 (Windows에서 특히)
- **추천**: 정확도가 중요한 경우
- **설치**: 
  ```bash
  # Windows
  # https://github.com/Pusnow/mecab-ko-msvc 에서 다운로드
  
  # Mac/Linux
  bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
  ```

#### Komoran
- **장점**: 준수한 성능, 커스터마이징 가능
- **단점**: Java 필요
- **추천**: 학습 데이터 추가 필요 시

#### Hannanum
- **장점**: 안정적, 오래된 분석기
- **단점**: 느림
- **추천**: 안정성 우선 시

#### Kkma (Korean Knowledge Morpheme Analyzer)
- **장점**: 상세한 분석
- **단점**: 매우 느림
- **추천**: 정밀한 분석 필요 시

## 설치 방법

### 1단계: 기본 라이브러리 설치

```bash
# requirements.txt를 통한 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install kiwipiepy>=0.17.0
pip install konlpy>=0.6.0
```

### 2단계: Java 설치 (KoNLPy 사용 시)

KoNLPy의 일부 분석기(Mecab 제외)는 Java가 필요합니다:

```bash
# Java 버전 확인
java -version

# Java 미설치 시
# Windows: https://www.oracle.com/java/technologies/downloads/
# Mac: brew install openjdk
# Linux: sudo apt-get install default-jdk
```

### 3단계: 추가 데이터 다운로드 (선택사항)

```python
# konlpy 설치 확인
from konlpy.tag import Okt
okt = Okt()
print(okt.morphs("한국어 형태소 분석"))
```

## 사용 방법

### 기본 사용

```python
from korean_nlp_service import get_korean_nlp_service

# 서비스 초기화 (기본: Kiwi)
nlp = get_korean_nlp_service(analyzer='kiwi')

# 텍스트
text = "삼성전자는 한국의 대표적인 전자제품 제조 회사입니다."

# 형태소 분석
morphs = nlp.morphs(text)
print("형태소:", morphs)

# 명사 추출
nouns = nlp.nouns(text)
print("명사:", nouns)

# BoW 생성
bow = nlp.create_bow_from_nouns(text)
print("BoW:", bow)
```

### 분석기 변경

```python
# Okt 사용
nlp = get_korean_nlp_service(analyzer='okt')

# Mecab 사용 (설치된 경우)
nlp = get_korean_nlp_service(analyzer='mecab')

# Komoran 사용
nlp = get_korean_nlp_service(analyzer='komoran')
```

### 워드클라우드 생성 (자동 적용)

```python
# 한국어 텍스트는 자동으로 형태소 분석 적용
GET http://localhost:8080/api/ml/nlp/data/wordcloud?filename=kr-Report_2018.txt
```

## 품사 태그 설명

### 주요 품사 태그 (Kiwi/KoNLPy 공통)

| 태그 | 의미 | 예시 |
|------|------|------|
| NNG | 일반 명사 | 사람, 컴퓨터, 회사 |
| NNP | 고유 명사 | 삼성, 서울, 한국 |
| NNB | 의존 명사 | 것, 수, 등 |
| VV | 동사 | 하다, 가다, 먹다 |
| VA | 형용사 | 좋다, 크다, 아름답다 |
| MAG | 일반 부사 | 매우, 아주, 너무 |
| JKS | 주격 조사 | 이, 가 |
| JKO | 목적격 조사 | 을, 를 |

### BoW 생성 시 추천 필터

```python
# 명사만
bow = nlp.create_bow(text, pos_filter=['N'])

# 명사 + 동사
bow = nlp.create_bow(text, pos_filter=['N', 'V'])

# 명사 + 동사 + 형용사
bow = nlp.create_bow(text, pos_filter=['N', 'V', 'VA'])
```

## 성능 비교

| 분석기 | 속도 | 정확도 | 설치 난이도 | 추천도 |
|--------|------|--------|-------------|--------|
| Kiwi | ★★★★★ | ★★★★ | ★★★★★ | ★★★★★ |
| Mecab | ★★★★★ | ★★★★★ | ★★ | ★★★★ |
| Okt | ★★★★ | ★★★ | ★★★★★ | ★★★★ |
| Komoran | ★★★ | ★★★★ | ★★★ | ★★★ |
| Hannanum | ★★ | ★★★ | ★★★ | ★★ |
| Kkma | ★ | ★★★★★ | ★★★ | ★★ |

## 트러블슈팅

### 1. Java 관련 오류

```
JPype._jclass.JClass: java.lang.NoClassDefFoundError
```

**해결:**
```bash
# JAVA_HOME 환경 변수 설정
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
```

### 2. Mecab 설치 오류 (Windows)

**해결:**
- https://github.com/Pusnow/mecab-ko-msvc 에서 Windows용 설치파일 다운로드
- 또는 Kiwi 사용 권장

### 3. 형태소 분석 실패

**해결:**
```python
# 폴백 옵션으로 여러 분석기 시도
try:
    nlp = get_korean_nlp_service(analyzer='kiwi')
except:
    try:
        nlp = get_korean_nlp_service(analyzer='okt')
    except:
        # 기본 토큰화 사용
        pass
```

## 지속적 사용 전략

### 1. 환경 변수 설정

`.env` 파일에 추가:
```env
KOREAN_NLP_ANALYZER=kiwi
```

### 2. 컨테이너/Docker 설정

`Dockerfile`에 추가:
```dockerfile
RUN pip install kiwipiepy konlpy
# Java 설치 (KoNLPy용)
RUN apt-get update && apt-get install -y default-jdk
```

### 3. 캐싱 전략

```python
# 분석 결과 캐싱
nlp = KoreanNLPService(use_cache=True)

# BoW 저장/로드
nlp.save_bow(bow, Path("bow_cache.pkl"))
bow = nlp.load_bow(Path("bow_cache.pkl"))
```

### 4. 배치 처리

```python
# 대량 텍스트 처리
texts = [text1, text2, text3, ...]
bows = [nlp.create_bow_from_nouns(text) for text in texts]
```

## 참고 자료

- Kiwipiepy: https://github.com/bab2min/kiwipiepy
- KoNLPy: https://konlpy.org/
- 한국어 형태소 분석기 비교: https://konlpy.org/ko/latest/morph/
- 품사 태그 가이드: https://docs.google.com/spreadsheets/d/1OGAjUvalBuX-oZvZ_-9tEfYD2gQe7hTGsgUpiiBSXI8/

## 라이센스

- Kiwipiepy: LGPLv3
- KoNLPy: GPL v3 or later
- 각 형태소 분석기: 개별 라이센스 확인 필요
