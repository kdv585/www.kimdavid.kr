# 설정 가이드

## 에러 해결 방법

현재 TypeScript 에러는 `node_modules`가 설치되지 않아서 발생합니다.

### 해결 방법

1. **pnpm 설치 (필요한 경우)**
   ```bash
   npm install -g pnpm
   # 또는
   corepack enable
   ```

2. **의존성 설치**
   ```bash
   cd www.kimdavid.kr
   pnpm install
   ```

3. **설치 후 확인**
   - `node_modules` 폴더가 생성되었는지 확인
   - TypeScript 에러가 사라졌는지 확인

4. **여전히 에러가 발생하는 경우**
   ```bash
   # 캐시 삭제 후 재설치
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

## 파일 수정 사항

### ✅ 수정 완료
- `package.json`: `@types/node` 추가
- `tsconfig.node.json`: 설정 최적화
- `vite.config.ts`: ESM 호환 방식으로 수정
- `tsconfig.json`: references 제거 (composite 충돌 해결)

### 📝 참고
- `vite.config.ts`의 에러는 `pnpm install` 실행 후 자동으로 해결됩니다.
- 모든 필요한 타입 정의는 `@types/node`에 포함되어 있습니다.
- 이 프로젝트는 **pnpm**을 사용합니다.

