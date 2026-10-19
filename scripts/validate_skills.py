#!/usr/bin/env python3
"""Offline packaging checks. These do not evaluate agent behavior or SaaS access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate frontmatter keys instead of silently replacing them."""


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str):
            raise ValueError("frontmatter keys must be strings")
        if key in result:
            raise ValueError(f"duplicate frontmatter key: {key}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\s]+)\)")
FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc
    data = yaml.load("\n".join(lines[1:end]), Loader=UniqueKeyLoader)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, "\n".join(lines[end + 1:])


def validate_skill(path: Path) -> list[str]:
    errors = []
    try:
        data, body = read_frontmatter(path)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        return [f"{path}: {exc}"]
    if set(data) - FIELDS:
        errors.append("unsupported frontmatter fields")
    name = data.get("name")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        errors.append("name must be <=64 lowercase ASCII letters/digits with single hyphens")
    elif path.parent.name != name:
        errors.append("name must match the skill directory")
    description = data.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        errors.append("description must contain 1-1024 characters")
    if data.get("license") != "Apache-2.0":
        errors.append("repository skills must declare Apache-2.0")
    for field, maximum in (("compatibility", 500), ("allowed-tools", None)):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a nonempty string")
            elif maximum and len(value) > maximum:
                errors.append(f"{field} must be <= {maximum} characters")
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()
    ):
        errors.append("metadata must map strings to strings")
    if not body.strip():
        errors.append("skill body is empty")
    if len(path.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("keep SKILL.md at or below 500 lines; use references")
    for name in ("LICENSE", "NOTICE"):
        if not (path.parent / name).is_file():
            errors.append(f"missing standalone distribution file: {name}")
    return [f"{path}: {error}" for error in errors]


def validate_links(path: Path, boundary: Path) -> list[str]:
    """Check simple inline Markdown links used by this repository, not remote URLs."""
    errors = []
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        parts = urlsplit(target)
        if parts.scheme:
            if parts.scheme not in {"https", "mailto"}:
                errors.append(f"{path}: unsupported link scheme: {target}")
            continue
        if parts.netloc:
            errors.append(f"{path}: use explicit HTTPS URLs: {target}")
            continue
        if not parts.path:
            continue
        destination = (path.parent / unquote(parts.path)).resolve()
        if not destination.is_relative_to(boundary.resolve()):
            errors.append(f"{path}: link escapes distribution boundary: {target}")
        elif not destination.exists():
            errors.append(f"{path}: missing link target: {target}")
    return errors


def validate_scenarios(path: Path, skill_names: set[str]) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"{path}: {exc}"]
    if not isinstance(data, list) or not data:
        return [f"{path}: scenarios must be a nonempty list"]
    seen = set()
    fields = {"id", "skill", "prompt", "context", "must", "must_not"}
    for index, case in enumerate(data):
        prefix = f"{path}: scenario {index}"
        if not isinstance(case, dict) or set(case) != fields:
            errors.append(f"{prefix}: expected fields {sorted(fields)}")
            continue
        identifier = case["id"]
        if not isinstance(identifier, str) or not NAME.fullmatch(identifier):
            errors.append(f"{prefix}: invalid scenario id")
        elif identifier in seen:
            errors.append(f"{prefix}: duplicate scenario id: {identifier}")
        else:
            seen.add(identifier)
        if not isinstance(case["skill"], str) or case["skill"] not in skill_names:
            errors.append(f"{prefix}: unknown skill")
        for field in ("prompt", "context"):
            if not isinstance(case[field], str) or not case[field].strip():
                errors.append(f"{prefix}: {field} must be a nonempty string")
        for field in ("must", "must_not"):
            value = case[field]
            if not isinstance(value, list) or not value or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                errors.append(f"{prefix}: {field} must be a nonempty list of strings")
    return errors


def validate_repository(root: Path) -> tuple[list[str], int, int]:
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("no skills found")
    skill_dirs = {skill.parent.resolve() for skill in skills}
    for path in skills:
        errors.extend(validate_skill(path))
        for name in ("LICENSE", "NOTICE"):
            local, original = path.parent / name, root / name
            if local.is_file() and original.is_file() and local.read_bytes() != original.read_bytes():
                errors.append(f"{local}: must match repository {name}")
    for name in ("LICENSE", "NOTICE"):
        if not (root / name).is_file():
            errors.append(f"missing repository {name}")
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        boundary = next((parent for parent in path.parents if parent.resolve() in skill_dirs), root)
        errors.extend(validate_links(path, boundary))
    scenario_file = root / "evals" / "scenarios.json"
    errors.extend(validate_scenarios(scenario_file, {skill.parent.name for skill in skills}))
    scenario_count = 0
    if not errors:
        scenario_count = len(json.loads(scenario_file.read_text(encoding="utf-8")))
    return errors, len(skills), scenario_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, skills, scenarios = validate_repository(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Validated {skills} skill package(s) and {scenarios} behavioral scenario definition(s).")
    print("Structural validation only; behavioral evaluations and live SaaS flows were not run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
