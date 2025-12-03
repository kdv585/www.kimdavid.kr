# 데이트코스 추천 프론트엔드

React + TypeScript + Vite로 구현된 데이트코스 추천 웹 애플리케이션입니다.

## 기술 스택

- React 18
- TypeScript
- Vite
- React Router
- Axios
- Zustand (상태 관리)

## 기능

- 데이트코스 추천 폼
  - 위치, 예산, 소요시간 입력
  - 관심사 다중 선택
  - 날씨 및 시간대 선택
- AI 기반 데이트코스 추천
- 추천 결과 카드 형태로 표시
- 반응형 디자인

## 설치 및 실행

### 1. pnpm 설치 (필요한 경우)

```bash
npm install -g pnpm
# 또는
corepack enable
```

### 2. 패키지 설치

```bash
cd www.kimdavid.kr
pnpm install
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 API Gateway URL을 설정하세요:

```
VITE_API_BASE_URL=http://localhost:8000
```

### 4. 개발 서버 실행

```bash
pnpm run dev
```

서버는 `http://localhost:3000`에서 실행됩니다.

### 5. 빌드

```bash
pnpm run build
```

빌드된 파일은 `dist` 디렉토리에 생성됩니다.

## 프로젝트 구조

```
www.kimdavid.kr/
├── src/
│   ├── components/          # 재사용 가능한 컴포넌트
│   │   ├── Layout.tsx
│   │   ├── RecommendationForm.tsx
│   │   └── DateCourseCard.tsx
│   ├── pages/               # 페이지 컴포넌트
│   │   └── HomePage.tsx
│   ├── services/            # API 서비스
│   │   └── api.ts
│   ├── types/               # TypeScript 타입 정의
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
└── package.json
```

## API 연동

프론트엔드는 API Gateway (`http://localhost:8000`)를 통해 백엔드와 통신합니다.

### 주요 API 엔드포인트

- `POST /api/v1/date-courses/recommend` - 데이트코스 추천

## 스타일링

CSS 변수를 사용한 일관된 디자인 시스템을 적용했습니다.

- Primary Color: #6366f1 (Indigo)
- Secondary Color: #8b5cf6 (Purple)
- 반응형 디자인 지원

