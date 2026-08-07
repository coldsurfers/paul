---
name: coldsurf-domain
description: COLDSURF 도메인 정본 — 공연/티켓 데이터 모델, SaaS→파트너십→마켓플레이스 로드맵, Fan Platform(공연 기록·취향 그래프) 비전, 파트너 benefit·fee 구조, 편집 페르소나.
when_to_use: billets · billets-app · billets-server · billets-admin · coldsurf 레포에서 작업할 때. 공연 · 티켓 · 공연장(venue) · 아티스트 · 라인업 · 포스터 · 예매 · 파트너가 등장하는 기능을 설계하거나 구현할 때. "이걸 뭐라고 부르지" · "이 기능이 로드맵 어디쯤이지" · "파트너한테 뭘 주지" 판단이 필요할 때.
---

# COLDSURF 도메인

**더 나은 티켓 생태계.** [coldsurf.io](https://coldsurf.io) · [github.com/coldsurfers](https://github.com/coldsurfers)

## 데이터 모델

```
Venue
 ├ Event (공연)
 │   ├ Lineup
 │   │   ├ Artist A
 │   │   └ Artist B
 │   ├ Poster
 │   └ Ticket Link
 └ 좌표 (geohash 기반)
```

좌표가 있으면 근처 공연 추천 · 지도 기반 탐색이 열린다.

**공연 등록 필드:** 제목 / 공연장 / 날짜·시간 / 라인업 / 포스터 / 티켓 링크 / 가격 / 장르 / 설명 / Instagram · Spotify · YouTube

**공연장 필드:** 이름 / 주소 / 좌표 / 수용 인원 / 웹사이트 / Instagram

## 전략 순서: SaaS → 파트너십 → Marketplace

플랫폼만 있으면 공급자가 참여할 이유가 없다. SaaS 가 있으면 구조가 바뀐다.

```
공연장 / 아티스트 → COLDSURF SaaS (관리툴) → 자동으로 COLDSURF 노출
```

업무 도구와 플랫폼 노출이 동시에 된다.

### Phase 1 — Admin System

**역할 3종:** `Admin`(운영자) · `Venue`(공연장) · `Organizer/Artist`(기획자·아티스트)

**메뉴 5개면 충분하다:** Dashboard(이번달 공연 수 · upcoming) / Venues / **Events(가장 중요)** / Artists / Analytics(optional)

**UX 목표: 공연 등록 30초** — 자동 완성, 이전 공연 복사, 아티스트 검색.

**킬러 기능:** 공연 등록 → 자동으로 멋진 공연 페이지 생성 → 공유 링크. 공연장은 보통 포스터 + 인스타 링크뿐이다. 페이지를 대신 만들어주면 파트너십 설득력이 생긴다.

### 파트너 Benefit · Fee

| 단계 | 내용 |
|------|------|
| Discovery | 새로운 팬 발견, 인디씬 노출 |
| 티켓 판매 | 수수료 5~10% (플랫폼 성장 후) |
| 팬 데이터 | 지역/공연 인기 분석 (Spotify for Artists 모델) |
| 홍보 자동화 | 공연 등록 → 자동 SNS 공유 링크 |

```
초기: 등록 무료 · 홍보 무료
성장: 티켓 판매 수수료 5~10%
이후: 프리미엄 SaaS + 데이터 분석 + 마케팅 도구
```

레퍼런스: **Eventbrite**(이벤트 SaaS → marketplace), **Resident Advisor**(클럽 이벤트 등록 → 티켓 marketplace)

## Phase 2 — Fan Platform

**"Spotify + Letterboxd for Live Music"**

라이브 공연 시장에 아직 없는 것: **팬 행동 데이터 플랫폼.** 진짜 금광은 *"누가 어떤 공연을 실제로 갔는가"*(real attendance data).

왜 없나 — ① 티켓 플랫폼(인터파크 등)이 데이터 독점 ② 공연장이 공유 안 함 ③ KOPIS 는 산업 통계 시스템이라 팬 경험이 없음.

```
공연 발견 (Discovery)
  ↓
공연 기록 (Record)        ← 핵심 추가
  ↓
취향 데이터 (Taste Graph)
  ↓
추천 → 팬 커뮤니티 → 티켓 / 산업 데이터 (B2B)
```

프로필 예시: *본 공연 184개 / 좋아하는 장르 stoner rock · indie rock / 자주 가는 공연장 홍대*

쌓이면 — 공연 추천("좋아할 확률 87%"), 투어 계획("이 도시에 팬이 많다"), 페스티벌 라인업("이 두 밴드 팬층이 겹친다").

**수익: 겉은 B2C, 돈은 B2B.** 초기 티켓 수수료 5~15% → 중기 공연 산업 SaaS(기획사·페스티벌에 팬 데이터) → 장기 아티스트 마케팅 · 프리미엄 팬 서비스.

### 전략 A — 작지만 확실한 팬 시장

DIY 를 즐길 정도로 음악에 조예 깊은 사람들부터. 씬 문화를 **플랫폼화하지 않고 증폭**시킨다. 레퍼런스는 **Bandcamp** — 대형 플랫폼이 관심 없는 영역 → 깊은 팬 → 충성 커뮤니티.

핵심 유저는 전체 음악 팬의 5~10%. 하지만 가장 열심히 쓰는 집단이다.

### 초기 1000명

기록 서비스의 성패는 **처음 1000명이 누구인가**에서 갈린다. 타깃 — 페스티벌을 매년 찾아가는 사람 / 특정 씬(홍대 인디) 팬 / 셋리스트와 공연 자체를 기억하고 싶은 사람.

동기: ① 개인 공연 히스토리 타임라인 ② 팬 정체성("공연 200번 본 사람") ③ 씬 참여 정체성("홍대 인디씬 참여자")

### 한국 시장 특성

- 대형 공연(내한·아이돌·페스티벌) 중심이라 discovery 필요성이 낮다
- 인디씬(홍대·합정·상수) 정보는 분산 → "공연이 있는지 몰라서 못 간다"
- KOPIS 는 인디·클럽 공연 누락이 많다
- Dice 모델 직접 이식은 어렵다. 일본 시장과 구조가 더 유사하다

### 레퍼런스

| 서비스 | 분야 | 구조 |
|--------|------|------|
| Letterboxd | 영화 | 기록 → 취향 → 커뮤니티 |
| Goodreads | 책 | 기록 → 추천 → 커뮤니티 |
| Bandcamp | 음악 | DIY 팬 → 아티스트 직접 연결 |
| Setlist.fm | 공연 | setlist 기록 (공연 *경험* 기록은 아님) |

**공연 경험 기록 플랫폼은 아직 없다.** 여기가 COLDSURF 의 기회.

## 편집 페르소나

매체 픽 · 추천 · 헤드라인의 북극성은 **tomwaters** — 14년치 Bandcamp 컬렉션 1,103건을 쌓은 사람의 결. 큐레이터의 권위가 아니라 오래 모은 사람의 손때로 말한다.

## 기술 스택

```
Admin (웹)     Next.js
API            Supabase / Hono on Cloudflare Workers
App (모바일)    React Native
```

서버별 상세 규약은 `paul-stack` 스킬 참조.
