# paul

Paul Choi 로서 생각하고, 설계하고, 코딩하기 위한 **Claude Code 하네스**.

에이전트(누가)와 스킬(어떻게)을 분리해 어느 레포에서든 재사용한다. 코드는 없고 마크다운 자산만 있다.

## 구성

```
paul/
├── NORMS.md                 # 전역 행동 규범 — 매 세션 주입되는 정본
├── AGENTS.md                # 이 레포를 편집할 때의 작업 규약 (+ @NORMS.md)
├── CLAUDE.md                # → @AGENTS.md
├── .claude-plugin/
│   ├── plugin.json          # 플러그인 매니페스트 — version 이 릴리스 태그가 된다
│   └── marketplace.json     # 로컬 마켓플레이스 등록용
├── .github/workflows/
│   └── release.yml          # main 머지 → 해당 버전 태그로 릴리스 노트 발행
├── hooks/
│   ├── hooks.json           # SessionStart 훅 등록
│   └── inject-norms.js      # NORMS.md 를 컨텍스트로 주입
├── agents/
│   ├── paul.md              # 메인 — 실제로 만드는 사람
│   ├── paul-planner.md      # Plan · Spec 작성 (읽기 전용)
│   └── paul-reviewer.md     # 코드 리뷰 (읽기 전용)
└── skills/
    ├── paul-rockstar/       # 페르소나 정본 — 어떻게 생각하는가
    ├── code-to-product/     # 설계 철학 — 실물의 관점으로 모델링
    ├── agentic-workflow/    # 요구사항 → Plan → Spec → step → 검증 → 커밋
    ├── paul-stack/          # 스택 규약 — pnpm · Biome · TS · 앱별 서버 구분
    ├── coldsurf-domain/     # COLDSURF 도메인 · 로드맵 · 편집 페르소나
    ├── paul-taste/          # 취향 — 도구 · 코드 · 커뮤니케이션
    ├── spec/                # /paul:spec — 스펙 파일 생성 (사용자 호출 전용)
    └── step/                # /paul:step — 다음 스텝 실행 + 검증 (사용자 호출 전용)
```

스킬은 두 종류다. 위 여섯은 **모델이 상황을 보고 자동으로 부른다.** `spec` · `step` 은 `disable-model-invocation: true` 를 달아 **사용자가 `/` 로 칠 때만** 열린다 — 파일을 쓰고, 정해진 지점에서 멈추는 절차라 발동 시점을 사람이 쥐어야 한다.

## 설치

```bash
claude plugin marketplace add coldsurfers/paul
claude plugin install paul@paul

claude plugin update paul@paul   # 나중에 최신으로
```

디바이스가 여러 대라 심볼릭 링크는 쓰지 않는다 — 절대경로가 디바이스마다 달라 깨진다.

설치하면 `NORMS.md` 가 **모든 레포의 매 세션에** 자동 주입된다. 기기별 `settings.json` 설정은 필요 없다.

### 새 기기에서

위 두 줄이 전부다. 다만 이 레포 이전의 설정이 남아 있는 기기라면 **중복 로딩되므로 아래를 지운다.**

```bash
rm -rf ~/dotfiles/.agents/skills/paul-rockstar   # 축 분리 전 모놀리식 스킬
rm -f  ~/.claude/skills/paul-rockstar            # 위를 가리키던 심볼릭 링크
rm -f  ~/dotfiles/AGENTS.md                      # NORMS.md 로 이관됨
```

`~/.claude/settings.json` 에 `paul-rockstar/SKILL.md` 를 읽는 `SessionStart` 훅이 있으면 함께 지운다 — 플러그인 훅과 겹친다.

확인:

```bash
cd /tmp && claude -p "<paul-norms> 블록 있나?"
```

레포 밖에서 물어야 의미가 있다. 이 레포 안에서는 `CLAUDE.md → AGENTS.md → @NORMS.md` 로도 들어오므로 훅이 죽어도 붙어 보인다.

자산을 고칠 때의 반영 절차는 AGENTS.md 4장에 있다.

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

기존 모놀리식 스킬 제거는 「새 기기에서」에 있다.

## 원칙

- **결정은 사용자에게.** 갈림길이 나오면 옵션을 제시하고 멈춘다.
- **커밋은 명시적 요청이 있을 때만.** 자동 커밋 금지, `--no-verify` 금지.
- **스킬 본문은 500줄 이내.** 넘치면 `references/` 로 내리고 본문엔 포인터만 남긴다.
