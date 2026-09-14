---
name: paul-react
description: Paul 의 React · React Native 컴포넌트 작성 규약 — 메모이제이션 판정, ReactNode 슬롯 레이아웃, 껍데기/알맹이 분리, 타입 바인딩 훅, 표면당 스타일 도구 하나, 이름을 가진 wrapper, 디자인 토큰.
when_to_use: 컴포넌트 · 화면 본문을 쓰거나 고칠 때. props 를 설계할 때. 상태 · 파생값 · 핸들러를 배치할 때. 로딩 · 에러 경계를 붙일 때. 스타일이나 색을 지정할 때. 리스트를 렌더할 때. "컴포넌트 만들어줘" · "이 화면 짜줘" · "props 어떻게 넘기지" · "리렌더가 많은데" · "memo 걸어야 하나" · "로딩 처리" · "스타일 어떻게 줘" 요청. `useReducer` · `css` prop · 하드코딩 색상 · index key 를 쓰려는 순간. 핸들러나 파생값을 습관적으로 `useCallback` · `useMemo` 로 감싸려는 순간. wrapper `div` 에 클래스 조합식(`cx(...)`)을 늘어놓으려는 순간. 파일을 어디에 둘지는 `paul-layout` 의 몫이다.
---

# React 작성 규약

`paul-layout` 이 **어디에 두는가**라면 이건 **안에 무엇을 쓰는가**다. 함께 읽는다.

여기 있는 건 두 플랫폼에 다 적용된다. **네이티브라서 다른 것**(리스트 선택 · NativeWind 함정 · safe-area · 픽셀 검증)은 `paul-react-native` 에 있다.

## 1. 메모이제이션은 기본값이 아니라 판정이다

**기본값은 감싸지 않는 것이다.** `useCallback` · `useMemo` · `memo` · `forwardRef` 는 **붙일 이유를 댈 수 있을 때만** 붙인다.

「매 렌더 새로 만들어지니까」는 이유가 아니다 — 거의 모든 값이 그렇고 대부분은 그래도 싸다. 습관으로 감싸면 판단이 사라지고, **감싸지 않은 것이 예외**가 되어 진짜 무거운 자리를 아무도 못 찾는다.

### 붙일 자리는 셋으로 가린다

- **항상 마운트돼 있는가** — 부모가 다시 그릴 때마다 딸려 그려지는 자리인가
- **prop 이 원시값 몇 개인가** — 참조가 매 렌더 바뀌면 `memo` 는 장식이다
- **트리가 무거운가** — SVG 아이콘 여럿 · 이미지 · 긴 목록

셋이 맞으면 붙인다. 탭바가 그 자리다. 리스트는 이미 셋을 통과한 자리라 따로 다룬다 (`paul-react-native` 2절).

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

- **`useReducer` 는 쓰지 않는다.** 상태가 reducer 를 부를 만큼 복잡해졌다면 컴포넌트 밖으로 — zustand store 로 뺀다
- **`useRef` 는 아껴 쓴다.** DOM 을 직접 만지는 대신 상태와 선언적 props 로 푼다

의존성 배열은 빠짐없이 채운다. 배열을 줄이려고 로직을 밖으로 빼지 않는다 — 반대로, 다 넣었더니 매 렌더 바뀌면 그 값이 잘못 만들어진 것이다.

## 2. 레이아웃은 데이터를 모른다 — `ReactNode` 슬롯만 받는다

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
- **슬롯 이름은 역할이다** — `poster` · `lineup` · `venue`. `slot1` 처럼 번호를 붙이지 않는다
- **역할을 모르는 컴포넌트만 위치로 짓는다** — 도메인을 아는 레이아웃은 역할(`poster`), 무엇이 들어올지 모르는 프리미티브는 위치(`leftAddon` · `rightAddon`). `ListItem` 은 자기 왼쪽에 아이콘이 올지 아바타가 올지 모른다. **축이 갈리는 지점은 도메인을 아는가다**
- **조건부는 부모가 판단해서 넘긴다** — `lineup={artists.length > 0 && <Lineup artists={artists} />}`. 레이아웃은 `{lineup && ...}` 로 받아 **섹션 헤더 껍데기까지 함께 지운다**

도메인 타입을 받기 시작하면 그건 레이아웃이 아니라 화면이다. 나눈다.

## 3. 껍데기와 알맹이를 나눈다

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

## 4. 제네릭 타입 바인딩은 훅으로 고정한다

같은 타입 인자를 여러 곳에서 반복해 쓰게 되면, **한 번만 쓰고 훅으로 감싼다.**

```ts
// home-screen.hooks.ts
export const useHomeScreenNavigation = () => useNavigation<HomeScreenProps['navigation']>()
export const useHomeScreenRoute = () => useRoute<HomeScreenProps['route']>()
```

소비처는 인자 없이 부른다. 타입이 바뀌면 고칠 곳이 한 군데다.

## 5. 스타일 도구는 표면당 하나

| | 쓰는 것 | 쓰지 않는 것 |
|---|---|---|
| React Native | `StyleSheet.create` — 파일 하단에 `styles` | `.styled` 파일 |
| Web | **그 앱이 고른 도구 하나** — emotion `styled`(`.styled.ts` · `Styled*` prefix) 또는 vanilla-extract(`.css.ts`) | **`css` prop** · 한 표면에 두 도구 혼용 |

무엇을 골랐는지는 레포가 정한다. 이 절은 **고른 하나로만 간다**는 것만 정한다.

- 인라인 `style={{}}` 은 **동적 값만** — 테마 색, 계산된 크기. 정적 스타일을 인라인에 두지 않는다
- 반응형은 브레이크포인트 헬퍼로 묶는다 — `${media.medium(css\`...\`)}`
- 컴포넌트 파일에 스타일 정의가 쌓이면 스타일 파일로 내린다 (`paul-layout` 1절)

### 구조를 가진 wrapper 는 이름을 가진 컴포넌트다

```tsx
<WarmPaperSurface>                                    // ✅ 이름이 의미다
<div className={cx(sprinkles({ ... }), page)} style={SURFACE}>   // ❌
```

- **JSX 본문에 스타일 조합식을 노출하지 않는다.** `cx(...)` · `styled` 선언은 컴포넌트 안으로 들어가고, 화면은 이름만 읽는다
- 이름은 **역할**이다 — `WarmPaperSurface` · `PageShell`. `Wrapper` · `Container1` 은 이름이 아니다
- 같은 조합이 **두 번째 표면에 나타나면** 그때 뽑는다. 한 번 쓰는 `<div className={styles.row}>` 까지 컴포넌트로 만들지 않는다

**판정: 이 div 에 이름을 붙일 수 있는가.** 붙일 수 있으면 컴포넌트다.

## 6. 색은 토큰으로만

```tsx
color: ${semantics.color.foreground[1]};        // ✅ 1순위 — 의미
backgroundColor: colors.oc.gray[1].value        // ✅ 2순위 — 팔레트
color: '#1a1a1a'                                // ❌
```

**semantic 이 먼저다.** 팔레트 직접 접근은 semantic 에 해당 역할이 없을 때만. 하드코딩 hex 는 쓰지 않는다 — 다크 모드에서 조용히 깨진다.

## 7. 렌더 관용구

- **가드를 먼저 턴다.** `if (!data) return null` — JSX 안에서 중첩 삼항으로 갈래를 만들지 않는다
- **key 는 도메인 id.** `key={event.id}`. 배열 index 는 id 가 없을 때만이고, 그건 대개 데이터가 잘못 온 것이다
- 두 갈래는 `&&`, 값이 갈리면 삼항. 세 갈래부터는 변수로 빼거나 컴포넌트를 나눈다
- 디자인 시스템 컴포넌트는 `forwardRef` 로 ref 를 통과시킨다 — 소비처가 누구일지 모르는 자리라 이유가 이미 서 있다(1절의 예외)

- **`export default` 는 쓰지 않는다.** 배럴이 `export *` 라 default 는 그 문을 지나지 못한다 (`paul-layout` 2절). 프레임워크가 default 를 요구하는 자리(라우트 파일)만 예외다

**선언 형태(`const` 화살표 / `function`)는 정해진 규칙이 없다.** 이건 export 형태와 다른 축이다 — 새로 정하지 말고 **그 파일과 그 앱의 기존 형태를 따른다.**

## 판정

1. 이 컴포넌트가 **데이터를 알아야 하는가** — 아니면 슬롯으로 받는다
2. 로딩·에러를 **여기서 처리하는가, 껍데기가 하는가**
3. 이 핸들러·파생값을 감쌀 **이유를 댈 수 있는가** (1절의 셋)
4. 이 색이 **토큰인가**
5. props 가 **한 화면에 들어오는가** (`code-to-product`)

## 안 하는 것

| 하지 않는 것 | 이유 |
|---|---|
| 이유 없는 `useCallback` · `useMemo` · `memo` | 기본값은 감싸지 않는 것이다 (1절) |
| `useReducer` | 그만큼 복잡하면 store 로 나갈 때다 |
| `css` prop | 한 표면은 고른 도구 하나로 간다 |
| JSX 에 노출된 스타일 조합식 | 이름을 붙일 수 있으면 컴포넌트다 |
| 하드코딩 hex | 다크 모드에서 조용히 깨진다 |
| index key | 리스트가 재정렬되면 상태가 엉킨다 |
| 컴포넌트마다 `isLoading` 분기 | 껍데기가 한 번에 처리한다 |
| 레이아웃이 도메인 타입 받기 | 레이아웃이 아니라 화면이다 |
| JSX 안 중첩 삼항 | 가드로 먼저 턴다 |
