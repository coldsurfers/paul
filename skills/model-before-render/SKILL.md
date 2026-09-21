---
name: model-before-render
description: 기획(요구사항)을 컴포넌트가 아니라 자료구조로 먼저 번역하고, 외부 스토어 경계(store · subscribe · useSyncExternalStore)로 React 에 붙이는 설계 절차. 정책을 `if` 문이 아니라 자료구조 선택으로 흡수해 쓸 코드를 없앤다.
when_to_use: 기획 · 요구사항을 받고 `useState` · `useEffect` 부터 치려는 순간. 상태 로직이 컴포넌트 안에서 불어나기 시작할 때. 스트림 · 구독 · 큐 · 선택 · 되돌리기 · 낙관적 업데이트처럼 *정책이 있는* 상태를 다룰 때. "이 상태 어디에 두지" · "전역 상태 필요한가" · "리렌더가 많은데" 판단이 필요할 때. `useState` 대여섯 개를 `useEffect` 로 서로 동기화하고 있을 때. zustand · jotai 같은 라이브러리부터 고르려는 순간 — 도구보다 모양이 먼저다. 코드를 어디에 두고 컴포넌트 안에 무엇을 쓰는가는 `paul-frontend` 의 몫이라 여기서 가로채지 않는다.
---

# Model Before Render

**기획을 컴포넌트로 옮기지 말고, 자료구조로 먼저 옮긴다.**

요구사항을 읽자마자 `useState`를 치면 정책이 전부 `if` 문과 `useEffect`로 흩어진다. 자료구조를 먼저 고르면 그 정책 중 상당수가 **쓸 필요가 없어진다.** 코드가 짧아지는 건 줄여 써서가 아니라 쓸 일이 사라져서다.

무엇을 만드는지는 `code-to-product`, 그 상태를 **어느 파일에 두고 컴포넌트 안에 무엇을 쓰는지**는 `paul-frontend`. 이 문서는 그 사이 — **상태의 모양을 정하는 한 스텝**이다.

**트레이드오프:** 이 절차는 설계에 10~20분을 먼저 쓴다. 한 화면에서만 살다 죽는 상태라면 과하다 — §7을 먼저 본다.

---

## §1. 정책을 문장으로 먼저 적는다

코드를 열기 전에, 기획에서 **규칙에 해당하는 문장만** 뽑아 명령형 한 줄씩 적는다.

```
- 같은 종목 틱은 마지막 것만 남긴다
- 이미 예약돼 있으면 또 예약하지 않는다
- 늦게 도착한 과거 틱은 버린다
- 화면 밖 행은 구독하지 않는다
```

이 목록이 **설계의 입력**이다. 이걸 안 적고 시작하면 정책이 코드 여기저기에 흩어진 뒤에야 발견된다.

> 문장이 안 나오면 아직 기획을 이해 못 한 것이다. 코딩이 아니라 질문을 할 차례다.

---

## §2. 문장을 자료구조로 번역한다 ← 이 절이 핵심

각 문장에 자료구조를 하나씩 붙인다.

| 정책 문장 | 자료구조 |
|---|---|
| "같은 X는 마지막 것만" | `Map<key, V>` — set 하면 덮어써진다 |
| "중복 없이 모은다" | `Set<Id>` |
| "이미 됐으면 건너뛴다" | nullable id 필드 **하나** (`number \| null`) |
| "순서대로 처리한다" | 배열 큐 |
| "되돌릴 수 있다" | 스택 2개 (past / future) |
| "가장 최근 N개" | 배열 + `slice(-N)` |
| "오래된 건 버린다" | 타임스탬프 비교 + early return |
| "기준점에서부터 범위" | 앵커 필드 + 순서 배열의 인덱스 두 개 |

### 판정 기준

**정책 문장이 `if` 문으로 남아 있으면 아직 덜 접힌 것이다.**

```ts
// ❌ 정책이 코드로 남았다
if (!buffer.some((t) => t.symbol === tick.symbol)) buffer.push(tick)
else buffer[buffer.findIndex(...)] = tick

// ✅ 자료구조가 정책을 흡수했다
pending.set(tick.symbol, tick)
```

### 필드 하나가 두 의미를 겸하게 한다

```ts
// ❌ 두 값이 어긋날 수 있다
private isScheduled = false
private frameId = 0

// ✅ 어긋날 수가 없다
private frame: number | null = null
```

`null`이면 "예약 안 됨", 값이 있으면 "예약됨 + 그 ID". **상태 개수가 줄면 버그 종류가 줄어든다.**

`??=`가 여기에 붙는다 — 왼쪽이 `null`일 때만 오른쪽이 **실행된다**(단축 평가).

```ts
this.frame ??= requestAnimationFrame(this.flush)
```

`||=`를 쓰면 안 된다. `0`도 falsy라 "없음"으로 오판한다. 금융·수량 데이터에서 특히 위험하다.

---

## §3. 읽기면과 쓰기면을 가른다

**누가 쓰고 누가 읽는지, 그리고 빈도가 같은지** 묻는다.

빈도가 다르면 **버퍼를 나눈다** (double buffering).

```
pending   ← 생산자가 쓴다 (초당 500번)
snapshot  ← React가 읽는다 (프레임당 1번)
```

둘이 다른 객체라 서로를 방해할 수 없다. 렌더 도중 값이 바뀌는 사고(tearing)가 **구조적으로** 불가능해진다.

빈도가 같으면 나누지 않는다. 안 나눠도 될 걸 나누는 것도 과설계다.

---

## §4. 경계를 셋만 연다

스토어의 공개 API는 **세 방향**이면 충분하다.

```ts
write(input)                        // 쓰기 — 렌더를 일으키지 않는다
read(key)                           // 읽기 — 동기, 부작용 없음
subscribe(key, notify): () => void  // 알림 — 해제 함수를 돌려준다
```

- `write`는 **렌더를 직접 일으키지 않는다.** 언제 그릴지는 스토어가 정한다
- `read`는 부작용이 없다
- `subscribe`는 반드시 **해제 함수**를 돌려준다

여기에 네 번째를 붙이고 싶어지면, 그건 보통 **다른 스토어가 필요하다는 신호**다.

---

## §5. hook으로 React에 붙인다

```ts
export function useEntry(key: string) {
  return useSyncExternalStore(
    useCallback((notify) => store.subscribe(key, notify), [key]),
    useCallback(() => store.read(key), [key]),
    () => undefined, // SSR 스냅샷
  )
}
```

### ⚠️ `getSnapshot` 참조 안정성 — 여기서 제일 많이 터진다

`getSnapshot`은 **값이 안 변했으면 같은 참조**를 돌려줘야 한다. 아니면 React가 무한 루프를 돈다.

```ts
// ❌ 매번 새 객체 → Maximum update depth exceeded
() => ({ price: store.read(key)?.price })

// ✅ 스토어가 들고 있는 객체를 그대로
() => store.read(key)
```

그래서 §2에서 **불변 객체를 Map에 넣는** 모양이 중요하다. flush 때만 객체가 교체되니 그 사이 참조가 고정된다.

파생값이 필요하면 스토어 안에서 만들어 캐시하거나, 컴포넌트에서 `useMemo`로 만든다. `getSnapshot` 안에서 만들지 않는다.

### 구독은 가능한 좁게

전체 배열을 구독하면 하나만 바뀌어도 전부 리렌더된다. **키 단위로 구독**하면 바뀐 것만 깨어난다. 이게 `memo`보다 확실한 이유 — `memo`는 렌더가 시작된 뒤에 거르지만, 좁은 구독은 **렌더를 시작하지 않는다.**

---

## §6. 검산 4문항

다 쓰고 나서 스스로 묻는다.

1. **상태가 몇 개인가** — 줄일 수 있으면 줄인다 (§2의 "두 의미 겸하기")
2. **어긋날 수 있는 쌍이 있나** — 두 필드가 같은 사실을 중복 표현하면 언젠가 갈라진다
3. **화살표가 한 방향인가** — `쓰기 → 버퍼 → 스냅샷 → 리스너 → React`. 되돌아오는 선이 있으면 순환이다
4. **안 이쁜 곳이 어디인가** — 하나는 반드시 있다. 못 찾았으면 아직 안 본 것이다

---

## §7. 이 스킬을 쓰면 안 될 때

**정책이 없으면 자료구조를 설계할 게 없다.** 아래는 그냥 `useState`가 정답이다.

- 한 화면 안에서 살다 죽는 상태 (모달 열림, 탭 인덱스, 입력값)
- 규칙 문장이 §1에서 **한 줄도 안 나오는** 경우
- 서버 상태 — 캐시·재검증·경쟁 조건은 이미 풀린 문제다. 데이터 페칭 라이브러리를 쓴다

**신호:** `useState` 대여섯 개가 서로를 `useEffect`로 동기화하고 있으면, 그때 이 절차로 넘어온다.

---

## 워크스루 A — 고빈도 틱 코얼레싱

**§1 정책**
```
- 같은 종목 틱은 마지막 것만
- 이미 프레임이 예약됐으면 또 예약 안 함
- 늦게 온 과거 틱은 버림
```

**§2 번역** → `Map<symbol, Tick>` + `frame: number | null` + 타임스탬프 early return
**§3 분리** → 쓰기 초당 500회 / 읽기 초당 60회 → `pending` · `snapshot` 분리
**§4 경계** → `push` / `get` / `subscribe`

```ts
type Tick = { symbol: string; price: number; at: number }

class TickStore {
  private snapshot = new Map<string, Tick>()
  private pending = new Map<string, Tick>()
  private listeners = new Map<string, Set<() => void>>()
  private frame: number | null = null

  push(tick: Tick) {
    const prev = this.pending.get(tick.symbol) ?? this.snapshot.get(tick.symbol)
    if (prev && prev.at >= tick.at) return       // "과거 틱은 버린다"
    this.pending.set(tick.symbol, tick)          // "마지막 것만"
    this.frame ??= requestAnimationFrame(this.flush) // "이미 됐으면 건너뛴다"
  }

  private flush = () => {
    this.frame = null
    for (const [symbol, tick] of this.pending) {
      this.snapshot.set(symbol, tick)
      this.listeners.get(symbol)?.forEach((notify) => notify())
    }
    this.pending.clear()
  }

  subscribe(symbol: string, notify: () => void) {
    const set = this.listeners.get(symbol) ?? new Set()
    set.add(notify)
    this.listeners.set(symbol, set)
    return () => {
      set.delete(notify)
      if (set.size === 0) this.listeners.delete(symbol)
    }
  }

  get(symbol: string) {
    return this.snapshot.get(symbol)
  }
}
```

**정책 세 줄이 코드 세 줄이 됐다.** 분기문은 하나뿐이고 그건 "과거 틱 버리기" — 자료구조로 못 접히는 유일한 정책이다.

**덤으로 따라온 것들:** 백그라운드 탭에서 rAF가 멈춰도 `pending`이 Map이라 메모리가 키 개수로 묶인다. 복귀하면 첫 프레임이 최신값을 한 번에 칠한다. 설계하지 않았는데 Map을 고른 대가로 얻는다.

---

## 워크스루 B — 다중 선택 + 범위 선택

**§1 정책**
```
- 클릭하면 하나만 선택
- Cmd+클릭은 토글
- Shift+클릭은 직전 기준점부터 범위
- 같은 항목을 두 번 담지 않는다
```

**§2 번역**

| 문장 | 자료구조 |
|---|---|
| "두 번 담지 않는다" | `Set<Id>` ← 중복 체크 코드가 사라진다 |
| "직전 기준점" | `anchor: Id \| null` ← 필드 하나 |
| "기준점부터 범위" | 순서 배열 + 인덱스 두 개 `slice` |

```ts
class SelectionStore {
  private selected = new Set<string>()
  private anchor: string | null = null

  click(id: string, mode: 'single' | 'toggle' | 'range', order: string[]) {
    if (mode === 'toggle') {
      if (!this.selected.delete(id)) this.selected.add(id)  // "토글"
      this.anchor = id
    } else if (mode === 'range' && this.anchor) {
      const [a, b] = [order.indexOf(this.anchor), order.indexOf(id)].sort((x, y) => x - y)
      for (const key of order.slice(a, b + 1)) this.selected.add(key) // Set 이라 중복 무시
    } else {
      this.selected = new Set([id])
      this.anchor = id
    }
    this.emit()
  }
}
```

`order`를 **필드로 들지 않고 인자로 받는다** — 정렬·필터는 이 스토어의 결정이 아니다(§4: 결정을 하나만 든다).

---

## 패턴 이름 — 설명할 때 쓴다

즉흥이 아니라 **선택**으로 들리게 한다.

- **Double buffering** — 쓰기면/읽기면 분리 (§3)
- **Scheduling dedupe** — `??=`로 예약 접기 (§2)
- **External store + pull snapshot** — React 밖에 진실을 두고 당겨 읽기 (§5)
