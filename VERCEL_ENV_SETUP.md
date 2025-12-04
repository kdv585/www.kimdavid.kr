# Vercel 환경 변수 설정 가이드

## 현재 문제
프론트엔드는 Vercel에 배포되었지만, API 서버는 로컬에만 있어서 Network Error 발생

## 해결 방법

### 옵션 1: 로컬 API를 인터넷에 공개 (ngrok)

1. **ngrok 다운로드 및 설치**
   - https://ngrok.com/download
   - 다운로드 후 압축 해제

2. **ngrok 실행**
   ```bash
   # API Gateway 포트(8000)를 공개
   ngrok http 8000
   ```

3. **ngrok URL 복사**
   - 예: `https://abc123.ngrok.io`

4. **Vercel 환경 변수 설정**
   - https://vercel.com/dashboard
   - 프로젝트 선택 → Settings → Environment Variables
   - 추가:
     - Name: `VITE_API_BASE_URL`
     - Value: `https://abc123.ngrok.io` (ngrok URL)
     - Environment: Production 선택

5. **재배포**
   ```bash
   cd www.kimdavid.kr
   vercel --prod
   ```

### 옵션 2: Mock 데이터로 테스트

API 없이 프론트엔드만 테스트하고 싶다면, 프론트엔드 코드를 수정하여 mock 데이터를 사용하도록 설정할 수 있습니다.

### 옵션 3: API 서버도 Vercel에 배포

Java API를 Vercel에 배포할 수 없으므로, AWS, GCP, Heroku, Railway 등에 배포해야 합니다.

## 추천 방법

**지금 당장**: ngrok 사용 (5분 소요)
**프로덕션**: 클라우드 서버에 API 배포

