---
name: paul-layout
description: Paul 의 코드 배치 규약 — 유닛 하나 = 디렉터리 하나, 접미사로 역할 분리, 배럴 index.ts, 도메인 슬라이스, 경계 변환을 한 곳에 가두기, 타입의 단일 정본.
when_to_use: 새 컴포넌트 · 훅 · 스토어 · 모듈 파일을 만들 때. 파일이 커져 쪼갤 때. import 경로를 새로 뚫을 때. 외부 데이터(DB row · API 응답)를 내부 타입으로 바꾸는 코드를 쓸 때. 인터페이스와 구현을 나눌지 정할 때. "어디에 두지" · "파일 어떻게 나눠" · "폴더 구조" · "이거 쪼개줘" · "import 가 지저분한데" · "계층 어떻게 가져가" 요청. 한 파일에 타입 · 스타일 · 상수 · 로직을 같이 쓰려는 순간.
---

# Code Layout

**어디에 두는가.** 무엇을 만드는지(`code-to-product`)와 무엇으로 만드는지(`paul-stack`)와는 별개 축이다. 프레임워크가 바뀌어도 이 규약은 바뀌지 않는다.

이름 규칙(kebab-case · PascalCase · `use*`)은 `paul-taste` 에 있다.

## 1. 유닛 하나 = 디렉터리 하나

```
artist-subscribe-button/
  artist-subscribe-button.tsx        # 본체 — 이 유닛이 하는 일
  artist-subscribe-button.types.ts   # 타입
  artist-subscribe-button.styled.ts  # 스타일 전부
  artist-subscribe-button.constants.ts
  index.ts                           # 배럴
```

**파일명은 디렉터리명을 반복한다.** 에디터 탭과 검색 결과가 `index.ts` 로 도배되지 않는 것이 반복의 값이다.

| 접미사 | 담는 것 |
|---|---|
| `.types.ts` | props · 도메인 타입 |
| `.styled.ts` | 스타일 정의 전부 |
| `.constants.ts` | 매직 넘버 · 리터럴 |
| `.utils.ts` | 이 유닛 전용 순수 함수 |
| `.hooks.ts` | 이 유닛 전용 훅 |

본체 파일에는 **하는 일만** 남는다. 열었을 때 타입 40줄 · 스타일 80줄을 지나야 로직이 나오면 이미 진 것이다.

**쪼개는 시점은 자랐을 때다.** 상수 하나 때문에 `.constants.ts` 를 만들지 않는다. 역할이 본체를 가릴 만큼 커지면 그때 내린다.

## 2. index.ts 는 `export *` 만

```ts
export * from './button'
export * from './button.types'
```

로직 · 조건부 export · 재가공을 넣지 않는다. 배럴은 **다단으로 쌓아** 소비 측이 최상위 하나만 알게 한다.

```
features/index.ts
 └ features/subscribe/index.ts
    └ features/subscribe/ui/index.ts
       └ features/subscribe/ui/artist-subscribe-button/index.ts
```

```ts
import { ArtistSubscribeButton } from '@/features'   // ✅
import { ArtistSubscribeButton } from '@/features/subscribe/ui/artist-subscribe-button/artist-subscribe-button'   // ❌
```

상대경로(`../utils`)는 **슬라이스 안에서만.** 슬라이스 경계를 상대경로로 넘지 않는다 — 넘고 있다면 경계를 잘못 그은 것이다.

## 3. 도메인으로 자른다, 타입으로 자르지 않는다

```
❌ components/  hooks/  stores/  utils/     ← 앱 최상위에 타입별로
✅ features/<도메인>/{ui,hooks,stores,utils}/
```

`components/` 를 열면 무슨 앱인지 알 수 없다. `features/` 를 열면 앱이 무엇을 하는지 목록으로 보인다.

**기준: 이 디렉터리를 통째로 지웠을 때 정확히 하나의 기능이 사라지는가.** 여기저기서 구멍이 나면 슬라이스가 아니다.

여러 도메인이 함께 쓰는 것만 공용으로 올린다 — 두 번째 사용처가 생겼을 때 올리지, 미리 올리지 않는다.

## 4. 경계 변환은 한 곳에 가둔다

외부 모델(DB row · 외부 API 응답)이 내부 타입으로 바뀌는 지점은 **파일 하나 안의 private 함수 하나**다.

```ts
// artist-detail.repository.ts — 무엇을 할 수 있는가
export interface ArtistDetailRepository {
  findArtistDetailById(id: string): Promise<ArtistDetailDTO | null>
}

// artist-detail.repository.impl.ts — 어떻게 하는가
export class ArtistDetailRepositoryImpl implements ArtistDetailRepository {
  async findArtistDetailById(id: string): Promise<ArtistDetailDTO | null> {
    const data = await /* 외부 조회 */
    if (!data) {
      return null
    }
    return this.toDTO(data)
  }

  private toDTO(model: ArtistDetailModel): ArtistDetailDTO { /* ... */ }
}
```

- **interface 와 impl 은 파일을 나눈다.** 바깥 층은 interface 만 알고, 구현은 생성자로 주입받는다
- **`toDTO` 는 `private`.** 변환이 이 클래스 밖에서 필요해졌다면 경계를 잘못 그은 것이다
- 외부 모델 타입(`ArtistDetailModel`)은 impl 파일 안에 둔다 — 밖으로 새면 경계가 아니다

**경계가 없으면 층을 만들지 않는다.** 외부 모델과 내부 타입이 같은 모양이면 통과만 하는 층은 노이즈다. 층의 개수를 맞추려고 만드는 파일은 만들지 않는다.

## 5. 타입의 정본은 하나

런타임 스키마가 있으면 **타입은 스키마에서 파생한다.** 손으로 쓴 타입과 스키마를 나란히 두지 않는다 — 반드시 갈라진다.

```ts
export const ArtistDetailDTOSchema = ArtistDTOSchema.extend({
  upcomingEvents: EventDTOSchema.array(),
})
export type ArtistDetailDTO = z.infer<typeof ArtistDetailDTOSchema>
```

타입 상속이 아니라 **스키마 조립**이다. 검증과 타입이 같이 따라온다.

생성된 타입(코드젠 산출물)도 같다 — 손으로 고치지 않고, 필요하면 파생시킨다.

## 6. 에러는 `code` + `message`

```ts
{ code: 'ARTIST_NOT_FOUND', message: 'artist not found' }
```

- **`code`** — SCREAMING_SNAKE. 분기의 대상이고 계약이다
- **`message`** — 사람이 읽는 것. 분기하지 않고, 바뀌어도 깨지지 않는다
- 미리 만들지 않는다. 실제로 발생하는 것만 정의한다
- 마지막 갈래는 `UNKNOWN` + 원본 로그

## 7. 본체 파일 안에서

- **guard 는 위로.** `if (!x) return null` 을 먼저 털고, 정상 경로는 아래에 평평하게 둔다. 중첩 if 로 감싸지 않는다
- 기본값은 구조분해에 인라인 — `({ size = 'md', theme = 'indigo' })`
- 타입 선언이 본체 파일에 보이면 `.types.ts` 로 내린다
- 파일 하나가 200줄을 넘으면 유닛이 둘 이상이라는 신호다

## 판정

1. 이 파일을 열었을 때 **하는 일이 첫 화면에 보이는가**
2. 이 디렉터리를 통째로 지우면 **정확히 하나의 기능이 사라지는가**
3. 새 접미사 파일을 만들 만큼 그 역할이 **자랐는가** — 아니면 아직 본체에 둔다
4. import 가 **슬라이스 경계를 뚫고 있지 않은가**
5. 이 층에 **경계가 실제로 있는가** — 없으면 층이 아니라 노이즈다

## 안 하는 것

| 하지 않는 것 | 이유 |
|---|---|
| `index.ts` 에 로직 | 배럴은 주소록이지 구현이 아니다 |
| 앱 최상위 `components/` · `utils/` | 무슨 앱인지 안 보인다 |
| 슬라이스 경계를 넘는 상대경로 | 경계가 없다는 뜻 |
| 통과만 하는 층 | 경계가 없는 층은 노이즈 |
| 스키마와 손으로 쓴 타입 병존 | 반드시 갈라진다 |
| 사용처 하나짜리 공용 디렉터리 | 두 번째가 생기면 그때 올린다 |
| 안 쓰는 에러 코드 미리 정의 | 계약만 늘고 분기는 안 생긴다 |
