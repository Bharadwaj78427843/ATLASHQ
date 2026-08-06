from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.ai.skills_runtime.errors import SkillInstallError, SkillNotFoundError


@lru_cache(maxsize=8)
def _read_registry(path: str) -> dict[str, Any]:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise SkillNotFoundError("Invalid registry format")
    return data


def discover_repo_root(start: Path) -> Path:
    cursor = start.resolve()
    for candidate in [cursor, *cursor.parents]:
        if (candidate / ".ai" / "skills" / "registry.yaml").exists():
            return candidate
    raise SkillNotFoundError("Unable to discover repository root with .ai/skills/registry.yaml")


class SkillRegistryService:
    def __init__(self, registry_path: Path | None = None) -> None:
        if registry_path is None:
            repo_root = discover_repo_root(Path(__file__))
            registry_path = repo_root / ".ai" / "skills" / "registry.yaml"
        self._registry_path = registry_path
        self._repo_root = self._registry_path.parent.parent.parent

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    @property
    def registry_path(self) -> Path:
        return self._registry_path

    def reload(self) -> None:
        _read_registry.cache_clear()

    def _load(self) -> dict[str, Any]:
        return _read_registry(str(self._registry_path))

    def _write(self, data: dict[str, Any]) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        with self._registry_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)
        self.reload()

    def _split_skill_id(self, skill_id: str) -> tuple[str, str | None]:
        if "@" not in skill_id:
            return skill_id, None
        base, version = skill_id.split("@", 1)
        return base, version or None

    def list(self, *, active_only: bool = True) -> list[dict[str, Any]]:
        rows = self._load().get("skills", [])
        if not isinstance(rows, list):
            return []
        out: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            if active_only and row.get("status") not in {None, "active"}:
                continue
            out.append(row)
        return out

    def get(self, skill_id: str) -> dict[str, Any]:
        base_id, requested_version = self._split_skill_id(skill_id)
        for row in self.list(active_only=False):
            if row.get("id") != base_id:
                continue
            if requested_version and row.get("version") not in {None, requested_version}:
                continue
            return row
        raise SkillNotFoundError(f"Skill '{skill_id}' not found in registry")

    def skill_manifest_path(self, skill_id: str) -> Path:
        row = self.get(skill_id)
        rel = row.get("path")
        if not isinstance(rel, str) or not rel:
            raise SkillNotFoundError(f"Skill '{skill_id}' has no path in registry")
        return self._repo_root / rel

    def known_skill_ids(self) -> set[str]:
        return {row.get("id") for row in self.list(active_only=False) if isinstance(row.get("id"), str)}

    def upsert(self, row: dict[str, Any]) -> dict[str, Any]:
        skill_id = row.get("id")
        path = row.get("path")
        if not isinstance(skill_id, str) or not skill_id:
            raise SkillInstallError("Skill registry rows require a non-empty 'id'")
        if not isinstance(path, str) or not path:
            raise SkillInstallError("Skill registry rows require a non-empty 'path'")

        data = self._load()
        rows = data.get("skills", [])
        if not isinstance(rows, list):
            rows = []
        filtered = [existing for existing in rows if not (isinstance(existing, dict) and existing.get("id") == skill_id)]
        filtered.append(row)
        data["skills"] = filtered
        self._write(data)
        return row

    def remove(self, skill_id: str) -> None:
        data = self._load()
        rows = data.get("skills", [])
        if not isinstance(rows, list):
            raise SkillNotFoundError(f"Skill '{skill_id}' not found in registry")
        filtered = [row for row in rows if not (isinstance(row, dict) and row.get("id") == skill_id)]
        if len(filtered) == len(rows):
            raise SkillNotFoundError(f"Skill '{skill_id}' not found in registry")
        data["skills"] = filtered
        self._write(data)
