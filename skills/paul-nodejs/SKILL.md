---
name: paul-nodejs
description: Node 서버 안의 레이어 — route(계약) · service(흐름) · repository(DB) · module(요청당 조립). 클래스 + 생성자 주입, 데코레이터·DI 컨테이너 없음. NestJS 의 모양은 가져오되 컨테이너는 안 가져오는 이유.
when_to_use: 서버 라우트/핸들러를 새로 쓰거나 고칠 때. 핸들러 안에서 ORM(prisma 등)을 직접 부르고 있을 때. `*.route.ts` · `*.service.ts` · `*.repository.ts` · `domain/` 을 열 때. "이 라우트 좀 나눠줘" · "repository 패턴 적용하자" · "레이어 분리" · "핸들러가 너무 길다" 요청. **tsyringe · inversify · NestJS · reflect-metadata · 데코레이터 · `interface` + `impl` 쌍을 제안하기 전에 반드시 먼저 읽는다.**
---

# Node 서버 레이어

컴포넌트 안에 무엇을 쓰는가는 `paul-react`. **이건 서버 핸들러 안에 무엇을 쓰는가다.**

도구·설치·라우트 등록 절차(pnpm · Biome · `createRoute` · api-sdk · prisma 3단 sync)는 `paul-stack`. 디렉터리 일반론은 `paul-layout`. 여기는 **레이어와 그 사이 계약**만 다룬다.

## 네 자리

```
routes/<name>.route.ts              계약      OpenAPI 스펙 · 가드/레이트리밋 · 실행 순서
domain/<name>/<name>.service.ts     흐름      여러 단계를 잇는다 · 외부로 나가는 문안
domain/<name>/<name>.repository.ts  DB        ORM 을 부르는 유일한 자리
domain/<name>/<name>.module.ts      조립      요청당 한 번, 생성자에 물린다
domain/<name>/index.ts              배럴      module 만 내보낸다
```

NestJS 로 치면 `@Controller` · `@Injectable` · `@Injectable` · `@Module` 이다. **모양은 가져오고 데코레이터는 안 가져온다** — 아래 「컨테이너를 안 쓰는 이유」.

라우트에 ORM 호출이 하나라도 남아 있으면 분리가 덜 된 것이다.

## 규율

**클래스 + 생성자 주입.** 의존은 필드로 고정한다. 메서드마다 `prisma` 를 인자로 넘기고 있으면 그게 "느슨한" 느낌의 원인이다.

```ts
export class DataCorrectionRepository {
  constructor(private readonly prisma: PrismaClient) {}
  async create(params: CreateBodyDTO): Promise<void> { … }
}
```

**인자는 named object.** `create(id, kind, value)` 가 아니라 `create({ id, kind, value })`.

**ORM row 를 레이어 밖으로 내보내지 않는다.** repository 는 호출부가 그대로 쓸 값만 돌려준다. `include` 상수 · 매퍼 · where 술어도 여기 산다.

**`interface` + `impl` 쌍을 만들지 않는다.** 1:1 로 늘어나고 두 번째 구현이 영영 안 오면 그건 seam 이 아니라 세리머니다. 갈아끼울 일이 실제로 생기면 그때 인터페이스를 위에 얹는다 — 클래스가 이미 있으니 값이 싸다.

**service 는 흐름이 있을 때만 만든다.** repository 를 그대로 통과시키는 메서드 하나짜리 service 는 층이 아니라 별칭이다.

**라우트가 라우트를 import 하지 않는다.** 의존은 `route → domain → lib` 한 방향. 공유가 필요하면 아래로 내린다 — "그 매핑 어디 있냐"의 답이 "다른 **라우트** 파일"이 되는 순간 진 것이다.

**500 계약은 손으로 지키지 않는다.** 핸들러마다 `try/catch` 를 쓰면 반드시 빠뜨린다(실측: 134개 중 64개가 빠져 OpenAPI 에 선언한 `{ code, message }` 대신 프레임워크 기본 plain text 가 나갔다). 전역 에러 핸들러 하나로 잡는다.

## module — 조립은 함수 한 개

```ts
export function createDataCorrectionModule(c: Context<AppEnv>) {
  const repository = new DataCorrectionRepository(dbFromEnv(c.env))
  return { service: new DataCorrectionService(repository, c.env) }
}
```

핸들러는 이 한 줄만 안다.

```ts
const { service } = createDataCorrectionModule(c)
await service.submit(body)
```

## 컨테이너를 안 쓰는 이유

tsyringe · inversify 를 제안하기 전에 이 셋을 먼저 확인한다.

**1. 런타임이 요청 단위로 격리되면 컨테이너가 줄여줄 코드가 없다.** Cloudflare Workers 처럼 요청마다 DB 클라이언트를 새로 만드는 환경에서는 모든 provider 가 NestJS 로 치면 `Scope.REQUEST` 다. 그 상태면 컨테이너도 매 요청 서브트리를 다시 만든다 — 조립 함수 한 개가 짧다. 전역 싱글턴에 커넥션을 물리면 요청 간에 샌다.

**2. 데코레이터 값이 비싸다.** `experimentalDecorators` + `emitDecoratorMetadata`(TS5 표준 데코레이터가 아니라 legacy 쪽) + `reflect-metadata` 전역 import 가 붙는다.

**3. 인터페이스는 메타데이터로 안 읽힌다.** 런타임 타입이 없어서 `@inject('X')` 문자열 토큰 등록부를 손으로 유지해야 한다. 위의 "interface + impl 금지"와 정면으로 충돌한다.

**재판단 시점** — 한 라우트가 의존을 3개 넘게 물고(repository 여럿 + mailer + cache), 두 번째 구현이나 테스트 더블이 **실제로** 필요해질 때. 그전까지 컨테이너는 조립할 게 없다.

장기 프로세스(Lambda 컨테이너 재사용 · 상주 Node)라면 1번이 약해진다. 그래도 2·3번은 그대로다.

## 되짚기

- 라우트에 ORM 호출이 남아 있는가 → repository 로
- service 가 pass-through 하나뿐인가 → 지우고 라우트가 repository 를 직접
- 라우트가 라우트를 import 하는가 → 공유 조각을 `domain/` · `lib/` 로
- 판단(왜 컨테이너를 안 썼는지 · 왜 인터페이스가 없는지)은 **파일 상단 주석에 남긴다.** 다음 도메인이 같은 질문을 다시 하지 않게.
