# API Gateway (Java)

DDD(Domain-Driven Design) 구조로 구현된 마이크로서비스 API Gateway입니다.

## 기술 스택

- Java 17
- Spring Boot 3.2.0
- Spring Cloud Gateway
- Spring Data Redis
- JWT (JJWT)
- Maven

## 프로젝트 구조

```
api-server/
├── src/
│   ├── main/
│   │   ├── java/kr/david/gateway/
│   │   │   ├── domain/              # 도메인 계층
│   │   │   │   ├── entity/         # 엔티티
│   │   │   │   ├── valueobject/    # 값 객체
│   │   │   │   ├── repository/     # 저장소 인터페이스
│   │   │   │   └── service/        # 도메인 서비스 인터페이스
│   │   │   ├── application/        # 애플리케이션 계층
│   │   │   │   ├── usecase/        # 유스케이스
│   │   │   │   └── dto/            # 데이터 전송 객체
│   │   │   ├── infrastructure/     # 인프라 계층
│   │   │   │   ├── repository/     # 저장소 구현
│   │   │   │   └── service/        # 외부 서비스 구현
│   │   │   ├── presentation/       # 프레젠테이션 계층
│   │   │   │   ├── controller/     # 컨트롤러
│   │   │   │   └── filter/         # 필터
│   │   │   └── config/             # 설정
│   │   └── resources/
│   │       └── application.yml     # 설정 파일
│   └── test/
└── pom.xml
```

## 주요 기능

### 1. 서비스 라우팅
- Spring Cloud Gateway 기반 라우팅
- 동적 라우트 관리
- 타임아웃 및 재시도 설정

### 2. 인증/인가
- JWT 토큰 기반 인증
- 서비스별 인증 요구사항 설정

### 3. 레이트 리미팅
- Redis 기반 레이트 리미팅
- 인메모리 폴백 지원
- IP/사용자별 요청 제한

### 4. 로깅 및 모니터링
- 요청/응답 로깅
- 요청 ID 추적
- 처리 시간 측정

### 5. 필터
- RequestContextFilter: 요청 컨텍스트 관리
- LoggingFilter: 요청/응답 로깅

## 설치 및 실행

### 1. 요구사항

- Java 17 이상
- Maven 3.6 이상
- Redis (선택사항, 없으면 인메모리 사용)

### 2. 빌드

```bash
cd api-server
mvn clean install
```

### 3. 실행

```bash
mvn spring-boot:run
```

또는

```bash
java -jar target/api-gateway-1.0.0.jar
```

서버는 `http://localhost:8000`에서 실행됩니다.

## 설정

### application.yml

기본 라우트 설정:

- `/api/v1/date-courses/**` → `http://localhost:8001` (ai-server)
- `/health` → `http://localhost:8001/health`

### 환경 변수

- `JWT_SECRET`: JWT 시크릿 키 (기본값: your-secret-key-change-in-production)
- `SPRING_REDIS_HOST`: Redis 호스트 (기본값: localhost)
- `SPRING_REDIS_PORT`: Redis 포트 (기본값: 6379)

## API 엔드포인트

### 게이트웨이 정보

**GET** `/`

게이트웨이 기본 정보 반환

### 헬스 체크

**GET** `/gateway/health`

게이트웨이 상태 확인

### 라우트 목록

**GET** `/gateway/routes`

등록된 모든 라우트 목록 조회

응답 예시:
```json
[
  {
    "name": "ai-server",
    "pathPrefix": "/api/v1/date-courses",
    "targetUrl": "http://localhost:8001",
    "status": "ACTIVE",
    "requiresAuth": false,
    "rateLimit": 100
  }
]
```

### 프록시 요청

모든 등록된 경로는 자동으로 프록시됩니다.

예: `POST /api/v1/date-courses/recommend` → ai-server로 프록시

## 아키텍처 설명

### Domain Layer (도메인 계층)
- **ServiceRoute**: 서비스 라우트 엔티티
- **RequestContext**: 요청 컨텍스트 값 객체
- **인터페이스**: Repository, AuthService, RateLimitService

### Application Layer (애플리케이션 계층)
- **ProxyRequestUseCase**: 프록시 요청 처리 유스케이스

### Infrastructure Layer (인프라 계층)
- **InMemoryServiceRouteRepository**: 인메모리 라우트 저장소
- **JwtAuthService**: JWT 인증 서비스
- **RedisRateLimitService**: Redis 기반 레이트 리미팅
- **InMemoryRateLimitService**: 인메모리 레이트 리미팅 (폴백)

### Presentation Layer (프레젠테이션 계층)
- **GatewayController**: 게이트웨이 컨트롤러
- **RequestContextFilter**: 요청 컨텍스트 필터
- **LoggingFilter**: 로깅 필터

## 향후 개선 사항

1. 서비스 디스커버리 (Eureka, Consul)
2. 로드 밸런싱
3. 서킷 브레이커 패턴 (Resilience4j)
4. 요청/응답 변환 및 검증
5. 메트릭 수집 (Micrometer, Prometheus)
6. 분산 추적 (Sleuth, Zipkin)

