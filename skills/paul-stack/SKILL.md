---
name: paul-stack
description: Paul 의 스택 규약 — pnpm · Biome · TypeScript strict · Next App Router 레이어 패턴 · React Hook Form · 서버별(Hono/Cloudflare vs Fastify/Lambda) 규칙 · changeset. 패키지 설치, 린트/포맷, 타입 체크, 라우트 추가, DTO 추가, 스키마 변경, 배포 관련 작업 시 반드시 참조할 것. npm/yarn 이나 ESLint/Prettier 를 제안하기 전에 먼저 읽는다.
---

# Stack Rules

## Package Manager

**항상 `pnpm`.** `npm`/`yarn` 은 쓰지 않는다.

```bash
pnpm add <pkg> --filter <app-or-package>
```

## Biome

ESLint/Prettier 를 제안하지 않는다. 루트 단일 `biome.json` 이 정본.

```bash
pnpm biome check --write <file>   # 편집 후 실행, 커밋에 포함
```

**예외:** `apps/coldsurf-blog` 는 ESLint + Prettier 를 쓴다.

## TypeScript

- `any` 금지 — 불가피하면 왜 불가피한지 주석을 단다
- strict 모드, 타입 단언(`as`) 최소화
- 타입 체크: `pnpm turbo check:type`

## React / React Native

- 작고 직관적인 컴포넌트, compact 한 props
- RN 은 NewArch(0.73+) 타깃, 불필요한 전역 상태 회피
- 상태는 `useState` 나열이 아니라 **state + 로직을 함께 캡슐화한 커스텀 훅**으로 (`paul-rockstar` 참조)

### Next.js App Router 레이어 패턴

RSC 는 ID/params 만 넘긴다. 데이터 페칭은 Client Component 에서.

```
page.tsx (RSC) → *-page.tsx (useRouter + Suspense) → *-content.tsx (useSuspenseQuery) → *-form/*-view (pure UI)
```

- `*-client` 접미사를 쓰지 않는다 — 역할 기반 이름(`*-page`, `*-screen`, `*-shell`)
- `useRouter` 는 최상위 Client Component 에서만. 아래로는 props 로 내린다

### React Hook Form + 커스텀 Input

커스텀 Input 의 `useImperativeHandle` 은 **`inputRef.current`(실제 HTMLInputElement)를 반환**해야 한다. `{ focus, blur }` 만 노출하면 RHF `defaultValues` 가 깨진다.

우회: `Controller` 를 쓰거나 `value={watch('field')}`.

## 서버 — 두 계열을 혼동하지 않는다

### billets-server — Hono + Cloudflare Workers (Fastify 아님)

- `@hono/zod-openapi`. DTO 는 `packages/data-models/*.dto.ts`(zod), 라우트는 `createRoute` + `app.openapi`(`*.route.ts`), `src/index.ts` 에 `register*Routes(app)` 등록
- 신규 도메인은 `/v2/*`. 템플릿은 `comments.route.ts`. enum import 는 `../generated/prisma/enums`
- **`addSchema` · `codegen:api-sdk` 없음.** dev(`pnpm dev`, workerd) 기동 → `/openapi.json` 을 `packages/api-sdk/openapi.json` 스냅샷으로, `openapi-typescript` 로 `types/api.ts` 생성
- ⚠️ api-sdk 는 Fastify→Hono **마이그레이션 superset**(미이관 auth · event 포함) — live 서버로 **전체 재덤프 금지**. 엔드포인트 추가는 커밋본에 **경로만 외과 삽입**
- 스키마 정본 = `packages/prisma-schema`(+마이그레이션). 3단 sync: prisma-schema → `packages/db`(prisma:sync) → billets-server(prisma:generate)

### coldsurf-studio-server · coldsurf-auth-server — Fastify + AWS Lambda

- OpenAPI spec 을 손으로 고치지 않는다 → `pnpm codegen:api-sdk`
- DTO 추가 시 `server.ts` 의 `addSchema` 배열에도 추가한다
- 라우트 파일은 `*.route.ts`

## Changeset

코드 변경마다 `pnpm changeset`(patch/minor/major). `changeset version` 을 `develop` 에서 직접 돌리지 않는다.

## 자동화 CLI

생산성용 CLI 는 **interactive prompt + TypeScript**. 일반 bash script 보다 `@clack/prompts` 로 사람이 읽을 수 있고 단계가 명확한 방식을 선호한다.

## 완료 전 체크리스트

- [ ] `pnpm biome check --write <changed-files>`
- [ ] `pnpm turbo check:type` 통과
- [ ] 필요하면 changeset 추가
