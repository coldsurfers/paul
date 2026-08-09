# AGENTS.md

`paul` 하네스 레포에서 작업할 때의 규약.

**이 레포엔 코드가 없다.** Claude Code 하네스 자산 — 에이전트(누가) · 스킬(어떻게) · 커맨드(무엇을) — 마크다운만 있다. 그래서 "돌아간다"는 검증이 없고, 대신 **다음 세션의 에이전트가 이 문서를 읽고 올바르게 행동하는가**가 검증이다.

전역 행동 규범의 정본은 `NORMS.md` 다 — 이 레포가 소유하고, `hooks/` 가 매 세션 주입한다. 이 문서는 그것을 이 레포 맥락으로 좁힌 것이고, 충돌하면 이 문서가 이긴다.

이 레포의 톤: 한국어, 단문, `—` 로 부연, 표와 코드펜스 적극 활용. 고아 정리 대상은 끊긴 상호참조 · 사라진 스킬을 가리키는 포인터 · README 구조도의 유령 항목이다.

---

## 검증

이 레포엔 `biome` 도 `check:type` 도 없다. 대신 자산을 만지면 아래를 검증한다.

| 바꾼 것 | 검증 |
|---|---|
| `skills/*/SKILL.md` | frontmatter `name` 이 디렉터리명과 같은가 · `description` 이 "무엇인지" · `when_to_use` 가 "언제 읽는지"를 말하는가 · 둘 합쳐 1,536자 이내인가 · 본문 500줄 이내인가 |
| 사용자 호출 전용 스킬 (`spec` · `step`) | `disable-model-invocation: true` 가 있는가 · `$ARGUMENTS` 가 비어 있을 때의 동작이 정의됐는가 (`when_to_use` 는 불필요 — 리스팅에 안 들어간다) |
| `agents/*.md` | frontmatter `name` 이 파일명과 같은가 · `tools` 가 그 역할에 필요한 최소인가 |
| 자산 추가 · 삭제 · 이름 변경 | README 구조도와 실제 트리가 일치하는가 |
| `.claude-plugin/*.json` | JSON 이 파싱되는가 · `plugin.json` 의 `name` 과 `marketplace.json` 의 `plugins[].name` 이 같은가 |
| 자산을 고쳐 PR 을 낼 때 | `plugin.json` 의 `version` 을 올렸는가 — **main 머지 시 그 버전으로 릴리스가 나가고, 안 올리면 릴리스는 no-op 이다** |
| `NORMS.md` · `hooks/*` | 훅이 단독 실행되는가 · 레포 전용 내용이 `NORMS.md` 에 새지 않았는가 |

기계적으로 볼 수 있는 것은 스크립트가 본다 — 위 표에서 판단이 필요한 항목(축이 겹치는가 · 트리거가 실제 발화인가 · `tools` 가 최소인가)만 사람이 본다.

```bash
pip install pyyaml                    # 최초 1회
python3 scripts/validate-assets.py    # frontmatter · 매니페스트 · README 정합
node hooks/inject-norms.js | python3 -m json.tool > /dev/null   # 훅 단독 실행
```

같은 검사가 `.github/workflows/validate.yml` 로 PR 마다 돈다 — `claude plugin validate` 와 version bump 확인까지 함께.

**frontmatter 값이 `"` 로 시작하면 반드시 작은따옴표로 감싼다.** YAML 이 그걸 닫힌 스칼라로 읽고 뒤를 잉여 토큰으로 보기 때문에 파싱이 깨진다. 깨져도 `claude plugin validate` 는 통과하고, 스킬만 조용히 목록에서 빠져 자동 발동이 죽는다.

```yaml
❌ when_to_use: "이거 만들어줘" · "리팩토링해줘" 요청.
✅ when_to_use: '"이거 만들어줘" · "리팩토링해줘" 요청.'
```

### 고친 자산을 세션에 반영하기

**이 레포를 고쳐도 세션은 안 바뀐다.** 플러그인 설치본은 `~/.claude/plugins/cache/paul/paul/<version>/` 로 복사되는 스냅샷이고, 세션은 그 복사본만 읽는다. 마켓플레이스를 로컬 경로로 걸어도 라이브가 아니다.

```bash
claude plugin marketplace update paul
claude plugin update paul@paul
```

**`version` 을 올렸으면 이게 정상 경로다** — `plugin.json` 의 `version` 을 올려 main 에 머지하면 릴리스가 나가고, `update` 가 버전 차이를 보고 새 스냅샷을 받는다.

`version` 을 그대로 둔 채 내용만 고쳐 돌려볼 때만 재설치한다 — `update` 는 버전 비교라 그 경우 no-op 이다.

```bash
claude plugin uninstall paul@paul && claude plugin install paul@paul
```

편집마다 돌릴 필요는 없다 — 여러 개 고친 뒤 마지막에 한 번. 다만 **하네스가 이상하면 문구를 다시 고치기 전에 캐시부터 의심한다.** 고쳤다고 믿는데 안 고쳐진 상태가 이 방식의 유일한 함정이다.

---

## 어디에 쓸 것인가

새 내용이 생겼을 때 **어느 자산에 넣을지 먼저 정한다.** 잘못 넣으면 로딩되지 않거나 매번 로딩된다.

| 성격 | 위치 |
|---|---|
| 어디서든 무조건 지켜야 하는 규범 | `NORMS.md` (매 세션 주입) |
| 누구로서 판단하는가 (페르소나 · 권한 · 위임) | `agents/` |
| 특정 상황에서만 필요한 지식 | `skills/` — 모델 자동 발동 |
| 사용자가 명시적으로 호출하는 절차 | `skills/` + `disable-model-invocation: true` |
| 이 레포를 편집하는 규약 | 이 문서 |

`NORMS.md` 는 매 세션 값을 치르므로 **비싸다.** 상황을 가리는 지식은 스킬로 내린다.

자산은 `skills/` 하나로 통일돼 있고, **갈리는 축은 호출 주체다.** 자동 발동 스킬은 `description` + `when_to_use` 로 리스팅에 상주하고, 사용자 호출 전용은 `disable-model-invocation: true` 로 리스팅에서 **아예 빠진다**(비용 0, `/paul:이름` 으로만 열림).

부수효과가 있거나(파일을 쓴다) 정해진 지점에서 멈추는 게 요점인 절차는 사용자 호출 전용으로 둔다 — 발동 시점을 사람이 쥐어야 브레이크 구실을 한다.

**자동 발동 스킬은 축 하나에 하나다.** 현재 축 — `paul-rockstar`(어떻게 생각하는가) · `code-to-product`(어떻게 모델링하는가) · `paul-layout`(어디에 두는가) · `paul-react`(컴포넌트 안에 무엇을) · `paul-review`(어떻게 검토하는가) · `agentic-workflow`(어떤 순서로) · `paul-stack`(무엇으로) · `paul-taste`(어떤 결로). 새 스킬을 만들기 전에 **기존 축에 안 들어가는지 먼저 따진다.** 축이 겹치는 자동 발동 스킬이 둘이면 라우팅이 갈린다.

## 단일 정본

**같은 내용을 두 곳에 쓰지 않는다.** 커밋 형식은 `paul-taste` 에만, Spec 구조는 `agentic-workflow` 에만 있다. 다른 문서에선 포인터만 남긴다 — `상세: agentic-workflow 스킬`.

중복은 반드시 갈라진다. 갈라진 두 정본은 없는 것보다 나쁘다.

## 스킬 frontmatter

스킬은 **자동 발동이 목적**이다. 리스팅에 상주하는 건 `description` + `when_to_use` 둘뿐이고, 그게 라우팅의 전부다. **역할을 나눈다.**

| 필드 | 쓰는 것 |
|---|---|
| `description` | **무엇인가** — 스킬이 담은 축을 한 문장으로 |
| `when_to_use` | **언제 읽는가** — 사용자가 실제로 칠 법한 발화 · 파일/레포 조건 · 하면 안 되는 것을 하려는 순간 |

```
❌ description: 스택 규약 모음
✅ description: pnpm · Biome · TS strict · 서버별 규칙.
   when_to_use: 패키지 설치 · 라우트 추가 · DTO 추가 · 타입 체크.
   "설치해줘" · "타입 에러 나" 요청. npm/yarn · ESLint/Prettier 를 제안하기 전에 반드시.
```

`when_to_use` 는 `description` 뒤에 이어붙어 리스팅에 들어간다 — 즉 **공짜가 아니다.** 둘 합쳐 항목당 1,536자에서 잘리고, 전체 리스팅은 컨텍스트의 1% 예산을 나눠 쓴다. 트리거 문구는 넉넉히, 설명은 짧게.

본문 500줄 이내. 넘치면 `references/` 로 내리고 본문엔 포인터만 남긴다.

## 에이전트 frontmatter

`tools` 는 그 역할이 실제로 필요한 것만. 읽기 전용 에이전트(`paul-planner`)에 `Edit`/`Write` 를 주지 않는다 — 역할 경계를 지시문이 아니라 **권한으로** 강제한다.

**그래서 경계가 권한이어야 하는 역할만 에이전트로 남긴다.** 스킬은 `tools` 를 못 좁히므로 경계가 지시문으로 내려간다 — 대신 리스팅에 상주해 사용자가 부르지 않아도 발동한다. 그 교환이 남는 장사인지가 판단 기준이다.

## 커밋

형식은 `paul-taste` 스킬에 있다. 이 레포의 scope 는 `paul` 또는 자산 이름.

```
docs(paul): AGENTS.md 하네스 작업 규약 추가
feat(paul): paul-planner 에이전트 추가
```
