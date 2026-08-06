// 세션 시작 시 NORMS.md 를 컨텍스트로 주입한다.
// 플러그인이 설치된 기기 · 레포와 무관하게 항상 붙는다.
const { readFileSync } = require('node:fs')
const { join } = require('node:path')

const norms = readFileSync(join(__dirname, '..', 'NORMS.md'), 'utf8')

console.log(
  JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: `<paul-norms>\n${norms}\n</paul-norms>`,
    },
  })
)
