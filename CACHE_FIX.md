# 🔥 브라우저 캐시 문제 해결

## 문제:
브라우저가 오래된 JavaScript 파일을 캐시하고 있어서,
새로 배포한 버전(ngrok URL 포함)이 로드되지 않고 있습니다.

## 해결 방법:

### 방법 1: 시크릿 모드 (가장 확실!)
1. **Ctrl + Shift + N** (Chrome/Edge)
2. 시크릿 창에서 `https://www.kimdavid.kr` 접속
3. 추천 받기 테스트

### 방법 2: 하드 리프레시
1. **Ctrl + Shift + R** (또는 Ctrl + F5)
2. F12 → Application 탭 → Storage → Clear site data
3. 페이지 새로고침

### 방법 3: 캐시 삭제
1. **Ctrl + Shift + Delete**
2. "Cached images and files" 체크
3. "Clear data" 클릭
4. 페이지 새로고침

## 확인 방법:

F12 → Network 탭에서:
- 요청 URL이 `https://acronychal-trena-genially.ngrok-free.dev/...`로 가는지 확인
- `localhost:8000`이면 캐시가 아직 남아있음!

## 시크릿 모드에서 테스트하세요!

