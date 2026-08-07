#!/usr/bin/env python3
"""자산 형식 검사 — `claude plugin validate` 가 놓치는 것들.

`claude plugin validate` 는 frontmatter 의 **YAML 파싱 오류를 잡지 못한다.**
`when_to_use` 값이 `"` 로 시작해 파싱이 깨졌을 때도 통과했고, 그 결과
스킬이 모델 목록에 실리지 않아 자동 발동이 조용히 죽었다. 이 스크립트가 그걸 잡는다.

    python3 scripts/validate-assets.py

판단 검사(축이 겹치지 않는가 · 트리거 문구가 실제 발화인가)는 자동화할 수 없다 —
AGENTS.md 를 직접 본다.
"""

import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML 이 필요하다: pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESC_CAP = 1536  # description + when_to_use 합계. 넘으면 목록에서 잘린다
BODY_MAX = 500  # SKILL.md 본문 줄 수

errors: list[str] = []


def fail(path: pathlib.Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def parse_frontmatter(path: pathlib.Path) -> dict | None:
    """frontmatter 를 YAML 로 파싱한다. 실패하면 None."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(path, "frontmatter 블록(`---`)이 없다")
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        # 이게 이 스크립트의 존재 이유다.
        detail = str(e).replace("\n", " ")[:200]
        fail(path, f"frontmatter YAML 파싱 실패 — {detail} (값이 `\"` 로 시작하면 `'…'` 로 감싼다)")
        return None
    if not isinstance(data, dict):
        fail(path, "frontmatter 가 매핑이 아니다")
        return None
    return data


def check_description(path: pathlib.Path, fm: dict) -> None:
    desc = fm.get("description")
    if not desc:
        fail(path, "`description` 이 없다 — 목록에서 발동 판정에 쓰인다")
        return
    total = len(str(desc)) + len(str(fm.get("when_to_use", "")))
    if total > DESC_CAP:
        fail(path, f"description + when_to_use 가 {total}자 — {DESC_CAP}자에서 잘린다")


def check_skills() -> None:
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        fm = parse_frontmatter(skill)
        if fm is None:
            continue
        if fm.get("name") != skill.parent.name:
            fail(skill, f"`name: {fm.get('name')}` 이 디렉터리명 `{skill.parent.name}` 과 다르다")
        check_description(skill, fm)
        # 자동 발동 스킬은 when_to_use 로 라우팅된다. 사용자 호출 전용은 리스팅에 안 들어가므로 불필요.
        if not fm.get("disable-model-invocation") and not fm.get("when_to_use"):
            fail(skill, "`when_to_use` 가 없다 — 자동 발동 스킬은 이걸로 라우팅된다")
        lines = len(skill.read_text(encoding="utf-8").splitlines())
        if lines > BODY_MAX:
            fail(skill, f"본문 {lines}줄 — {BODY_MAX}줄 넘으면 `references/` 로 내린다")


def check_agents() -> None:
    for agent in sorted((ROOT / "agents").glob("*.md")):
        fm = parse_frontmatter(agent)
        if fm is None:
            continue
        if fm.get("name") != agent.stem:
            fail(agent, f"`name: {fm.get('name')}` 이 파일명 `{agent.stem}` 과 다르다")
        check_description(agent, fm)
        if "when_to_use" in fm:
            fail(agent, "`when_to_use` 는 스킬 전용 필드다 — 에이전트는 description 에 담는다")


def check_manifests() -> None:
    plugin_path = ROOT / ".claude-plugin/plugin.json"
    market_path = ROOT / ".claude-plugin/marketplace.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        market = json.loads(market_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f".claude-plugin: JSON 파싱 실패 — {e}")
        return

    names = [p.get("name") for p in market.get("plugins", [])]
    if plugin.get("name") not in names:
        errors.append(
            f"plugin.json `name: {plugin.get('name')}` 이 marketplace.json plugins[].name {names} 에 없다"
        )
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(plugin.get("version", ""))):
        errors.append(f"plugin.json `version` 이 semver 가 아니다: {plugin.get('version')!r}")


def check_hooks() -> None:
    """hooks.json 이 파싱되는가 · 참조하는 스크립트가 실제로 있는가."""
    path = ROOT / "hooks/hooks.json"
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"hooks/hooks.json: JSON 파싱 실패 — {e}")
        return

    for event, blocks in cfg.get("hooks", {}).items():
        for block in blocks:
            for hook in block.get("hooks", []):
                cmd = hook.get("command", "")
                # ${CLAUDE_PLUGIN_ROOT}/hooks/x.js → hooks/x.js 가 실재하는가
                for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)", cmd):
                    if not (ROOT / ref).exists():
                        errors.append(f"hooks.json [{event}] 이 없는 파일을 가리킨다: {ref}")
                if "${CLAUDE_PLUGIN_ROOT}" not in cmd:
                    errors.append(
                        f"hooks.json [{event}] 의 command 에 ${{CLAUDE_PLUGIN_ROOT}} 가 없다 — "
                        f"설치 캐시 경로에서 깨진다"
                    )


def check_readme_tree() -> None:
    """README 구조도가 실제 자산을 전부 담고 있는가 — 유령 항목의 반대편."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assets = [p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")]
    assets += [p.name for p in (ROOT / "agents").glob("*.md")]
    assets += [p.name for p in (ROOT / "hooks").glob("*") if p.is_file()]
    for a in sorted(assets):
        if a not in readme:
            errors.append(f"README.md 구조도에 `{a}` 가 없다")


def main() -> int:
    check_skills()
    check_agents()
    check_hooks()
    check_manifests()
    check_readme_tree()

    if errors:
        print(f"✘ 형식 검사 실패 — {len(errors)}건\n")
        for e in errors:
            print(f"  • {e}")
        print("\n판단 검사는 자동화할 수 없다 — AGENTS.md 를 직접 본다.")
        return 1

    print("✔ 형식 검사 통과")
    print("  판단 검사는 AGENTS.md 를 직접 본다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
