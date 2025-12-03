# 데이트코스 추천 AI API

DDD(Domain-Driven Design) 구조로 구현된 데이트코스 추천 AI 서비스입니다.

## 프로젝트 구조

```
api-server/
├── app/
│   ├── domain/              # 도메인 계층
│   │   ├── entities/        # 엔티티
│   │   ├── value_objects/   # 값 객체
│   │   ├── repositories/    # 저장소 인터페이스
│   │   └── services/        # 도메인 서비스 인터페이스
│   ├── application/         # 애플리케이션 계층
│   │   ├── use_cases/       # 유스케이스
│   │   └── dto/             # 데이터 전송 객체
│   ├── infrastructure/      # 인프라 계층
│   │   ├── repositories/    # 저장소 구현
│   │   └── services/        # 외부 서비스 구현
│   └── presentation/        # 프레젠테이션 계층
│       ├── controllers/     # 컨트롤러
│       └── routes/          # 라우팅
├── main.py                  # 애플리케이션 진입점
├── dependencies.py          # 의존성 주입
└── requirements.txt         # 패키지 의존성
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:

```
AI_API_KEY=your_ai_api_key_here
AI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
```

### 4. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 데이트코스 추천

**POST** `/api/v1/date-courses/recommend`

요청 본문:
```json
{
  "preference": {
    "budget": "보통",
    "duration": 180,
    "location": "서울시 강남구",
    "interests": ["카페", "디저트"],
    "weather": "맑음",
    "time_of_day": "오후"
  }
}
```

응답:
```json
{
  "courses": [
    {
      "id": "1",
      "title": "카페 투어",
      "description": "트렌디한 카페들을 돌아보는 코스",
      "location": "서울시 강남구",
      "category": "카페",
      "duration": 180,
      "price_range": "보통",
      "tags": ["카페", "디저트", "인스타그램"],
      "rating": 4.3
    }
  ],
  "count": 1
}
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 아키텍처 설명

### Domain Layer (도메인 계층)
- 비즈니스 로직의 핵심
- 엔티티, 값 객체, 도메인 서비스 인터페이스 정의
- 외부 의존성 없음

### Application Layer (애플리케이션 계층)
- 유스케이스 구현
- 도메인 계층을 조합하여 비즈니스 흐름 구성
- DTO를 통한 데이터 전송

### Infrastructure Layer (인프라 계층)
- 도메인 인터페이스의 구체적 구현
- 데이터베이스, 외부 API 연동
- AI 서비스 구현

### Presentation Layer (프레젠테이션 계층)
- HTTP 요청/응답 처리
- 컨트롤러와 라우팅
- DTO 변환

## 향후 개선 사항

1. 실제 데이터베이스 연동 (PostgreSQL, MongoDB 등)
2. OpenAI API 실제 연동
3. 인증/인가 추가
4. 로깅 및 모니터링
5. 테스트 코드 작성
6. 캐싱 전략 구현

