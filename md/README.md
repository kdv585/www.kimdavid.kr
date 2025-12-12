# David.kr - 데이트코스 추천 시스템

DDD 구조로 구현된 데이트코스 추천 AI 시스템입니다.

## 시스템 아키텍처

```
┌─────────────┐
│  Frontend   │ (React + TypeScript)
│  Port: 3000 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ API Gateway │ (Spring Boot + Spring Cloud Gateway)
│  Port: 8000 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  AI Server  │ (Python + FastAPI)
│  Port: 8001 │
└─────────────┘

┌─────────────┐
│    Redis    │ (레이트 리미팅)
│  Port: 6379 │
└─────────────┘
```

## 프로젝트 구조

```
david.kr/
├── api-server/          # API Gateway (Java/Spring Boot)
├── ai-server/           # AI 서버 (Python/FastAPI)
├── www.kimdavid.kr/     # 프론트엔드 (React/TypeScript)
└── docker-compose.yaml  # Docker Compose 설정
```

## 빠른 시작

### Docker Compose로 전체 시스템 실행

```bash
# 프로덕션 모드
docker-compose up -d

# 개발 모드
docker-compose -f docker-compose.dev.yaml up -d
```

### 개별 서비스 실행

#### 1. 프론트엔드

```bash
cd www.kimdavid.kr
pnpm install
pnpm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

#### 2. API Gateway

```bash
cd api-server
mvn clean install
mvn spring-boot:run
```

API Gateway는 `http://localhost:8000`에서 실행됩니다.

#### 3. AI Server

```bash
cd ai-server
pip install -r requirements.txt
python main.py
```

AI Server는 `http://localhost:8001`에서 실행됩니다.

#### 4. Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## 환경 변수

### API Gateway

- `SPRING_REDIS_HOST`: Redis 호스트 (기본값: localhost)
- `SPRING_REDIS_PORT`: Redis 포트 (기본값: 6379)
- `JWT_SECRET`: JWT 시크릿 키

### AI Server

- `AI_API_KEY`: AI API 키
- `AI_MODEL`: AI 모델 (기본값: gpt-4)

### Frontend

- `VITE_API_BASE_URL`: API Gateway URL (기본값: http://localhost:8000)

## API 엔드포인트

### API Gateway

- `GET /` - 게이트웨이 정보
- `GET /gateway/health` - 헬스 체크
- `GET /gateway/routes` - 등록된 라우트 목록

### AI Server (프록시됨)

- `POST /api/v1/date-courses/recommend` - 데이트코스 추천

## 주요 기능

### 프론트엔드
- ✅ 데이트코스 추천 폼
- ✅ 추천 결과 카드 표시
- ✅ 반응형 디자인
- ✅ 로딩 및 에러 처리

### API Gateway
- ✅ 서비스 라우팅
- ✅ JWT 인증
- ✅ 레이트 리미팅
- ✅ 요청 로깅

### AI Server
- ✅ 데이트코스 추천 AI
- ✅ DDD 구조
- ✅ RESTful API

## 기술 스택

### Frontend
- React 18
- TypeScript
- Vite
- Axios

### API Gateway
- Java 17
- Spring Boot 3.2
- Spring Cloud Gateway
- Redis

### AI Server
- Python 3.11
- FastAPI
- Pydantic

## 개발 가이드

### 코드 스타일

- **Java**: Google Java Style Guide
- **Python**: PEP 8
- **TypeScript**: ESLint + Prettier

### 테스트

```bash
# Java 테스트
cd api-server
mvn test

# Python 테스트
cd ai-server
pytest
```

## 배포

### 프로덕션 빌드

```bash
# 프론트엔드
cd www.kimdavid.kr
pnpm run build

# API Gateway
cd api-server
mvn clean package

# Docker 이미지 빌드
docker-compose build
```

## 라이선스

MIT License

