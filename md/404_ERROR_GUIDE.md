# 404 에러 해결 가이드

## 🔍 404 에러 원인 분석

### 1. 포트 매핑 문제 ✅ 해결됨
- **문제**: Docker Compose에서 프론트엔드 포트가 `3030:3030`으로 설정되어 있었지만, nginx는 컨테이너 내부에서 포트 80을 사용
- **해결**: `3030:80`으로 변경

### 2. API 엔드포인트 확인

#### ✅ 정상 작동해야 하는 엔드포인트:

1. **데이트코스 추천**
   - `POST /api/v1/date-courses/recommend`
   - Spring Cloud Gateway → AI Server로 라우팅

2. **OAuth 인증**
   - `GET /api/auth/kakao` - 카카오 로그인 URL
   - `GET /api/auth/naver` - 네이버 로그인 URL
   - `GET /api/auth/google` - 구글 로그인 URL
   - `GET /api/auth/{provider}/callback` - OAuth 콜백

3. **헬스 체크**
   - `GET /gateway/health` - API Gateway 헬스 체크
   - `GET /health` - AI Server 헬스 체크

### 3. 가능한 404 원인

#### A. 정적 파일 (JS, CSS) 404
- **증상**: 브라우저 콘솔에서 `.js`, `.css` 파일이 404
- **원인**: 빌드된 파일이 nginx에 제대로 복사되지 않음
- **해결**:
  ```bash
  docker-compose build frontend
  docker-compose up -d frontend
  ```

#### B. API 요청 404
- **증상**: API 호출 시 404 반환
- **원인**:
  1. API Gateway가 실행되지 않음
  2. Spring Cloud Gateway 라우팅 설정 문제
  3. AI Server가 실행되지 않음
- **해결**:
  ```bash
  # 모든 서비스 상태 확인
  docker-compose ps
  
  # 로그 확인
  docker logs david-api-gateway
  docker logs david-ai-server
  
  # 서비스 재시작
  docker-compose restart api-gateway ai-server
  ```

#### C. 프론트엔드 라우팅 404
- **증상**: 브라우저에서 직접 URL 접근 시 404
- **원인**: nginx의 SPA 라우팅 설정 문제
- **해결**: `nginx.conf`의 `try_files` 설정 확인 (이미 설정됨)

## 🔧 디버깅 방법

### 1. 브라우저 개발자 도구 확인
- **Network 탭**: 어떤 리소스가 404인지 확인
- **Console 탭**: JavaScript 에러 확인

### 2. Docker 로그 확인
```bash
# 프론트엔드 로그
docker logs david-frontend

# API Gateway 로그
docker logs david-api-gateway

# AI Server 로그
docker logs david-ai-server
```

### 3. API 엔드포인트 테스트
```bash
# API Gateway 헬스 체크
curl http://localhost:8000/gateway/health

# AI Server 헬스 체크 (Gateway를 통해)
curl http://localhost:8000/health

# OAuth 엔드포인트 테스트
curl http://localhost:8000/api/auth/kakao
```

### 4. 네트워크 연결 확인
```bash
# 컨테이너 간 네트워크 확인
docker network inspect david-network

# 프론트엔드에서 API Gateway 접근 테스트
docker exec david-frontend wget -O- http://api-gateway:8000/gateway/health
```

## 📝 체크리스트

- [ ] 포트 매핑이 올바른가? (`3030:80`)
- [ ] 모든 컨테이너가 실행 중인가? (`docker-compose ps`)
- [ ] 프론트엔드가 빌드되었는가? (`dist` 폴더 확인)
- [ ] API Gateway가 정상 작동하는가? (`/gateway/health` 확인)
- [ ] AI Server가 정상 작동하는가? (`/health` 확인)
- [ ] Spring Cloud Gateway 라우팅이 설정되었는가? (`application.yml` 확인)
- [ ] nginx 설정이 올바른가? (`nginx.conf` 확인)

## 🚀 빠른 해결 방법

```bash
# 1. 모든 컨테이너 중지
docker-compose down

# 2. 모든 서비스 재빌드
docker-compose build --no-cache

# 3. 모든 서비스 시작
docker-compose up -d

# 4. 로그 확인
docker-compose logs -f
```

## 💡 추가 팁

### 프론트엔드 빌드 확인
```bash
# 프론트엔드 컨테이너 내부 확인
docker exec -it david-frontend sh
ls -la /usr/share/nginx/html
```

### API Gateway 라우팅 확인
```bash
# 등록된 라우트 확인
curl http://localhost:8000/gateway/routes
```

### 환경 변수 확인
```bash
# API Gateway 환경 변수
docker exec david-api-gateway env | grep -E "KAKAO|NAVER|GOOGLE|JWT"
```

