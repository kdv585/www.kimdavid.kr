# 도메인 연결 가이드 (www.kimdavid.kr)

## 🔍 문제 진단

로컬에서는 작동하지만 도메인에서 404 에러가 발생하는 경우, 다음 원인이 있을 수 있습니다:

### 1. DNS 설정 확인

도메인이 올바른 서버 IP를 가리키는지 확인:

```bash
nslookup www.kimdavid.kr
# 또는
nslookup kimdavid.kr
```

**확인 사항:**
- DNS A 레코드가 서버의 공인 IP를 가리켜야 합니다
- TTL(Time To Live) 값에 따라 DNS 전파에 시간이 걸릴 수 있습니다 (최대 48시간)

### 2. 서버 위치 및 접근성

#### A. 로컬 개발 환경 (현재 상황으로 추정)

현재 Docker가 로컬 머신에서 실행 중인 경우:

**문제:**
- `docker-compose.yaml`의 포트 바인딩이 `0.0.0.0:3030->80`입니다
- 이는 로컬호스트에서만 접근 가능합니다
- 외부(도메인)에서는 접근할 수 없습니다

**해결 방법:**

1. **옵션 A: 클라우드 서버에 배포**
   - AWS EC2, GCP, Azure, Digital Ocean 등에 서버 생성
   - Docker 및 애플리케이션 설치
   - 포트 80, 443, 8000 오픈
   - DNS를 서버 공인 IP로 설정

2. **옵션 B: 로컬 포트 포워딩 (개발용)**
   - 라우터에서 포트 포워딩 설정 (80 → 로컬 머신:3030)
   - 공인 IP 확인 및 DNS 설정
   - ⚠️ 보안 위험이 있으므로 프로덕션에는 권장하지 않음

3. **옵션 C: Cloudflare Tunnel 또는 ngrok (개발/테스트용)**
   - 로컬 서버를 안전하게 외부에 노출
   - 임시 도메인 또는 커스텀 도메인 사용 가능

#### B. 클라우드 서버 환경

서버가 이미 클라우드에 있는 경우:

**확인 사항:**
1. 방화벽/보안 그룹 설정
2. 포트 80, 443이 열려있는지
3. nginx가 올바른 포트에서 리스닝하는지

### 3. Docker 컨테이너 포트 설정

#### 현재 설정:
```yaml
frontend:
  ports:
    - "3030:80"  # 호스트 3030 → 컨테이너 80
```

#### 프로덕션 권장 설정:

```yaml
frontend:
  ports:
    - "80:80"    # HTTP
    - "443:443"  # HTTPS (SSL 인증서 설정 후)
```

**수정이 필요한 이유:**
- 도메인은 기본적으로 포트 80(HTTP) 또는 443(HTTPS)으로 접속합니다
- 현재 3030 포트를 사용하므로 `www.kimdavid.kr:3030`으로 접속해야 합니다
- 포트 없이 접속하려면 80/443 포트를 사용해야 합니다

### 4. nginx 설정 업데이트

#### 현재 설정:
```nginx
server_name _;  # 모든 도메인 허용
```

#### 프로덕션 권장 설정:

```nginx
server {
    listen 80;
    server_name www.kimdavid.kr kimdavid.kr;
    
    # HTTP to HTTPS 리다이렉트 (SSL 설정 후)
    # return 301 https://$server_name$request_uri;
    
    # ... 나머지 설정
}
```

### 5. HTTPS/SSL 인증서 설정 (Let's Encrypt)

도메인 연결 후 HTTPS를 위해 SSL 인증서 설정:

```bash
# Certbot 설치 (Ubuntu/Debian)
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d kimdavid.kr -d www.kimdavid.kr

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

## 🚀 단계별 해결 방법

### 현재 상황별 가이드

#### 🔸 시나리오 1: 로컬 개발 중 (추천)

**테스트용으로 도메인 확인만 원하는 경우:**

1. **ngrok 사용** (가장 빠른 방법):
```bash
# ngrok 설치 후
ngrok http 3030
```
- 임시 URL 제공 (예: https://abc123.ngrok.io)
- 실제 도메인 연결은 별도 설정 필요

2. **Cloudflare Tunnel 사용**:
```bash
# cloudflared 설치
cloudflared tunnel --url http://localhost:3030
```

#### 🔸 시나리오 2: 클라우드 서버에 배포 (프로덕션)

**1단계: 서버 준비**
```bash
# 서버 접속
ssh user@your-server-ip

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**2단계: 프로젝트 배포**
```bash
# 프로젝트 업로드 (git 또는 scp)
git clone your-repository
cd david.kr

# docker-compose.yaml 수정 (포트 80으로 변경)
nano docker-compose.yaml

# 실행
docker-compose up -d
```

**3단계: 방화벽 설정**
```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**4단계: DNS 설정**
- 도메인 등록업체(가비아, 후이즈, AWS Route53 등)에서:
  - A 레코드: `@` → 서버 IP
  - A 레코드: `www` → 서버 IP

**5단계: SSL 인증서 설정**
```bash
sudo certbot --nginx -d kimdavid.kr -d www.kimdavid.kr
```

## 📋 체크리스트

### DNS 및 도메인
- [ ] DNS A 레코드가 올바른 IP를 가리킴
- [ ] DNS 전파 완료 (nslookup으로 확인)
- [ ] www와 비-www 모두 설정됨

### 서버 및 네트워크
- [ ] 서버가 외부에서 접근 가능
- [ ] 방화벽/보안 그룹에서 포트 80, 443 오픈
- [ ] 서버의 공인 IP 확인

### Docker 및 애플리케이션
- [ ] 포트 80(또는 443)에 바인딩됨
- [ ] 모든 컨테이너 정상 실행 중
- [ ] nginx 설정이 올바름
- [ ] 도메인이 server_name에 포함됨

### SSL/HTTPS
- [ ] SSL 인증서 발급 및 설치
- [ ] HTTPS 리다이렉트 설정
- [ ] 자동 갱신 설정

## 🔧 즉시 테스트할 수 있는 방법

### 1. 현재 포트로 접속 테스트
```
http://www.kimdavid.kr:3030
```
만약 이것이 작동한다면 → 포트 설정 문제

### 2. DNS 확인
```bash
nslookup www.kimdavid.kr
ping www.kimdavid.kr
```

### 3. 서버 접근성 확인
```bash
# 로컬에서 서버로 연결 테스트
telnet www.kimdavid.kr 80
# 또는
curl -I http://www.kimdavid.kr
```

## 💡 빠른 임시 해결책

### A. 포트 번호 포함하여 접속
현재 설정에서는:
```
http://www.kimdavid.kr:3030
```

### B. docker-compose.yaml 즉시 수정

```yaml
frontend:
  ports:
    - "80:80"   # 3030:80 → 80:80으로 변경
```

변경 후:
```bash
docker-compose down
docker-compose up -d
```

## ⚠️ 중요 참고사항

1. **로컬 개발 환경**에서는 도메인 접속이 불가능합니다
   - 서버를 클라우드에 배포해야 합니다
   
2. **포트 80 사용**:
   - Windows/Mac에서 포트 80은 관리자 권한 필요
   - 이미 다른 서비스가 사용 중일 수 있음

3. **DNS 전파 시간**:
   - DNS 변경 후 전파에 최대 48시간 소요
   - 빠른 확인: https://www.whatsmydns.net

4. **보안**:
   - 프로덕션에서는 반드시 HTTPS 사용
   - 방화벽 설정 필수
   - 환경 변수로 비밀키 관리

