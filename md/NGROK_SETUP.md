# 🚀 ngrok 설정 가이드

## 1단계: 회원가입 (브라우저에서)

방금 열린 페이지에서:
- Google 계정으로 로그인 가능
- 또는 이메일로 가입

## 2단계: authtoken 받기

가입 후 자동으로 이동하는 페이지에서:
- **Your Authtoken** 섹션 찾기
- 긴 문자열 복사 (예: `2abc...xyz`)

## 3단계: authtoken 설정

복사한 토큰을 아래 명령어에 붙여넣기:

```bash
cd C:\Users\hi\Documents\david.kr
.\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

## 4단계: ngrok 실행

```bash
.\ngrok.exe http 8000
```

## 5단계: URL 확인

화면에 표시되는 URL 복사:
```
Forwarding: https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

---

## 빠른 가이드

1. 브라우저에서 회원가입
2. authtoken 복사
3. 여기에 붙여넣기
4. 자동으로 설정 및 실행됩니다!

