# 포트 충돌 해결 방법

## 포트 3000이 이미 사용 중인 경우

### 방법 1: 기존 프로세스 종료

```powershell
# 포트 3000을 사용하는 프로세스 확인
netstat -ano | findstr :3000

# 프로세스 종료 (PID는 위 명령어 결과에서 확인)
taskkill /PID 10100 /F
taskkill /PID 12240 /F
```

### 방법 2: Docker Compose에서 다른 포트 사용

`docker-compose.yaml` 파일에서 포트를 변경:

```yaml
frontend:
  ports:
    - "3001:3000"  # 호스트 포트를 3001로 변경
```

또는

```yaml
frontend:
  ports:
    - "8080:3000"  # 호스트 포트를 8080으로 변경
```

### 방법 3: 기존 컨테이너 중지

```bash
docker-compose down
```

또는 특정 서비스만 중지:

```bash
docker stop david-frontend
docker rm david-frontend
```

## JWT 키 문제 해결

JWT 키는 최소 32바이트(256 bits)가 필요합니다. 

- ✅ **해결됨**: `JwtAuthService`에서 짧은 키를 자동으로 SHA-256 해시하여 32바이트로 확장하도록 수정했습니다.
- ✅ **해결됨**: 기본 JWT_SECRET 값을 더 긴 문자열로 변경했습니다.

### 환경 변수 설정 (선택사항)

`.env` 파일에 강력한 JWT 시크릿을 설정하세요:

```bash
JWT_SECRET=your-very-long-and-secure-jwt-secret-key-minimum-32-characters-long-for-production-use
```

또는 더 강력한 키 생성:

```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

