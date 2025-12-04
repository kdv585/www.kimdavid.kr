# AWS 배포 스크립트
# 사용법: .\deploy-to-aws.ps1

Write-Host "🚀 AWS 배포 스크립트" -ForegroundColor Green
Write-Host ""

# AWS CLI 확인
$awsInstalled = Get-Command aws -ErrorAction SilentlyContinue
if (-not $awsInstalled) {
    Write-Host "⚠️  AWS CLI가 설치되어 있지 않습니다." -ForegroundColor Yellow
    Write-Host "설치 방법:" -ForegroundColor Yellow
    Write-Host "  winget install Amazon.AWSCLI" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "또는 수동 배포 가이드를 참고하세요: AWS_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
    exit 1
}

# AWS 자격 증명 확인
Write-Host "📋 AWS 자격 증명 확인 중..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ AWS 자격 증명이 설정되지 않았습니다." -ForegroundColor Red
        Write-Host "다음 명령어로 설정하세요: aws configure" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ AWS 자격 증명 확인 완료" -ForegroundColor Green
    Write-Host $identity
} catch {
    Write-Host "❌ AWS 연결 실패" -ForegroundColor Red
    exit 1
}

# Docker 이미지 빌드
Write-Host ""
Write-Host "🔨 Docker 이미지 빌드 중..." -ForegroundColor Cyan
Set-Location ai-server
docker build -t ai-server:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker 빌드 실패" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker 이미지 빌드 완료" -ForegroundColor Green

# ECR 리포지토리 생성 (없는 경우)
Write-Host ""
Write-Host "📦 ECR 리포지토리 확인 중..." -ForegroundColor Cyan
$repoName = "date-course-ai-server"
$region = "ap-northeast-2"

$repoExists = aws ecr describe-repositories --repository-names $repoName --region $region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 ECR 리포지토리 생성 중..." -ForegroundColor Cyan
    aws ecr create-repository --repository-name $repoName --region $region
    Write-Host "✅ ECR 리포지토리 생성 완료" -ForegroundColor Green
} else {
    Write-Host "✅ ECR 리포지토리 존재 확인" -ForegroundColor Green
}

# ECR 로그인
Write-Host ""
Write-Host "🔐 ECR 로그인 중..." -ForegroundColor Cyan
$accountId = (aws sts get-caller-identity --query Account --output text)
$ecrUrl = "$accountId.dkr.ecr.$region.amazonaws.com"
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $ecrUrl

# 이미지 태그 및 푸시
Write-Host ""
Write-Host "📤 이미지 푸시 중..." -ForegroundColor Cyan
$imageTag = "$ecrUrl/$repoName:latest"
docker tag ai-server:latest $imageTag
docker push $imageTag
Write-Host "✅ 이미지 푸시 완료" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 배포 준비 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. AWS Console → App Runner 접속" -ForegroundColor Cyan
Write-Host "2. 'Create service' 클릭" -ForegroundColor Cyan
Write-Host "3. Container registry: Amazon ECR 선택" -ForegroundColor Cyan
Write-Host "4. Image URL: $imageTag" -ForegroundColor Cyan
Write-Host "5. 환경 변수 설정 후 배포" -ForegroundColor Cyan
Write-Host ""
Write-Host "또는 EC2/ECS에 배포할 수 있습니다." -ForegroundColor Yellow

Set-Location ..

