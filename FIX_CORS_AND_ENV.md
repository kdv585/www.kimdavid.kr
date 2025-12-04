# 🔧 CORS 및 환경 변수 수정

## 문제 1: CORS 에러 ✅ 해결됨
- `application.yml`에 CORS 설정 추가 완료
- API Gateway 재시작 완료

## 문제 2: 잘못된 API URL ❌ 수정 필요

현재 브라우저가 `localhost:8000`으로 요청하고 있습니다.
하지만 **LocalTunnel URL**(`https://old-women-pump.loca.lt`)을 사용해야 합니다!

### Vercel 환경 변수 확인

브라우저에서 Vercel 환경 변수 페이지를 확인하세요:

1. `VITE_API_BASE_URL` 변수가 있는지 확인
2. 값이 `https://old-women-pump.loca.lt`인지 확인
3. **Production** 환경에 체크되어 있는지 확인

### 만약 변수가 없거나 잘못되었다면:

**추가 또는 수정:**
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://old-women-pump.loca.lt`
- **Environments**: `Production` 체크 ✅

**저장 후 반드시 재배포:**

```bash
cd www.kimdavid.kr
vercel --prod --yes
```

## 배포 후 확인

1. 5-10분 대기
2. `https://www.kimdavid.kr` 새로고침
3. 브라우저 개발자 도구 (F12) → Network 탭
4. "추천 받기" 클릭
5. 요청 URL 확인: `https://old-women-pump.loca.lt/api/v1/date-courses/recommend`

## ⚠️ 주의사항

LocalTunnel PowerShell 창이 열려있어야 합니다!
창을 닫으면 API 연결이 끊어집니다.

