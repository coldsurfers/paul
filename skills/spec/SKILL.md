---
name: spec
description: 기능 하나를 받아 Plan 을 세우고 specs/{앱또는패키지}/{기능}.md 스펙 파일 초안을 만든다. 코드는 쓰지 않는다.
disable-model-invocation: true
---

`agentic-workflow` 스킬의 1~3단계(이해 → Plan → Spec)를 `$ARGUMENTS` 에 적용한다.
**코드는 쓰지 않는다.**

`$ARGUMENTS` 가 비어 있으면 무엇에 대한 Spec 인지 먼저 묻는다.

- Spec 필요 판정 · 구조 · 범위 표기(✅ ⏸ ❌) 는 스킬을 따른다
- 현재 구조를 짚을 때 광범위한 탐색이 필요하면 서브 에이전트를 띄우기 전에 **먼저 허락을 구한다**
- `specs/{앱또는패키지}/{기능}.md` 경로를 제시하고 **승인 후** 쓴다
- 다 쓰면 첫 스텝만 제안하고 **멈춘다** — 구현으로 넘어가지 않는다
