#!/usr/bin/env node
// 기기별 `~/.claude/settings.json` 을 이 플러그인이 요구하는 상태로 맞춘다.
//
// 플러그인은 스킬 · 훅 · 명령만 실을 수 있고 **전역 설정은 못 건드린다.**
// 그런데 NORMS §4.5 는 `TaskCreate` 를 규범으로 요구하고, 그 툴은
// `env.CLAUDE_CODE_ENABLE_TODO_TOOLS` 가 있어야 세션에 올라온다.
// 그래서 이 한 줄만은 기기마다 사람이 넣어야 한다 — 그걸 자동화한 것이 이 스크립트다.
//
//     node scripts/setup-settings.js
//
// 몇 번을 돌려도 결과가 같다. 이미 맞으면 아무것도 쓰지 않는다.

const { readFileSync, writeFileSync, statSync, existsSync, renameSync, chmodSync } = require('node:fs')
const { join, dirname } = require('node:path')
const { homedir } = require('node:os')

// 키 → 왜 필요한가. 값이 다르면 덮어쓴다.
const REQUIRED_ENV = {
  // NORMS §4.5 의 터미널 체크리스트(TaskCreate · TaskUpdate)를 켠다.
  CLAUDE_CODE_ENABLE_TODO_TOOLS: '1',
}

const SETTINGS = join(homedir(), '.claude', 'settings.json')

function readSettings() {
  if (!existsSync(SETTINGS)) return {}
  const raw = readFileSync(SETTINGS, 'utf8').trim()
  if (!raw) return {}
  try {
    return JSON.parse(raw)
  } catch (e) {
    // 깨진 파일을 덮어쓰면 hooks · permissions · plugins 가 통째로 날아간다.
    console.error(`✘ ${SETTINGS} 가 올바른 JSON 이 아니다 — ${e.message}`)
    console.error('  손으로 고친 뒤 다시 실행한다. 아무것도 쓰지 않았다.')
    process.exit(1)
  }
}

const settings = readSettings()
const env = settings.env ?? {}

const changed = Object.entries(REQUIRED_ENV).filter(([k, v]) => env[k] !== v)

if (changed.length === 0) {
  console.log(`✔ ${SETTINGS} — 이미 맞다`)
  process.exit(0)
}

for (const [k, v] of changed) env[k] = v
settings.env = env

// 새로 만드는 경우 0600. 기존 파일이면 원래 퍼미션을 유지한다 —
// 이 파일에는 API 키가 들어가는 자리라 rename 이 권한을 넓히면 안 된다.
const mode = existsSync(SETTINGS) ? statSync(SETTINGS).mode & 0o777 : 0o600

// 같은 디렉터리에 쓰고 rename — 도중에 죽어도 반쪽짜리 설정이 남지 않는다.
const tmp = join(dirname(SETTINGS), `.settings.json.${process.pid}.tmp`)
writeFileSync(tmp, `${JSON.stringify(settings, null, 2)}\n`, { encoding: 'utf8', mode })
renameSync(tmp, SETTINGS)
chmodSync(SETTINGS, mode)

for (const [k, v] of changed) console.log(`✔ env.${k} = ${JSON.stringify(v)}`)
console.log(`  ${SETTINGS} 에 반영했다. 실행 중인 세션에도 바로 붙는다.`)
