# paul

Paul Choi 로서 생각하고, 설계하고, 코딩하기 위한 **Claude Code 하네스**.

축 하나에 스킬 하나로 쪼개 어느 레포에서든 재사용한다. 코드는 없고 마크다운 자산만 있다.

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
│   ├── validate.yml         # PR·push → 자산 형식 · 훅 동작 · version bump 검사
│   └── release.yml          # main 머지 → 해당 버전 태그로 릴리스 노트 발행
├── scripts/
│   ├── validate-assets.py   # frontmatter · 매니페스트 · README 정합 검사
│   └── setup-settings.js    # 기기별 ~/.claude/settings.json 을 규범이 요구하는 상태로
├── hooks/
│   ├── hooks.json           # SessionStart 훅 등록
│   └── inject-norms.js      # NORMS.md 를 컨텍스트로 주입
└── skills/
    ├── paul-rockstar/       # 페르소나 정본 — 어떻게 생각하는가
    ├── code-to-product/     # 설계 철학 — 실물의 관점으로 모델링
    ├── paul-layout/         # 코드 배치 — 디렉터리 · 배럴 · 슬라이스 · 경계
    ├── paul-react/          # 컴포넌트 작성 — 메모 · 슬롯 · 껍데기 · 스타일
    ├── paul-react-native/   # RN 고유 — 리스트 선택 · NativeWind 함정 · 픽셀 검증
    ├── paul-review/         # 코드 리뷰 — 렌즈 · 필수/권고 · 출력 형식
    ├── paul-review-fix/     # 리뷰 반영 — 가르기 · 반영 단위 · 되짚기(커밋 링크)
    ├── agentic-workflow/    # 요구사항 → Plan → Spec → step → 검증 → 커밋
    ├── paul-stack/          # 스택 규약 — pnpm · Biome · TS · 앱별 서버 구분
    ├── paul-taste/          # 취향 — 도구 · 코드 · 커뮤니케이션
    ├── writing-voice/       # 글의 문체 — KO 3종 voice · EN 평론 톤 · 금지 목록
    ├── paul-music/          # 음악 취향 — 무엇을 듣고 어떻게 고르는가
    ├── stage-voice/         # 공연 · 문화예술 짧은 표면 — 메일링 · SNS 말투
    ├── grill/               # /paul:grill — 결정을 라운드로 심문 (사용자 호출 전용)
    ├── spec/                # /paul:spec — 스펙 파일 생성 (사용자 호출 전용)
    ├── step/                # /paul:step — 다음 스텝 실행 + 검증 (사용자 호출 전용)
    ├── reply-review/        # /paul:reply-review — PR 코멘트 답글 (사용자 호출 전용)
    └── like-gpt/            # /paul:like-gpt — 압축된 문장을 풀어 다듬기 (사용자 호출 전용)
```

스킬은 두 종류다. 위 열은 **모델이 상황을 보고 자동으로 부른다.** `grill` · `spec` · `step` · `reply-review` · `like-gpt` 는 `disable-model-invocation: true` 를 달아 **사용자가 `/` 로 칠 때만** 열린다 — 파일을 쓰거나 남의 PR 에 글을 남기거나, 정해진 지점에서 멈추는 절차라 발동 시점을 사람이 쥐어야 한다.

셋은 이어진다.

```
/paul:grill  결정을 뽑는다        → 아무것도 안 씀
/paul:spec   결정을 문서로 굳힌다  → specs/ 에 씀
/paul:step   문서대로 실행한다     → 코드를 씀
```

**에이전트는 없다.** 있던 셋(`paul` · `paul-planner` · `paul-reviewer`)은 전부 스킬로 흡수됐다 — 본문이 스킬의 재기술이었고, 사용자가 지목해야만 열리는 게 손해였다. 판단 기준은 AGENTS.md 「에이전트를 다시 만들 때」에 있다.

## 설치

```bash
claude plugin marketplace add coldsurfers/paul
claude plugin install paul@paul

node scripts/setup-settings.js   # 기기별 전역 설정 (아래)

claude plugin update paul@paul   # 나중에 최신으로
```

디바이스가 여러 대라 심볼릭 링크는 쓰지 않는다 — 절대경로가 디바이스마다 달라 깨진다.

설치하면 `NORMS.md` 가 **모든 레포의 매 세션에** 자동 주입된다.

### 기기별 전역 설정 — 왜 한 줄이 더 필요한가

플러그인이 실을 수 있는 건 스킬 · 훅 · 명령까지고, **`~/.claude/settings.json` 은 못 건드린다.** 그런데 NORMS §4.5 는 3스텝 이상 작업에 `TaskCreate` 체크리스트를 요구하고, 그 툴은 `env.CLAUDE_CODE_ENABLE_TODO_TOOLS` 가 있어야 세션에 올라온다. 규범만 주입되고 툴이 없으면 **조용히 안 지켜진다.**

`scripts/setup-settings.js` 가 그 키만 병합한다. 몇 번을 돌려도 결과가 같고, 기존 키 · 파일 퍼미션은 건드리지 않는다. 설정 watcher 가 집어가므로 **실행 중인 세션에도 바로 붙는다.**

레포를 클론하지 않은 기기라면 설치 캐시에서 그대로 돌린다.

```bash
node ~/.claude/plugins/cache/paul/paul/*/scripts/setup-settings.js
```

### 새 기기에서

위가 전부다. 다만 이 레포 이전의 설정이 남아 있는 기기라면 **중복 로딩되므로 아래를 지운다.**

```bash
rm -rf ~/dotfiles/.agents/skills/paul-rockstar   # 축 분리 전 모놀리식 스킬
rm -f  ~/.claude/skills/paul-rockstar            # 위를 가리키던 심볼릭 링크
rm -f  ~/dotfiles/AGENTS.md                      # NORMS.md 로 이관됨
```

`~/.claude/settings.json` 에 `paul-rockstar/SKILL.md` 를 읽는 `SessionStart` 훅이 있으면 함께 지운다 — 플러그인 훅과 겹친다.

확인:

```bash
cd /tmp && claude -p "<paul-norms> 블록 있나? TaskCreate 툴 쓸 수 있나?"
```

레포 밖에서 물어야 의미가 있다. 이 레포 안에서는 `CLAUDE.md → AGENTS.md → @NORMS.md` 로도 들어오므로 훅이 죽어도 붙어 보인다. 둘 다 있어야 §4.5 가 실제로 지켜진다 — 규범은 훅이, 툴은 설정이 대는 것이라 한쪽만 살아도 티가 안 난다.

자산을 고칠 때의 반영 절차는 AGENTS.md 4장에 있다.

## 스킬 정본 관계

기존 `~/.claude/skills/paul-rockstar/SKILL.md` 는 페르소나 · 로드맵 · 워크플로 · 스택이 한 파일에 섞여 있었다. 이 레포는 그것을 **축별로 쪼갠 것이 정본**이다.

| 축 | 스킬 |
|---|---|
| 어떻게 생각하는가 | `paul-rockstar` |
| 무엇을 어떻게 모델링하는가 | `code-to-product` |
| 코드를 어디에 두는가 | `paul-layout` |
| 컴포넌트 안에 무엇을 쓰는가 | `paul-react` |
| 네이티브라서 무엇이 다른가 | `paul-react-native` |
| 남의 코드를 어떻게 보는가 | `paul-review` |
| 리뷰를 어떻게 반영하는가 | `paul-review-fix` |
| 어떤 순서로 일하는가 | `agentic-workflow` |
| 무엇으로 만드는가 | `paul-stack` |
| 어떤 결을 좋아하는가 | `paul-taste` |
| 어떤 문장으로 쓰는가 | `writing-voice` |

기존 모놀리식 스킬 제거는 「새 기기에서」에 있다.

## 원칙

- **결정은 사용자에게.** 갈림길이 나오면 옵션을 제시하고 멈춘다.
- **커밋은 명시적 요청이 있을 때만.** 자동 커밋 금지, `--no-verify` 금지.
- **스킬 본문은 500줄 이내.** 넘치면 `references/` 로 내리고 본문엔 포인터만 남긴다.
