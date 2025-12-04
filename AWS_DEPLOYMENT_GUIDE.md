# AWS 배포 가이드

## 🚀 배포 옵션

### 옵션 1: AWS App Runner (가장 간단) ⭐ 추천
- 자동 스케일링
- HTTPS 자동 제공
- Docker 이미지 직접 배포 가능

### 옵션 2: EC2 + Docker
- 완전한 제어
- 비용 효율적
- 수동 설정 필요

### 옵션 3: ECS Fargate
- 서버리스 컨테이너
- 자동 스케일링
- ECR 필요

---

## 📋 사전 준비

### 1. AWS 계정 생성
- https://aws.amazon.com 접속
- 계정 생성 및 로그인

### 2. AWS CLI 설치 (선택사항)
```powershell
# Windows용 AWS CLI 설치
winget install Amazon.AWSCLI
```

### 3. AWS 자격 증명 설정
```powershell
aws configure
# Access Key ID 입력
# Secret Access Key 입력
# Region: ap-northeast-2 (서울)
# Output format: json
```

---

## 🎯 방법 1: AWS App Runner 배포 (추천)

### 1단계: Docker 이미지 준비
```powershell
# 로컬에서 이미지 빌드
cd ai-server
docker build -t ai-server:latest .
```

### 2단계: AWS App Runner 콘솔에서 배포
1. AWS Console → App Runner 접속
2. "Create service" 클릭
3. "Container registry" 선택
4. "Amazon ECR" 또는 "Docker Hub" 선택
5. 이미지 URL 입력
6. 서비스 이름: `date-course-ai-server`
7. 포트: `8000`
8. 환경 변수 설정:
   - `AI_API_KEY`: OpenAI API 키
   - `AI_MODEL`: `gpt-4`
9. "Create & deploy" 클릭

### 3단계: URL 확인
- 배포 완료 후 제공되는 URL 사용
- 예: `https://xxxxx.ap-northeast-2.awsapprunner.com`

---

## 🎯 방법 2: EC2 배포

### 1단계: EC2 인스턴스 생성
1. AWS Console → EC2
2. "Launch Instance" 클릭
3. AMI: Ubuntu 22.04 LTS
4. Instance type: t3.small (최소)
5. Key pair 생성/선택
6. Security Group 설정:
   - SSH (22): 내 IP만
   - HTTP (8000): 0.0.0.0/0 (또는 Vercel IP만)
7. "Launch Instance"

### 2단계: EC2 접속 및 설정
```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# Docker 설치
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker

# 프로젝트 클론
git clone https://github.com/your-repo/david.kr.git
cd david.kr/ai-server

# 환경 변수 설정
nano .env
# AI_API_KEY=your-key
# AI_MODEL=gpt-4

# Docker 실행
docker build -t ai-server .
docker run -d -p 8000:8000 --env-file .env ai-server
```

### 3단계: Nginx 리버스 프록시 (선택사항)
```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/ai-server

# 설정 내용:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

sudo ln -s /etc/nginx/sites-available/ai-server /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 보안 설정

### API 키 보호
- 환경 변수로만 관리
- `.env` 파일은 `.gitignore`에 추가
- AWS Secrets Manager 사용 권장

### 네트워크 보안
- Security Group에서 필요한 IP만 허용
- Vercel IP 범위만 허용 가능:
  - https://vercel.com/docs/security/deployment-protection#ip-allowlist

---

## 📝 프론트엔드 설정

배포 후 AWS URL을 프론트엔드에 설정:

```typescript
// www.kimdavid.kr/src/services/api.ts
const API_BASE_URL = 'https://your-aws-url.com'
```

Vercel 환경 변수:
- `VITE_API_BASE_URL`: AWS URL

---

## 💰 비용 예상

- **App Runner**: 약 $0.007/시간 (~$5/월)
- **EC2 t3.small**: 약 $0.0208/시간 (~$15/월)
- **ECS Fargate**: 약 $0.04/vCPU/시간 (~$30/월)

---

## 🆘 문제 해결

### Health check 실패
- Security Group에서 포트 8000 허용 확인
- `/health` 엔드포인트 확인

### CORS 에러
- `main.py`의 CORS 설정 확인
- AWS URL을 `allow_origins`에 추가

---

## 📞 다음 단계

1. AWS 계정 생성
2. 배포 방법 선택 (App Runner 추천)
3. 배포 후 URL 확인
4. 프론트엔드에 URL 설정

