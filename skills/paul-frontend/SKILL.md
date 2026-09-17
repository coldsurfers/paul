---
name: paul-frontend
description: Paul 의 프론트엔드 작성 규약 — 바깥에서 안으로 세우는 순서, 코드를 어디에 두는가(유닛 · 배럴 · 도메인 슬라이스 · 타입 정본), 컴포넌트 안에 무엇을 쓰는가(메모이제이션 판정 · 슬롯 레이아웃 · 좁은 프리미티브 · 껍데기/알맹이 · 스타일 도구 · 토큰).
when_to_use: 컴포넌트 · 화면 · 훅 · 스토어를 쓰거나 고칠 때. 프로젝트나 화면을 새로 세울 때. props 를 설계할 때. 파일을 어디에 둘지 · 어떻게 쪼갤지 정할 때. import 경로를 뚫을 때. 로딩 · 에러 경계를 붙일 때. 스타일이나 색을 지정할 때. 리스트를 렌더할 때. "컴포넌트 만들어줘" · "이 화면 짜줘" · "어디에 두지" · "폴더 구조" · "이거 쪼개줘" · "props 어떻게 넘기지" · "리렌더가 많은데" · "memo 걸어야 하나" · "로딩 처리" · "스타일 어떻게 줘" 요청. 여백을 `margin` 으로 주려는 순간. `useReducer` · `css` prop · 하드코딩 색상 · index key 를 쓰려는 순간. 습관적으로 `useCallback` · `useMemo` 로 감싸려는 순간. wrapper `div` 에 클래스 조합식을 늘어놓으려는 순간.
---

# Frontend 작성 규약

**프론트엔드 코드를 어떻게 세우고 · 어디에 두고 · 안에 무엇을 쓰는가.** 셋은 같은 결정의 세 면이라 한 문서에 있다.

무엇을 만드는지는 `code-to-product`, 무엇으로 만드는지는 `paul-stack`, 이름 규칙은 `paul-taste`.
**네이티브라서 다른 것**(리스트 선택 · NativeWind 함정 · safe-area · 픽셀 검증)은 [`references/react-native.md`](references/react-native.md) — RN · Expo 레포에서만 연다.

---

# Ⅰ. 세우는 순서

## 1. 바깥에서 안으로 세운다

각 층은 **아래층만 알고 위층을 모른다.**

```
1  토큰        색 · 간격의 유일한 출처
2  프리미티브   여백 · 구분선 · 텍스트 — 일부러 좁게 (8절)
3  레이아웃     화면 껍데기 한 겹 — 배경 · 폭을 여기서 한 번만 정한다
4  라우팅       경로를 타입으로 고정
5  데이터       얇은 클라이언트 래퍼 → 엔드포인트 1:1 함수
6  화면        위 다섯을 조립만 한다
```

**화면이 마지막인 게 핵심이다. 화면 파일에서 새 개념이 태어나면 순서를 어긴 것이다.**
화면에 `css` 가 늘기 시작하면 화면이 특별한 게 아니라 **프리미티브가 모자란 것**이다.

### 경로는 타입으로 고정한다

라우터 라이브러리를 화면이 직접 부르지 않는다. **얇은 훅 하나로 감싸고 경로를 유니온으로 잠근다.**

```ts
export type AppRoute =
  | { name: 'event-list' }
  | { name: 'event-detail'; params: { eventId: string } }
  | { name: 'venue-detail'; params: { venueId: string } }

export function useAppNavigation() {
  const navigate = useNavigate()
  return useMemo(() => ({ go: (route: AppRoute) => navigate(toPath(route)) }), [navigate])
}
```

경로 문자열을 화면이 조립하지 않는다. **어디로 가는지를 값으로 넘기고**, 문자열 조립은 `toPath` 한 곳에 가둔다.
오타가 런타임 404 가 아니라 **컴파일 에러**가 되고, 경로 모양이 바뀌어도 고칠 곳이 한 군데다.

### 데이터는 2계층

```ts
// http — 얇은 래퍼. 응답 타입만 제네릭으로 받고 그 외엔 아무것도 안 한다
export const http = {
  async get<T>(path: string): Promise<T> {
    const res = await client(path)
    return res.json()
  },
}

// endpoints — 엔드포인트 하나 = 함수 하나, 응답 타입은 바로 아래에 붙인다
export function fetchUpcomingEvents(venueId: string) {
  return http.get<UpcomingEvents>(`/v1/venues/${venueId}/events`)
}
export interface UpcomingEvents {
  events: EventSummary[]
  nextCursor?: string
}
```

**타입이 API 문서다** — 요청·응답 형태를 주석이 아니라 시그니처로 말한다. `types/` 폴더를 따로 파지 않는다.
쪼개는 이유는 **대체 단위** 때문이다. 테스트가 엔드포인트 모듈 하나를 통째로 갈아끼운다.

---

# Ⅱ. 어디에 두는가

프레임워크가 바뀌어도 이 넷은 바뀌지 않는다.

## 2. 유닛 하나 = 디렉터리 하나

```
artist-subscribe-button/
  artist-subscribe-button.tsx        # 본체 — 이 유닛이 하는 일
  artist-subscribe-button.types.ts   # 타입
  artist-subscribe-button.styled.ts  # 스타일 전부
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

## 3. index.ts 는 `export *` 만

```ts
export * from './button'
export * from './button.types'
```

로직 · 조건부 export · 재가공을 넣지 않는다. 배럴은 **다단으로 쌓아** 소비 측이 최상위 하나만 알게 한다.

```ts
import { ArtistSubscribeButton } from '@/features'                                    // ✅
import { ArtistSubscribeButton } from '@/features/subscribe/ui/artist-subscribe-button/artist-subscribe-button'  // ❌
```

상대경로(`../utils`)는 **슬라이스 안에서만.** 슬라이스 경계를 상대경로로 넘지 않는다 — 넘고 있다면 경계를 잘못 그은 것이다.

**`export default` 는 쓰지 않는다.** 배럴이 `export *` 라 default 는 그 문을 지나지 못한다. 프레임워크가 요구하는 자리(라우트 파일)만 예외다.

## 4. 도메인으로 자른다, 타입으로 자르지 않는다

```
❌ components/  hooks/  stores/  utils/     ← 앱 최상위에 타입별로
✅ features/<도메인>/{ui,hooks,stores,utils}/
```

`components/` 를 열면 무슨 앱인지 알 수 없다. `features/` 를 열면 앱이 무엇을 하는지 목록으로 보인다.

**기준: 이 디렉터리를 통째로 지웠을 때 정확히 하나의 기능이 사라지는가.** 여기저기서 구멍이 나면 슬라이스가 아니다.

여러 도메인이 함께 쓰는 것만 공용으로 올린다 — **두 번째 사용처가 생겼을 때** 올리지, 미리 올리지 않는다.

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

---

# Ⅲ. 안에 무엇을 쓰는가

## 6. 메모이제이션은 기본값이 아니라 판정이다

**기본값은 감싸지 않는 것이다.** `useCallback` · `useMemo` · `memo` · `forwardRef` 는 **붙일 이유를 댈 수 있을 때만** 붙인다.

「매 렌더 새로 만들어지니까」는 이유가 아니다 — 거의 모든 값이 그렇고 대부분은 그래도 싸다. 습관으로 감싸면 판단이 사라지고, **감싸지 않은 것이 예외**가 되어 진짜 무거운 자리를 아무도 못 찾는다.

### 붙일 자리는 셋으로 가린다

- **항상 마운트돼 있는가** — 부모가 다시 그릴 때마다 딸려 그려지는 자리인가
- **prop 이 원시값 몇 개인가** — 참조가 매 렌더 바뀌면 `memo` 는 장식이다
- **트리가 무거운가** — SVG 아이콘 여럿 · 이미지 · 긴 목록

셋이 맞으면 붙인다. 탭바가 그 자리다. 리스트는 이미 셋을 통과한 자리라 따로 다룬다(RN 참고문서 2절).

### 붙일 거면 연쇄를 끝까지 확인한다

훅이 돌려주는 함수를 감싸지 않으면, 그걸 deps 에 넣은 바깥 `useCallback` 이 통째로 장식이 된다. **effect deps 에 들어가면 무한 루프다.**

```ts
// ❌ 훅은 안 감싸고 소비부만 감쌌다
export function useFilterPanel() {
  const reset = () => setSelected([])   // 매 렌더 새 함수
  return { reset }
}
useEffect(() => { reset() }, [reset])   // → setState → 리렌더 → 새 reset → 무한

// ✅ 돌려주는 쪽에서 고정한다
const reset = useCallback(() => setSelected([]), [])
```

`Maximum update depth exceeded` 가 뜨면 여기부터 본다.

### 나머지 훅

- **`useReducer` 는 쓰지 않는다.** 상태가 reducer 를 부를 만큼 복잡해졌다면 컴포넌트 밖으로 — store 로 뺀다
- **`useRef` 는 아껴 쓴다.** DOM 을 직접 만지는 대신 상태와 선언적 props 로 푼다

의존성 배열은 빠짐없이 채운다. 배열을 줄이려고 로직을 밖으로 빼지 않는다 — 반대로, 다 넣었더니 매 렌더 바뀌면 그 값이 잘못 만들어진 것이다.

## 7. 레이아웃은 데이터를 모른다 — `ReactNode` 슬롯만 받는다

```tsx
export function PageLayout({ poster, topInfo, ticketCTA, lineup, venue }: {
  poster: ReactNode
  topInfo: ReactNode
  ticketCTA: ReactNode
  lineup: ReactNode | null
  venue: ReactNode
}) {
  return (
    <StyledPageLayout>
      <StyledPosterContainer>{poster}</StyledPosterContainer>
      {lineup && (
        <StyledSectionContainer>
          <StyledSectionHeaderText as="h3">Lineup</StyledSectionHeaderText>
          {lineup}
        </StyledSectionContainer>
      )}
    </StyledPageLayout>
  )
}
```

- 레이아웃에 **페칭도 도메인 타입도 없다.** 구멍을 뚫고 배치만 한다
- **도메인을 아는 레이아웃은 역할로, 모르는 프리미티브는 위치로 이름 짓는다** — `poster` · `lineup` vs `contents` · `leftAddon` · `rightAddon`. `ListItem` 은 자기 왼쪽에 아이콘이 올지 아바타가 올지 모른다. **축이 갈리는 지점은 도메인을 아는가다**. `slot1` 처럼 번호를 붙이지 않는다
- **조건부는 부모가 판단해서 넘긴다** — `lineup={artists.length > 0 && <Lineup artists={artists} />}`. 레이아웃은 `{lineup && ...}` 로 받아 **섹션 헤더 껍데기까지 함께 지운다**

도메인 타입을 받기 시작하면 그건 레이아웃이 아니라 화면이다. 나눈다.

## 8. 프리미티브는 일부러 좁게

**여백을 CSS 로 내지 않는다.** `margin: 20px` 대신 컴포넌트로 낸다.

```tsx
export function Gap({ height }: { height: number }) {
  return <div aria-hidden style={{ blockSize: height, flexShrink: 0 }} />
}
```

화면은 `<Gap height={24} />` 를 줄 사이에 끼워 넣는다. 이 한 수로 화면 파일에서 **여백 계산이 통째로 사라지고**,
순서를 바꾸려면 줄을 옮기면 끝이 된다 — 위아래 마진이 겹쳐 무너지는 일도 없다.

props 개수를 보면 설계 의도가 보인다. **표현력을 줄여 일관성을 산다.**

| 성격 | props |
|---|---|
| 레이아웃 원자 — 여백 · 구분선 | **1개** |
| 세로 컨테이너 | 2개 |
| 행 조립 | 슬롯 둘 + 플래그 하나 |
| 텍스트 | 넓어도 되는 **유일한 탈출구** |

여백 원자에 `gap` 이나 `direction` 을 붙이고 싶으면 **그게 진짜 필요한지 먼저 묻는다.**
텍스트 말고 다른 프리미티브가 넓어지기 시작하면, 그건 프리미티브가 아니라 컴포넌트가 된 것이다.

### 변형은 플래그가 아니라 정적 프로퍼티로

```tsx
Row.TitleOnly    = ({ title }: TitleOnlyProps) => ( /* … */ )
Row.TitleAndMeta = ({ title, meta }: TitleAndMetaProps) => ( /* … */ )
```

새 변형이 생겨도 **컴포넌트 안에 `if` 가 안 늘어난다.** `variant="..."` 유니온을 넓히는 대신 프로퍼티를 하나 더 단다.

### rest props 는 DOM 으로 통과시킨다

```tsx
export function ListItem({ leftAddon, rightAddon, children, ...props }: ListItemProps) {
  return <li {...props}>{/* … */}</li>
}
```

빠뜨리면 `onClick` 이 **조용히 죽는다.** 타입도 통과하고 경고도 없다.

## 9. 껍데기와 알맹이를 나눈다

바깥 컴포넌트는 **에러 경계 + 로딩 fallback** 만, 안쪽이 데이터를 읽는다.

```tsx
export function EventDetailPage(props) {
  return (
    <ApiErrorBoundaryRegistry>
      <Suspense fallback={<PageLayoutSkeleton />}>
        <PageInner {...props} />
      </Suspense>
    </ApiErrorBoundaryRegistry>
  )
}
```

- fallback 은 **실제 레이아웃을 재사용**한다. 화면 한가운데 스피너 하나로 때우지 않는다
- 안쪽은 데이터가 있다고 가정하고 쓴다 — `isLoading` 분기를 컴포넌트마다 반복하지 않는다
- 안쪽 이름은 `*Inner` 로 통일한다

**실패 경로가 사용자에게 보여야 한다.** 로딩 · 에러 · 빈 상태를 `return null` 과 `console.error` 로 때우지 않는다.
막았으면 **왜 막혔는지 말한다** — 버튼을 숨기지 말고 이유를 띄운다. 폴링 · 재시도에는 **상한을 둔다.**

같은 타입 인자를 여러 곳에서 반복하게 되면 **한 번만 쓰고 훅으로 감싼다.**

```ts
export const useHomeScreenNavigation = () => useNavigation<HomeScreenProps['navigation']>()
```

## 10. 스타일 도구는 표면당 하나, 색은 토큰으로만

| | 쓰는 것 | 쓰지 않는 것 |
|---|---|---|
| React Native | `StyleSheet.create` — 파일 하단에 `styles` | `.styled` 파일 |
| Web | **그 앱이 고른 도구 하나** — emotion `styled`(`.styled.ts` · `Styled*` prefix) 또는 vanilla-extract(`.css.ts`) | **`css` prop** · 한 표면에 두 도구 혼용 |

무엇을 골랐는지는 레포가 정한다. 이 절은 **고른 하나로만 간다**는 것만 정한다.

- 인라인 `style={{}}` 은 **동적 값만** — 테마 색, 계산된 크기. 정적 스타일을 인라인에 두지 않는다
- 반응형은 브레이크포인트 헬퍼로 묶는다
- 컴포넌트 파일에 스타일 정의가 쌓이면 스타일 파일로 내린다 (2절)

```tsx
color: ${semantics.color.foreground[1]};        // ✅ 1순위 — 의미
backgroundColor: colors.oc.gray[1].value        // ✅ 2순위 — 팔레트
color: '#1a1a1a'                                // ❌
```

**semantic 이 먼저다.** 팔레트 직접 접근은 semantic 에 해당 역할이 없을 때만. 하드코딩 hex 는 쓰지 않는다 — 다크 모드에서 조용히 깨진다.

### 구조를 가진 wrapper 는 이름을 가진 컴포넌트다

```tsx
<WarmPaperSurface>                                               // ✅ 이름이 의미다
<div className={cx(sprinkles({ ... }), page)} style={SURFACE}>   // ❌
```

- **JSX 본문에 스타일 조합식을 노출하지 않는다.** `cx(...)` · `styled` 선언은 컴포넌트 안으로 들어가고, 화면은 이름만 읽는다
- 이름은 **역할**이다 — `WarmPaperSurface` · `PageShell`. `Wrapper` · `Container1` 은 이름이 아니다
- 같은 조합이 **두 번째 표면에 나타나면** 그때 뽑는다

**판정: 이 div 에 이름을 붙일 수 있는가.** 붙일 수 있으면 컴포넌트다.

## 11. 본문 관용구

- **가드를 먼저 턴다.** `if (!data) return null` — JSX 안에서 중첩 삼항으로 갈래를 만들지 않는다. 정상 경로는 아래에 평평하게 둔다
- **key 는 도메인 id.** `key={event.id}`. 배열 index 는 id 가 없을 때만이고, 그건 대개 데이터가 잘못 온 것이다
- 두 갈래는 `&&`, 값이 갈리면 삼항. 세 갈래부터는 변수로 빼거나 컴포넌트를 나눈다
- 기본값은 구조분해에 인라인 — `({ size = 'md', theme = 'indigo' })`
- **없음은 `undefined` 로 표현한다.** 체크는 `== null` / `!= null`
- 디자인 시스템 컴포넌트는 `forwardRef` 로 ref 를 통과시킨다 — 소비처가 누구일지 모르는 자리라 이유가 이미 서 있다(6절의 예외)
- 타입 선언이 본체 파일에 보이면 `.types.ts` 로 내린다. 파일 하나가 **200줄을 넘으면 유닛이 둘 이상**이라는 신호다

**선언 형태(`const` 화살표 / `function`)는 정해진 규칙이 없다.** 이건 export 형태와 다른 축이다 — 새로 정하지 말고 **그 파일과 그 앱의 기존 형태를 따른다.**

---

## 판정

1. 이 개념이 **화면 파일에서 태어나고 있지 않은가** (1절)
2. 이 디렉터리를 통째로 지우면 **정확히 하나의 기능이 사라지는가** (4절)
3. import 가 **슬라이스 경계를 뚫고 있지 않은가** (3절)
4. 이 컴포넌트가 **데이터를 알아야 하는가** — 아니면 슬롯으로 받는다 (7절)
5. 이 여백을 **컴포넌트로 낼 수 있는가** (8절)
6. 이 핸들러·파생값을 감쌀 **이유를 댈 수 있는가** (6절의 셋)
7. 로딩·에러·빈 상태가 **사용자에게 보이는가** (9절)
8. 이 색이 **토큰인가** (10절)

## 안 하는 것

| 하지 않는 것 | 이유 |
|---|---|
| 화면 파일에서 새 개념 만들기 | 세우는 순서를 어긴 것이다 |
| `margin` 으로 화면 여백 주기 | 여백은 프리미티브다 |
| 프리미티브에 props 늘리기 | 표현력을 줄여 일관성을 산다 |
| `{...props}` 빠뜨리기 | `onClick` 이 조용히 죽는다 |
| 이유 없는 `useCallback` · `useMemo` · `memo` | 기본값은 감싸지 않는 것이다 |
| `useReducer` | 그만큼 복잡하면 store 로 나갈 때다 |
| `css` prop · 한 표면에 두 도구 | 고른 하나로만 간다 |
| JSX 에 노출된 스타일 조합식 | 이름을 붙일 수 있으면 컴포넌트다 |
| 하드코딩 hex | 다크 모드에서 조용히 깨진다 |
| index key | 리스트가 재정렬되면 상태가 엉킨다 |
| 컴포넌트마다 `isLoading` 분기 | 껍데기가 한 번에 처리한다 |
| 레이아웃이 도메인 타입 받기 | 레이아웃이 아니라 화면이다 |
| `index.ts` 에 로직 | 배럴은 주소록이지 구현이 아니다 |
| 앱 최상위 `components/` · `utils/` | 무슨 앱인지 안 보인다 |
| 슬라이스 경계를 넘는 상대경로 | 경계가 없다는 뜻 |
| 스키마와 손으로 쓴 타입 병존 | 반드시 갈라진다 |
| 사용처 하나짜리 공용 디렉터리 | 두 번째가 생기면 그때 올린다 |
