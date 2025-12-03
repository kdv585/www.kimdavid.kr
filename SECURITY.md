# 보안 가이드

## 환경 변수 보안

### ⚠️ 중요 사항

1. **절대 실제 비밀키를 코드에 하드코딩하지 마세요**
2. **`.env` 파일은 절대 Git에 커밋하지 마세요**
3. **프로덕션 환경에서는 강력한 비밀키를 사용하세요**

## 보안 체크리스트

### ✅ 완료된 보안 조치

- [x] 루트 `.gitignore`에 `.env` 파일 추가
- [x] 각 서브 디렉토리 `.gitignore`에 `.env` 추가
- [x] `.env.example` 파일 생성 (비밀키 없이)
- [x] README에서 실제 비밀키 제거
- [x] OAuthController에서 하드코딩된 Client ID 제거

### 🔒 보안 권장사항

#### 1. JWT Secret 생성

```bash
# 강력한 JWT Secret 생성 (32자 이상 권장)
openssl rand -base64 32
```

#### 2. 환경 변수 관리

- 개발 환경: `.env` 파일 사용
- 프로덕션 환경: 환경 변수 또는 시크릿 관리 시스템 사용
  - AWS Secrets Manager
  - HashiCorp Vault
  - Kubernetes Secrets
  - Docker Secrets

#### 3. OAuth 비밀키 관리

각 OAuth 제공자에서 발급받은 실제 비밀키를 `.env` 파일에 저장:

```bash
# api-server/.env
KAKAO_CLIENT_ID=실제_발급받은_키
KAKAO_CLIENT_SECRET=실제_발급받은_비밀키
# ... 기타 설정
```

#### 4. Git 보안

```bash
# 이미 커밋된 .env 파일이 있다면 제거
git rm --cached .env
git commit -m "Remove .env file from repository"

# Git 히스토리에서 완전히 제거 (필요한 경우)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

#### 5. 코드 스캔

```bash
# 민감한 정보 검색
grep -r "CLIENT_SECRET\|API_KEY\|PASSWORD" --exclude-dir=node_modules --exclude-dir=target
```

## 누출된 비밀키 대응

만약 비밀키가 공개 저장소에 노출되었다면:

1. **즉시 비밀키 재발급**
   - 카카오: https://developers.kakao.com
   - 네이버: https://developers.naver.com
   - 구글: https://console.cloud.google.com

2. **Git 히스토리에서 제거** (위 참고)

3. **모든 환경의 비밀키 교체**

4. **보안 감사 수행**

## 추가 보안 권장사항

1. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS 사용
2. **CORS 설정**: 허용된 도메인만 접근 가능하도록 설정
3. **레이트 리미팅**: API 남용 방지
4. **로깅**: 민감한 정보는 로그에 기록하지 않기
5. **정기 업데이트**: 의존성 패키지 정기 업데이트

