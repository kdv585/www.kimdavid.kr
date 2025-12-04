# Render 배포 가이드 (완전 무료)

## 🎯 Render 장점
- ✅ 완전 무료 (제한적이지만 무료)
- ✅ 자동 HTTPS
- ✅ GitHub 연동으로 자동 배포
- ✅ 환경 변수 관리 쉬움
- ✅ Docker 지원

## 📋 사전 준비

### 1. Render 계정 생성
1. https://render.com 접속
2. "Get Started for Free" 클릭
3. GitHub 계정으로 로그인 (권장)

### 2. GitHub 저장소 준비
- 프로젝트가 GitHub에 푸시되어 있어야 함

---

## 🚀 배포 방법

### 방법 1: Render Dashboard에서 배포 (추천)

1. **Render Dashboard 접속**
   - https://dashboard.render.com 접속
   - 로그인

2. **새 Web Service 생성**
   - "New +" → "Web Service" 클릭
   - "Connect GitHub" 선택
   - 저장소 선택: `david.kr` 또는 `www.kimdavid.kr`

3. **서비스 설정**
   - **Name**: `date-course-ai-server`
   - **Region**: `Singapore` (한국과 가까움)
   - **Branch**: `main`
   - **Root Directory**: `ai-server`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `Dockerfile` (기본값)

4. **환경 변수 설정**
   - "Environment" 섹션에서 추가:
     - `AI_API_KEY`: OpenAI API 키
     - `AI_MODEL`: `gpt-4`
     - `PORT`: `8000` (Render가 자동 설정)

5. **고급 설정 (선택사항)**
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes` (GitHub 푸시 시 자동 배포)

6. **"Create Web Service" 클릭**
   - 배포 시작 (5-10분 소요)

7. **URL 확인**
   - 배포 완료 후 제공되는 URL 확인
   - 예: `https://date-course-ai-server.onrender.com`

---

### 방법 2: render.yaml 사용 (자동화)

프로젝트 루트에 `render.yaml` 파일 생성:

```yaml
services:
  - type: web
    name: date-course-ai-server
    runtime: docker
    plan: free
    dockerfilePath: ./ai-server/Dockerfile
    dockerContext: ./ai-server
    envVars:
      - key: AI_API_KEY
        sync: false  # 수동으로 설정
      - key: AI_MODEL
        value: gpt-4
    healthCheckPath: /health
    autoDeploy: true
```

그리고 Render Dashboard에서:
1. "New +" → "Blueprint"
2. GitHub 저장소 연결
3. `render.yaml` 자동 인식
4. 환경 변수만 설정하고 배포

---

## 🔧 프론트엔드 설정

배포 완료 후:

1. **Render URL 확인**
   - 예: `https://date-course-ai-server.onrender.com`

2. **프론트엔드 코드 수정**
   ```typescript
   // www.kimdavid.kr/src/services/api.ts
   const API_BASE_URL = 'https://date-course-ai-server.onrender.com'
   ```

3. **Vercel 환경 변수 업데이트**
   - Vercel Dashboard → Environment Variables
   - `VITE_API_BASE_URL`: Render URL

---

## ⚠️ Render 무료 티어 제한사항

1. **슬리프 모드**
   - 15분 비활성 시 자동 슬리프
   - 첫 요청 시 깨어나는데 30초~1분 소요
   - 해결: Uptime Robot 등으로 주기적 핑

2. **리소스 제한**
   - CPU: 제한적
   - RAM: 512MB
   - 디스크: 1GB

3. **트래픽 제한**
   - 과도한 트래픽 시 제한 가능

---

## 🔄 자동 깨우기 설정 (선택사항)

### Uptime Robot 사용
1. https://uptimerobot.com 접속
2. 무료 계정 생성
3. "Add New Monitor" 클릭
4. **Monitor Type**: HTTP(s)
5. **URL**: Render 서비스 URL
6. **Monitoring Interval**: 5분
7. 저장

이렇게 하면 5분마다 요청이 가서 슬리프 모드 방지!

---

## 🆘 문제 해결

### 배포 실패
- Dockerfile 경로 확인
- 환경 변수 확인
- 로그 확인: Render Dashboard → Logs

### CORS 에러
- `ai-server/main.py`의 CORS 설정 확인
- Render URL을 `allow_origins`에 추가

### 슬리프 모드
- Uptime Robot 설정
- 또는 유료 플랜 ($7/월)으로 업그레이드

---

## 💰 비용

- **무료 플랜**: 완전 무료 (슬리프 모드 있음)
- **Starter 플랜**: $7/월 (슬리프 모드 없음)

---

## ✅ 배포 체크리스트

- [ ] Render 계정 생성
- [ ] GitHub 저장소 연결
- [ ] Web Service 생성
- [ ] 환경 변수 설정 (AI_API_KEY, AI_MODEL)
- [ ] 배포 완료 대기
- [ ] URL 확인
- [ ] 프론트엔드에 URL 설정
- [ ] 테스트

---

## 🎉 완료!

배포가 완료되면 ngrok 없이도 작동합니다!

