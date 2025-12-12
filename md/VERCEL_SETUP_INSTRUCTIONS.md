# ✅ 최종 설정 단계

## LocalTunnel URL
```
https://old-women-pump.loca.lt
```

## Vercel 환경 변수 설정 (브라우저에서)

방금 열린 브라우저 페이지에서:

### 1. 환경 변수 추가
- **Name**: `VITE_API_BASE_URL`
- **Value**: `https://old-women-pump.loca.lt`
- **Environment**: `Production` 체크
- **Save** 클릭

### 2. 재배포
터미널에서 다음 명령어 실행:
```bash
cd www.kimdavid.kr
vercel --prod
```

## 또는 수동 재배포
Vercel 대시보드에서:
1. Deployments 탭
2. 최신 배포의 `...` 메뉴 클릭
3. "Redeploy" 선택
4. "Use existing Build Cache" 체크 해제
5. "Redeploy" 클릭

---

## 완료 후 테스트
5-10분 후:
- https://www.kimdavid.kr 접속
- "추천 받기" 클릭
- 정상 작동 확인! 🎉

## ⚠️ 주의사항
LocalTunnel은 임시 URL입니다:
- PowerShell 창을 닫으면 연결 끊김
- 매번 새 URL이 생성됨
- 프로덕션용으로는 적합하지 않음

프로덕션 배포는 AWS/GCP 등의 클라우드 서버 필요합니다.

