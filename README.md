# paul

Paul Choi 로서 생각하고, 설계하고, 코딩하기 위한 **Claude Code 하네스**.

에이전트(누가)와 스킬(어떻게)을 분리해 어느 레포에서든 재사용한다. 코드는 없고 마크다운 자산만 있다.

## 구성

```
paul/
├── AGENTS.md                # 이 레포를 편집할 때의 작업 규약
├── CLAUDE.md                # → @AGENTS.md
├── .claude-plugin/
│   ├── plugin.json          # 플러그인 매니페스트
│   └── marketplace.json     # 로컬 마켓플레이스 등록용
├── agents/
│   ├── paul.md              # 메인 — 실제로 만드는 사람
│   ├── paul-planner.md      # Plan · Spec 작성 (읽기 전용)
│   └── paul-reviewer.md     # 코드 리뷰 (읽기 전용)
├── skills/
│   ├── paul-rockstar/       # 페르소나 정본 — 어떻게 생각하는가
│   ├── code-to-product/     # 설계 철학 — 실물의 관점으로 모델링
│   ├── agentic-workflow/    # 요구사항 → Plan → Spec → step → 검증 → 커밋
│   ├── paul-stack/          # 스택 규약 — pnpm · Biome · TS · 앱별 서버 구분
│   ├── coldsurf-domain/     # COLDSURF 도메인 · 로드맵 · 편집 페르소나
│   └── paul-taste/          # 취향 — 도구 · 코드 · 커뮤니케이션
└── commands/
    ├── spec.md              # /paul:spec — 스펙 파일 생성
    └── step.md              # /paul:step — 다음 스텝 실행 + 검증
```

## 설치

```bash
claude plugin marketplace add coldsurfers/paul
claude plugin install paul@paul
```

디바이스가 여러 대라 심볼릭 링크는 쓰지 않는다 — 절대경로가 디바이스마다 달라 깨진다.

### 편집은 즉시 반영되지 않는다

설치본은 `~/.claude/plugins/cache/paul/paul/<version>/` 로 **복사되는 스냅샷**이다. 마켓플레이스를 로컬 경로로 걸어도(`claude plugin marketplace add ~/dev/paul`) 마찬가지 — 라이브가 아니다. 자산을 고쳤으면:

```bash
claude plugin marketplace update paul
claude plugin uninstall paul@paul && claude plugin install paul@paul
```

`claude plugin update` 는 버전 비교라 `plugin.json` 의 `version` 을 올리지 않으면 no-op 이다. 문서만 고칠 때마다 버전을 올릴 게 아니면 재설치가 맞다.

## 스킬 정본 관계

기존 `~/.claude/skills/paul-rockstar/SKILL.md` 는 페르소나 · 로드맵 · 워크플로 · 스택이 한 파일에 섞여 있었다. 이 레포는 그것을 **축별로 쪼갠 것이 정본**이다.

| 축 | 스킬 |
|---|---|
| 어떻게 생각하는가 | `paul-rockstar` |
| 무엇을 어떻게 모델링하는가 | `code-to-product` |
| 어떤 순서로 일하는가 | `agentic-workflow` |
| 무엇으로 만드는가 | `paul-stack` |
| 무엇을 만드는가 | `coldsurf-domain` |
| 어떤 결을 좋아하는가 | `paul-taste` |

설치 후에는 기존 모놀리식 `paul-rockstar` 스킬을 제거해 중복 로딩을 막는다.

## 원칙

- **결정은 사용자에게.** 갈림길이 나오면 옵션을 제시하고 멈춘다.
- **커밋은 명시적 요청이 있을 때만.** 자동 커밋 금지, `--no-verify` 금지.
- **스킬 본문은 500줄 이내.** 넘치면 `references/` 로 내리고 본문엔 포인터만 남긴다.
