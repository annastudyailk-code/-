#!/usr/bin/env python3
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


errors: list[str] = []
names: dict[str, list[Path]] = collections.defaultdict(list)
skill_files = sorted(SKILLS.glob("*/SKILL.md"))

for path in skill_files:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        errors.append(f"{path}: missing YAML frontmatter")
        continue

    rows = [line for line in match.group(1).splitlines() if line.strip()]
    if len(rows) != 2 or not rows[0].startswith("name: ") or not rows[1].startswith("description: "):
        errors.append(f"{path}: frontmatter must contain only name and description")
        continue

    name = rows[0][6:].strip()
    try:
        description = json.loads(rows[1][13:].strip())
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid description: {exc}")
        continue
    if not NAME.fullmatch(name):
        errors.append(f"{path}: invalid skill name {name!r}")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{path}: empty description")
    if "<" in description or ">" in description:
        errors.append(f"{path}: angle brackets are not allowed in description")
    names[name].append(path)

    for raw in LINK.findall(text):
        target = raw.strip().split("#", 1)[0].strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "data:", "#", "/")):
            continue
        if target in {"url", "URL", "path", "PATH"}:
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"{path}: broken relative link {raw!r}")

for name, paths in names.items():
    if len(paths) > 1:
        errors.append(f"duplicate skill name {name!r}: {paths}")

for path in SKILLS.rglob("SKILL.md"):
    if path not in skill_files:
        errors.append(f"unexpected nested SKILL.md: {path}")

for path in ROOT.rglob("*"):
    if path.is_symlink() and not path.exists():
        errors.append(f"broken symlink: {path}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)

print(f"OK: {len(skill_files)} unique skills; frontmatter and local links are valid")

