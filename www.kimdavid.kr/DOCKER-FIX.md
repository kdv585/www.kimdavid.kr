# Docker 빌드 에러 해결 가이드

## 문제
Docker 빌드 시 `Cannot find module '/app/node_modules/typescript/bin/tsc'` 에러 발생

## 원인
- `node_modules`가 설치되지 않음
- `pnpm-lock.yaml` 파일이 없어서 의존성 설치가 제대로 되지 않음

## 해결 방법

### 1. 로컬에서 의존성 설치 (권장)

```bash
cd www.kimdavid.kr
pnpm install
```

이 명령어로 `pnpm-lock.yaml` 파일이 생성됩니다.

### 2. Docker 빌드 재시도

```bash
# 프로젝트 루트에서
docker-compose build frontend

# 또는 전체 빌드
docker-compose build
```

## 수정된 내용

### Dockerfile
- `--frozen-lockfile` 옵션 제거
- `pnpm install`만 사용하여 lockfile이 없어도 작동하도록 수정
- lockfile이 있으면 사용하고, 없으면 생성

### .dockerignore 추가
- 불필요한 파일들이 Docker 이미지에 포함되지 않도록 설정

## 참고
- `pnpm-lock.yaml` 파일을 Git에 커밋하는 것을 권장합니다
- 이렇게 하면 모든 환경에서 동일한 의존성 버전을 사용할 수 있습니다

