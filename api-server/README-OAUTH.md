# OAuth 인증 설정 가이드

## 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

**⚠️ 보안 주의**: 실제 비밀키는 절대 공개 저장소에 커밋하지 마세요!

```bash
# Kakao OAuth
# 카카오 개발자 콘솔(https://developers.kakao.com)에서 발급받은 키를 입력하세요
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret
KAKAO_REDIRECT_URI=http://localhost:8000/api/auth/kakao/callback

# Naver OAuth
# 네이버 개발자 센터(https://developers.naver.com)에서 발급받은 키를 입력하세요
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
NAVER_REDIRECT_URI=http://localhost:8000/api/auth/naver/callback

# Google OAuth
# Google Cloud Console(https://console.cloud.google.com)에서 발급받은 키를 입력하세요
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
# 프로덕션 환경에서는 강력한 랜덤 문자열을 사용하세요 (최소 32자 이상 권장)
JWT_SECRET=your_strong_random_jwt_secret_key_minimum_32_characters
```

## 주요 변경사항

### 1. 포트 변경
- 원래 설정: `8080` 포트
- 현재 설정: `8000` 포트 (API Gateway 기본 포트)
- **해결**: 모든 `REDIRECT_URI`를 `8000` 포트로 변경했습니다.

### 2. OAuth 엔드포인트

#### Kakao
- 로그인 URL: `GET /api/auth/kakao`
- 콜백 URL: `GET /api/auth/kakao/callback?code={code}`

#### Naver
- 로그인 URL: `GET /api/auth/naver`
- 콜백 URL: `GET /api/auth/naver/callback?code={code}`

#### Google
- 로그인 URL: `GET /api/auth/google`
- 콜백 URL: `GET /api/auth/google/callback?code={code}`

## 사용 방법

### 1. 로그인 URL 가져오기

```bash
# Kakao
curl http://localhost:8000/api/auth/kakao

# Naver
curl http://localhost:8000/api/auth/naver

# Google
curl http://localhost:8000/api/auth/google
```

응답 예시:
```json
{
  "authUrl": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=..."
}
```

### 2. 콜백 처리

사용자가 OAuth 제공자에서 인증을 완료하면, 콜백 URL로 리다이렉트됩니다.
서버는 자동으로:
1. 인증 코드로 액세스 토큰 교환
2. 사용자 정보 조회
3. JWT 토큰 생성 및 반환

응답 예시:
```json
{
  "user": {
    "id": "123456789",
    "email": "user@example.com",
    "name": "홍길동",
    "nickname": "홍길동",
    "provider": "kakao",
    "profileImage": "https://..."
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Kakao 로그인 성공"
}
```

## 구현된 기능

- ✅ Kakao OAuth 인증
- ✅ Naver OAuth 인증
- ✅ Google OAuth 인증
- ✅ JWT 토큰 생성
- ✅ 사용자 정보 조회
- ✅ 에러 처리

## 주의사항

1. **환경 변수**: `.env` 파일을 생성하고 실제 값으로 설정하세요.
2. **리다이렉트 URI**: OAuth 제공자 콘솔에서 등록한 URI와 일치해야 합니다.
3. **JWT Secret**: 프로덕션 환경에서는 강력한 시크릿 키를 사용하세요.
4. **HTTPS**: 프로덕션 환경에서는 HTTPS를 사용하세요.

## 문제 해결

### 에러: "Invalid redirect_uri"
- OAuth 제공자 콘솔에서 등록한 리다이렉트 URI와 일치하는지 확인하세요.
- 현재 설정: `http://localhost:8000/api/auth/{provider}/callback`

### 에러: "Invalid client_id or client_secret"
- 환경 변수가 올바르게 설정되었는지 확인하세요.
- `.env` 파일이 프로젝트 루트에 있는지 확인하세요.

