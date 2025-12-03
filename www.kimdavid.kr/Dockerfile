FROM node:20-alpine AS build

# pnpm 설치
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# 패키지 파일 복사
COPY package.json pnpm-lock.yaml* ./

# 의존성 설치 (빌드에 필요한 devDependencies 포함)
# lockfile이 있으면 사용하고, 없으면 생성
RUN pnpm install

# 소스 코드 복사 및 빌드
COPY . .
RUN pnpm run build

# 프로덕션 이미지
FROM nginx:alpine

# 빌드된 파일을 nginx에 복사
COPY --from=build /app/dist /usr/share/nginx/html

# nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]

