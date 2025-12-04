# 404 에러 해결 가이드

## 도메인 연결 시 404 에러 원인 및 해결

### 🔍 주요 원인

1. **nginx server_name 설정**
   - 현재 `localhost`로 고정되어 있음
   - 도메인 연결 시 실제 도메인으로 변경 필요

2. **Spring Cloud Gateway 라우팅**
   - `/api/auth/**` 경로가 Gateway 라우팅에 명시적으로 설정되지 않음
   - 하지만 OAuthController가 직접 처리하므로 문제 없어야 함

3. **OAuth 리다이렉트 URI 불일치**
   - 환경 변수의 리다이렉트 URI가 실제 도메인과 일치하지 않음

### ✅ 해결 방법

#### 1. nginx 설정 업데이트

**개발 환경** (현재 설정):
```nginx
server_name _;  # 모든 도메인 허용
```

**프로덕션 환경**:
```nginx
server_name your-domain.com www.your-domain.com;
```

또는 `nginx.conf.production` 파일을 사용하세요.

#### 2. 환경 변수 업데이트

도메인 연결 후 `.env` 파일 업데이트:

```bash
# api-server/.env
KAKAO_REDIRECT_URI=https://your-domain.com/api/auth/kakao/callback
NAVER_REDIRECT_URI=https://your-domain.com/api/auth/naver/callback
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback
```

#### 3. OAuth 제공자 콘솔 설정

각 OAuth 제공자 콘솔에서 리다이렉트 URI를 실제 도메인으로 등록:

- **카카오**: https://developers.kakao.com
- **네이버**: https://developers.naver.com
- **구글**: https://console.cloud.google.com

#### 4. HTTPS 설정 (프로덕션)

프로덕션 환경에서는 HTTPS를 사용해야 합니다:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 기타 설정
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 🔧 디버깅 방법

#### 1. 로그 확인

```bash
# nginx 로그
docker logs david-frontend

# API Gateway 로그
docker logs david-api-gateway

# AI Server 로그
docker logs david-ai-server
```

#### 2. 라우팅 확인

```bash
# 등록된 라우트 확인
curl http://your-domain.com/gateway/routes
```

#### 3. 헬스 체크

```bash
# API Gateway
curl http://your-domain.com/gateway/health

# AI Server
curl http://your-domain.com/health
```

### 📝 체크리스트

- [ ] nginx `server_name`이 실제 도메인으로 설정되었는가?
- [ ] OAuth 리다이렉트 URI가 실제 도메인과 일치하는가?
- [ ] OAuth 제공자 콘솔에 실제 도메인 리다이렉트 URI가 등록되었는가?
- [ ] 환경 변수가 올바르게 설정되었는가?
- [ ] HTTPS가 설정되었는가? (프로덕션)
- [ ] 방화벽/보안 그룹에서 포트가 열려있는가?

### 🚨 일반적인 문제

1. **도메인이 nginx로 라우팅되지 않음**
   - DNS 설정 확인
   - 포트 포워딩 확인 (80, 443)

2. **API 요청이 404 반환**
   - `/api` 경로가 올바르게 프록시되는지 확인
   - API Gateway가 실행 중인지 확인

3. **OAuth 콜백 실패**
   - 리다이렉트 URI가 정확히 일치하는지 확인
   - HTTPS/HTTP 프로토콜 일치 확인

