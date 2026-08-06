#!/usr/bin/env python3
"""Validate AtlasHQ skill packages against JSON schemas.

Usage:
  python scripts/skills/validate_skill_package.py
  python scripts/skills/validate_skill_package.py --skill engineering_manager
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: pyyaml. Install it in your Python environment first."
    ) from exc

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: jsonschema. Install it in your Python environment first."
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / ".ai" / "skills"
SCHEMA_ROOT = SKILLS_ROOT / "schema"
REGISTRY_PATH = SKILLS_ROOT / "registry.yaml"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_instance(instance: Any, schema: dict[str, Any], name: str) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: str(err.path))
    messages: list[str] = []
    for err in errors:
        location = ".".join(str(item) for item in err.path) or "<root>"
        messages.append(f"{name}: {location}: {err.message}")
    return messages


def resolve_skill_paths(skill_id: str) -> dict[str, Path]:
    base = SKILLS_ROOT / skill_id
    return {
        "root": base,
        "manifest": base / "skill.yaml",
    }


def validate_skill(skill_id: str) -> list[str]:
    errors: list[str] = []
    paths = resolve_skill_paths(skill_id)
    if not paths["manifest"].exists():
        return [f"{skill_id}: missing manifest at {paths['manifest']}"]

    manifest = load_yaml(paths["manifest"])
    package_schema = load_json(SCHEMA_ROOT / "skill-package.schema.json")
    workflow_schema = load_json(SCHEMA_ROOT / "workflow.schema.json")
    policies_schema = load_json(SCHEMA_ROOT / "policies.schema.json")
    tools_schema = load_json(SCHEMA_ROOT / "tools.schema.json")

    errors.extend(validate_instance(manifest, package_schema, f"{skill_id}/skill.yaml"))

    artifacts = manifest.get("artifacts", {}) if isinstance(manifest, dict) else {}
    for artifact_name, schema in [
        ("workflow", workflow_schema),
        ("policies", policies_schema),
        ("tools", tools_schema),
    ]:
        rel = artifacts.get(artifact_name)
        if not rel:
            errors.append(f"{skill_id}: artifacts.{artifact_name} is missing")
            continue
        artifact_path = paths["root"] / rel
        if not artifact_path.exists():
            errors.append(f"{skill_id}: missing artifact file {artifact_path}")
            continue
        artifact_data = load_yaml(artifact_path)
        errors.extend(validate_instance(artifact_data, schema, f"{skill_id}/{rel}"))

    prompt_rel = artifacts.get("prompt") if isinstance(artifacts, dict) else None
    if not prompt_rel:
        errors.append(f"{skill_id}: artifacts.prompt is missing")
    else:
        prompt_path = paths["root"] / prompt_rel
        if not prompt_path.exists():
            errors.append(f"{skill_id}: missing prompt file {prompt_path}")

    for test_rel in manifest.get("tests", []) if isinstance(manifest, dict) else []:
        test_path = paths["root"] / test_rel
        if not test_path.exists():
            errors.append(f"{skill_id}: missing test file {test_path}")

    return errors


def skill_ids_from_registry() -> list[str]:
    registry = load_yaml(REGISTRY_PATH)
    entries = registry.get("skills", []) if isinstance(registry, dict) else []
    ids: list[str] = []
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            ids.append(entry["id"])
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AtlasHQ skill packages")
    parser.add_argument("--skill", help="Validate only one skill id from registry")
    args = parser.parse_args()

    ids = skill_ids_from_registry()
    if args.skill:
        if args.skill not in ids:
            print(f"Skill '{args.skill}' not found in {REGISTRY_PATH}")
            return 2
        ids = [args.skill]

    all_errors: list[str] = []
    for skill_id in ids:
        all_errors.extend(validate_skill(skill_id))

    if all_errors:
        print("Skill validation failed:")
        for line in all_errors:
            print(f"- {line}")
        return 1

    print(f"Skill validation passed for {len(ids)} skill(s): {', '.join(ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
