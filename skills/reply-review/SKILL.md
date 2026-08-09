---
name: reply-review
description: GitHub PR 리뷰 코멘트 하나에 답글을 단다 — 코멘트를 읽고, 무엇을 고쳤는지 한국어로 쓰고, 푸시된 커밋 링크로 닫는다. 초안을 보이고 승인받은 뒤에만 게시한다.
disable-model-invocation: true
---

`$ARGUMENTS` = `<코멘트 URL> [커밋 해시]`

| 인자 | 값 |
|---|---|
| 코멘트 URL | `https://github.com/<owner>/<repo>/pull/<n>#discussion_r<id>` |
| 커밋 해시 | 생략하면 `HEAD` — 3단계를 거친다 |

`$ARGUMENTS` 가 비어 있으면 **어느 코멘트에 답글을 달지 먼저 묻는다.** URL 없이 코멘트를 골라 잡지 않는다.

무엇을 반영하고 무엇을 되묻는지, 어디까지 되짚는지는 `paul-review-fix` 의 몫이다. 여기는 **코멘트 하나에 답글을 다는 절차**만 담는다.

## 절차

`Bash` 가 deferred 면 먼저 연다 — `ToolSearch: select:Bash`.

**1. URL 을 쪼갠다** — `owner` · `repo` · PR 번호 · `#discussion_r` 뒤의 코멘트 id.

**2. 코멘트를 읽는다.**

```bash
gh api repos/<owner>/<repo>/pulls/<n>/comments \
  --jq '.[] | select(.id == <id>) | {body, path, diff_hunk}'
```

**3. 해시를 정한다.** 인자로 받았으면 그걸 쓴다. 없으면:

```bash
git status --short          # 남은 변경이 있는가
git rev-parse HEAD          # 깨끗하면 여기서 해시를 얻는다
git branch -r --contains <hash>   # 푸시됐는가
```

- 스테이지되거나 커밋 안 된 변경이 있으면 **먼저 커밋할지 묻고 멈춘다.** 답을 받기 전에 `HEAD` 를 쓰지 않는다
- 링크는 **푸시된 커밋에만.** 로컬 해시는 남의 화면에서 404 다
- 표시는 앞 8자, 링크는 전체 해시

**4. 코멘트와 커밋 diff 를 맞춰본다** — 리뷰어가 무엇을 짚었고 그 커밋이 무엇을 바꿨는지.

**5. 답글 초안을 쓴다.** 한국어, 세 줄 이내.

1. 지적을 한 줄로 받는다
2. 어디를 어떻게 고쳤는지 한 줄 — 파일·심볼 이름을 적는다
3. 커밋 링크로 닫는다 — `([<short>](https://github.com/<owner>/<repo>/commit/<full>))`

**고치지 않았으면 고치지 않았다고 쓰고 근거를 남긴다.** 링크는 붙이지 않는다 — 반박도 답글이다.

**6. 초안을 보이고 승인을 받는다.** 승인 전에 게시하지 않는다.

**7. 게시한다.**

```bash
gh api repos/<owner>/<repo>/pulls/<n>/comments/<id>/replies -f body="<본문>"
```

`replies` 엔드포인트여야 그 스레드에 붙는다. PR 본문이나 새 코멘트로 몰아 쓰지 않는다 — 리뷰어가 자기 지적 옆에서 봐야 한다.

**8. 스레드는 닫지 않는다.** resolve 도 머지도 리뷰어의 몫이다.

## 예시

반영한 경우:

```
말씀대로 `any` 단언이 경계를 지우고 있었습니다.
`ConcertDTO` 로 좁히고 변환은 `to-concert.ts` 한 곳으로 모았습니다.
([a1b2c3d4](https://github.com/coldsurfers/billets/commit/a1b2c3d4...))
```

반영하지 않은 경우:

```
`venue` 로 바꾸자는 제안은 따르지 않았습니다.
실물 용어가 "공연장"이 아니라 "장소"라 DTO 이름이 도메인과 어긋나게 됩니다.
```

## 안 하는 것

| 하지 않는 것 | 이유 |
|---|---|
| 승인 없이 게시 | 남의 PR 에 남는 글이다 |
| 안 푸시한 해시로 링크 | 링크가 죽는다 |
| 새 코멘트로 몰아 쓰기 | 지적과 답이 떨어진다 |
| 답글 쓰면서 코드까지 고치기 | 이 스킬은 답글만 단다 |
| 대신 resolve · 대신 머지 | 리뷰를 닫는 권한은 리뷰어에게 있다 |
