# 네이티브라서 다른 것

`paul-frontend` 의 확장. **React Native · Expo 레포에서만 연다.**

메모이제이션 판정 · `ReactNode` 슬롯 · 프리미티브 폭 · 껍데기/알맹이 · 색 토큰은 본문에 있다. 여기는 **네이티브라서 달라지는 것**만 담는다.

## 1. 목록인가 화면인가

판정은 스크롤 방향이 아니라 **개수를 누가 정하는가**다.

| | 쓰는 것 |
|---|---|
| 개수가 고정된 이종 슬롯 — 화면 본문 | `ScrollView` |
| 서버가 개수를 정하는 동종 아이템 | `FlatList` |

- 화면 본문을 `FlatList` 로 바꾸려면 **슬롯 순서를 `data` 배열로** 만들어야 한다. 그 순간 레이아웃이 섹션을 알게 되고(본문 7절), 개수가 고정이라 가상화 이득도 없다
- 반대로 가로 셸프를 `ScrollView` 로 두면 **화면 밖 카드까지 전부 그린다.** 카드가 이미지를 물면 그만큼 디코딩한다
- 세로 `ScrollView` 안의 가로 `FlatList` 는 괜찮다 — 축이 달라 nested VirtualizedList 경고가 안 난다. 같은 축으로 겹치는 게 문제다

**판정: 이 배열의 길이를 내가 아는가.** 모르면 `FlatList` 다.

## 2. FlatList 로 옮기면 셋이 딸려온다

```tsx
const renderItem: ListRenderItem<GalleryItem> = useCallback(
  ({ item }) => <ShelfCard imagesUnavailable={imagesUnavailable} item={item} />,
  [imagesUnavailable],
)

<FlatList data={items} horizontal keyExtractor={(item) => item.id} renderItem={renderItem} />
```

- `renderItem` 은 `useCallback` — 매 렌더 새 함수면 셀이 통째로 다시 그려진다
- `keyExtractor` 는 **도메인 id.** index 는 재정렬에서 상태를 엉킨다
- 아이템 컴포넌트는 `memo` — 셀은 항상 마운트돼 있고 트리가 무겁다. 본문 6절의 판정을 이미 통과한 자리다

**로딩 자리표까지 태우지 않는다.** 스켈레톤은 개수가 고정이라 평범한 `flex-row` View 다 — 가상화할 게 없다.

**리스트 밖에서 `memo` 를 어디에 걸지는 본문 6절이 정본이다.** 이 절이 다루는 건 리스트가 이미 그 판정을 통과했다는 것뿐이다.

## 3. NativeWind 는 컴포넌트마다 다르게 붙는다

`className` 이 먹는다고 **같은 파일의 다른 prop 도 먹는 건 아니다.**

| 컴포넌트 | 거는 방식 |
|---|---|
| `View` · `Text` · `Image` · `Pressable` · `ScrollView` · `TextInput` … | `cssInterop` |
| `FlatList` · `VirtualizedList` · `ImageBackground` · `KeyboardAvoidingView` | `remapProps` |

`remapProps` 쪽은 버전 조합에 따라 **조용히 안 붙는다.** 타입도 통과하고 빌드도 되고 경고도 없다 — 간격과 padding 만 사라진다.

```tsx
<ScrollView contentContainerClassName="gap-[10px] px-4" horizontal>  // 먹는다
<FlatList   contentContainerClassName="gap-[10px] px-4" horizontal>  // 죽을 수 있다
<FlatList   contentContainerStyle={SHELF_CONTENT} horizontal>        // ✅ style 로
```

- `contentContainer*` 계열은 **style 객체로** 준다. 정적 값이니 상수 파일에 두고 왜 className 이 아닌지 주석으로 남긴다
- **`ScrollView` → `FlatList` 로 바꿀 때 className 을 그대로 옮기지 않는다.** 조용한 회귀의 단골 경로다

## 4. 회귀는 눈이 아니라 픽셀로 잡는다

RN 엔 DOM 스냅샷이 없어서 **"비슷해 보인다"에서 멈추기 쉽다.** 간격 · gutter 는 스크린샷의 한 행을 색이 바뀌는 지점으로 끊어 읽는다.

```python
row = [im.getpixel((x, y)) for x in range(w)]   # 색 경계로 끊어 폭을 센다
```

- 잰 값을 **의도한 상수와 대조**한다 — 패널 74 · 패널 사이 2 · 카드 사이 10 · gutter 16
- 어긋난 자리가 원인을 가리킨다. 안쪽 gap 은 살고 바깥 gap 만 죽었으면 범인은 `contentContainer` 다
- 텍스트 행의 첫 어두운 픽셀로 **들여쓰기**를 잰다 — 본문만 gutter 를 잃은 경우가 이렇게 잡힌다

시안 대조도 같다. 감으로 "맞는 것 같다"는 대조가 아니다.

## 5. 네이티브가 소유하는 것

- **safe-area inset 은 그 면을 그리는 컴포넌트가 먹는다.** 부모가 대신 패딩을 주면 탭바 면이 홈 인디케이터까지 안 내려간다
- **부모의 `overflow: hidden` 은 네이티브 그리기 뷰를 안 잘라준다.** radius 는 칠하는 뷰 자신에 준다 — 그라디언트 · 이미지 · 비디오

## 판정

1. 이 배열의 길이를 **내가 아는가** — 모르면 `FlatList`
2. `renderItem` `useCallback` · 도메인 `keyExtractor` · 아이템 `memo` 셋이 다 있는가
3. 이 prop 이 `className` 계열인가 — `FlatList` 면 style 로
4. 간격이 맞는다고 **잰 적이 있는가**, 봤을 뿐인가

## 안 하는 것

| 하지 않는 것 | 이유 |
|---|---|
| 서버가 개수를 정하는 목록을 `ScrollView` + `map` | 화면 밖까지 전부 그린다 |
| 화면 본문을 `FlatList` | 슬롯 순서가 `data` 가 되고 이득이 없다 |
| `FlatList` 에 `contentContainerClassName` | 조용히 안 붙는다 |
| 스켈레톤을 `FlatList` 로 | 개수가 고정이면 가상화할 게 없다 |
| 부모가 대신 먹는 safe-area | 면이 인디케이터까지 안 내려간다 |
| 스크린샷을 눈으로만 대조 | 사라진 16px 은 안 보인다 |
