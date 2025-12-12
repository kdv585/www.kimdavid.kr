# 타이타닉 API 디버깅 가이드

## 문제 상황
- API Gateway를 통해 `/titanic/data` 요청 시 500 에러 발생
- API Gateway 로그에 Reactor 스택 트레이스 표시

## 해결 방법

### 1. AI Server에 직접 요청 (우회 테스트)
Docker Compose 설정에 따르면 AI Server는 포트 8001로 매핑되어 있습니다.

**POSTMAN에서 직접 테스트:**
```
GET http://localhost:8001/titanic/data?limit=10
```

이렇게 하면 API Gateway를 우회하고 AI Server에 직접 요청할 수 있습니다.

### 2. API Gateway 재시작
```bash
docker-compose restart api-gateway
```

### 3. AI Server 로그 확인
```bash
docker-compose logs -f ai-server
```

### 4. 전체 재시작
```bash
docker-compose down
docker-compose up -d
```

## 가능한 원인

1. **AI Server가 응답을 제대로 반환하지 못함**
   - AI Server 로그를 확인하여 실제 에러 확인

2. **API Gateway의 Rate Limiter 문제**
   - Rate Limiter가 Redis에 의존하는데 Redis 연결 문제일 수 있음

3. **응답 형식 문제**
   - AI Server의 응답 형식이 API Gateway가 기대하는 형식과 다를 수 있음

## 다음 단계

1. 먼저 `http://localhost:8001/titanic/data?limit=10`로 직접 테스트
2. 작동하면 API Gateway 문제, 작동하지 않으면 AI Server 문제
3. AI Server 로그에서 실제 에러 메시지 확인
