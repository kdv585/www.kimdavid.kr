# Docker 한국어 NLP 설정 가이드

## 문제
Docker 컨테이너에서 한국어 형태소 분석이 작동하지 않는 문제:
- KoNLPy(Okt)는 Java가 필요하지만 Dockerfile에 Java가 설치되지 않음
- Kiwipiepy가 설치되어 있지만 import 실패 가능성

## 해결 방법

### 1. Dockerfile 수정 (완료)
Java를 설치하고 JAVA_HOME을 설정했습니다.

### 2. Docker 이미지 재빌드 필요

```bash
# Docker 이미지 재빌드
docker-compose build ai-server

# 또는 전체 재빌드
docker-compose down
docker-compose build
docker-compose up -d
```

### 3. 확인 방법

컨테이너 내에서 확인:
```bash
# 컨테이너 접속
docker exec -it <container_name> bash

# Java 확인
java -version

# Python에서 테스트
python -c "from kiwipiepy import Kiwi; k=Kiwi(); print(k.tokenize('한국어 테스트'))"
python -c "from konlpy.tag import Okt; o=Okt(); print(o.morphs('한국어 테스트'))"
```

## 우선순위

1. **Kiwipiepy** (Java 불필요) - 가장 빠르고 권장
2. **KoNLPy Okt** (Java 필요) - 폴백 옵션

## 로그 확인

성공 시:
```
Kiwi 형태소 분석기 로드 성공
한국어 형태소 분석 완료: XXX개 단어
```

실패 시:
```
Kiwipiepy가 설치되지 않았습니다. Okt로 대체합니다.
한국어 형태소 분석 실패, 기본 토큰화 사용: ...
```
