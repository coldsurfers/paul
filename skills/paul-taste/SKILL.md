---
name: paul-taste
description: Paul 의 취향 — 도구 선택, 파일·심볼 네이밍, 커밋·PR 형식, 커뮤니케이션 톤, 문서화 습관.
when_to_use: '"커밋해줘" · "PR 올려줘" · "이름 뭐로 하지" · "스크립트 만들어줘" · "이 라이브러리 쓸까" · "이거 이름 뭐가 낫나" · "이 도구 써도 되나" 요청. **커밋 메시지나 PR 제목·본문을 쓰기 직전에 반드시.** 파일 · 폴더 · 심볼 이름을 새로 지을 때. CLI · 스크립트를 만들 때. 새 도구나 의존성을 도입할지 판단할 때.'
---

# Paul 의 취향

## 도구

| 선호 | 대신 안 쓰는 것 | 이유 |
|---|---|---|
| pnpm | npm · yarn | 모노레포 워크스페이스 |
| Biome | ESLint · Prettier | 하나로 끝난다 (`apps/coldsurf-blog` 만 예외) |
| `@clack/prompts` + TypeScript | bash script | 사람이 읽을 수 있고 단계가 명확하다 |
| 새 아키텍처 | 구 아키텍처 | RN NewArch, App Router, Workers |
| 자동화 | 반복 수작업 | 손일이 반복되면 CLI 로 만든다 |

**단, 관리 포인트를 늘리는 도입은 하지 않는다.** 새 도구가 하나 늘면 유지 비용이 하나 는다. 그 값을 하는지 먼저 따진다.

## 네이밍

- 파일 · 디렉터리: `kebab-case`
- 컴포넌트 심볼: `PascalCase`, 훅: `use*`
- 역할 기반 접미사: `*-page` · `*-content` · `*-screen` · `*-shell` · `*-view` · `*-form`
- **`*-client` 접미사를 쓰지 않는다** — 무엇을 하는지가 아니라 어디서 도는지를 말하는 이름이라 정보가 없다
- Prisma 모델: `PascalCase` 단수형 + `camelCase` 필드. `snake_case` 로 바꾸자는 제안은 하지 않는다 (`@@map` 안 쓴다)
- Prisma M:N 조인 테이블: `<A>sOn<B>s` — `ConcertsOnArtists` · `UsersOnSubscribedVenues`
- DB 하나를 여러 프로덕트가 쓰면 **모델명 prefix 로 네임스페이스** — `PaulRockstarWork` · `NewsLetterUser`

파일 배치와 접미사 규약(`.types.ts` · `.styled.ts` · 배럴)은 `paul-layout` 에 있다.

## 커밋

**형식:** `<type>(<scope>): <한글 설명>`

- type: `feat` / `fix` / `chore` / `docs` / `refactor` / `test`
- scope: `billets-app` · `billets-server` · `billets-admin` · `web-next` · `ocean-road` 등
- 예: `feat(billets-app): 로그인 플로우 추가`

**규칙**
- 자동 커밋 금지. 작업이 끝났다고 임의로 커밋을 남기지 않는다 — **명시적 요청이 있을 때만**
- `--no-verify` 금지
- pre-push: biome 통과 · 타입 에러 없음 · changeset 추가

## PR

- 제목과 본문 모두 한국어
- feature → `develop`, hotfix → `main`(머지 후 develop 백포트)

## 커뮤니케이션

- **한국어.** 결론 먼저, 근거는 짧게
- 옵션은 제시하되 **결정은 사용자가** 한다. 추천은 하되 실행은 승인 후
- 불명확하면 덮지 말고 무엇이 헷갈리는지 이름 붙여 묻는다
- 과장하지 않는다. 테스트가 깨졌으면 깨졌다고 출력과 함께 말한다
- 사과문 · 자기비판 · 장황한 반성문은 쓰지 않는다. 틀렸으면 고치고 넘어간다

## 문서화

**`specs/` 와 `docs/` 는 다른 축이다.** 섞으면 둘 다 죽는다.

| | `specs/{앱또는패키지}/{기능}.md` | `docs/{주제}.md` (평면) |
|---|---|---|
| 담는 것 | 기능 하나의 실행 계획 | 시스템 설명 · 로드맵 · 워크플로 |
| 앱 종속 | 있다 | 없다 (`deploy-strategy` · `changeset-workflow`) |
| 수명 | 끝나면 죽는다 | 오래 산다 |

Spec 문서의 구조는 `agentic-workflow` 에 있다.

- 인덱스 문서는 *어디에 무엇이 있는가*만 가리키고, 본문은 링크된 문서에서만 관리한다
- 체크리스트는 작업하면서 갱신한다. 몰아서 쓰지 않는다

## 주석

주석은 **무엇을 하는지가 아니라 왜 이렇게 됐는지**를 쓴다. 우회 · 예외 · 남의 코드 사정은 **이유와 범위를 함께** 남긴다 — 다음 사람이 "이거 왜 이래" 로 시간을 쓰지 않게.

```ts
// `_setUserInput` 은 `@clack/core` 에서 protected 라 외부에서 직접 못 부른다.
// Tab 으로 placeholder 를 채울 때만 쓰는 좁은 표면이라 최소 형태로만 노출한다.
```

한국어로 쓴다. 코드를 읽으면 알 수 있는 것은 쓰지 않는다.

## 리뷰

간결하게. 칭찬보다 문제. **지적할 게 없으면 없다고 쓴다** — 채우기 위한 지적을 만들지 않는다.

## 문화적 결

Bandcamp 를 14년 판 사람의 결. 정리된 것보다 **발견되는 것**을 좋아한다. 한국 인디씬의 "다듬어지지 않은 상태" 자체를 문화로 본다. 그래서 프로덕트도 정리해주는 쪽이 아니라 **발견을 돕는 쪽**으로 기운다.
