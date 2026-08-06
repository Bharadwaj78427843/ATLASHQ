from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from app.ai.skills_runtime.models import SkillExecutionRequest


def _jsonify(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _jsonify(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _jsonify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonify(item) for item in value]
    return value


class SkillsPipeline:
    def __init__(self, runtime) -> None:
        self._runtime = runtime

    async def list(self) -> dict[str, Any]:
        skills: list[dict[str, Any]] = []
        for row in self._runtime.registry.list(active_only=False):
            skill_id = row.get("id")
            if not isinstance(skill_id, str) or not skill_id:
                continue
            try:
                package = self._runtime.loader.load(skill_id)
                skills.append({"valid": True, "registry_entry": row, "skill": _jsonify(package)})
            except Exception as exc:  # noqa: BLE001
                skills.append({"valid": False, "registry_entry": row, "skill_id": skill_id, "error": str(exc)})
        return {"skills": skills}

    async def get(self, skill_id: str) -> dict[str, Any]:
        package = self._runtime.loader.load(skill_id)
        return {"skill": _jsonify(package), "registry_entry": self._runtime.registry.get(skill_id)}

    async def schema(self, skill_id: str) -> dict[str, Any]:
        return self._runtime.loader.schema_bundle(skill_id)

    async def validate(self, skill_id: str | None = None, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
        if manifest is not None:
            candidate_id = skill_id or str(manifest.get("name") or "skill")
            self._runtime.loader.validate_manifest(manifest, skill_id=candidate_id)
            return {"skill_id": candidate_id, "valid": True}

        if not skill_id:
            raise ValueError("skill_id or manifest is required")

        skill = self._runtime.loader.load(skill_id)
        return {"skill_id": skill_id, "valid": True, "skill": _jsonify(skill)}

    async def execute(self, request: SkillExecutionRequest) -> dict[str, Any]:
        result = await self._runtime.execute(request)
        return _jsonify(result)

    async def install(self, row: dict[str, Any]) -> dict[str, Any]:
        previous: dict[str, Any] | None = None
        try:
            previous = self._runtime.registry.get(str(row["id"]))
        except Exception:  # noqa: BLE001
            previous = None

        self._runtime.registry.upsert(row)
        try:
            package = self._runtime.loader.load(str(row["id"]))
            return {"status": "installed", "registry_entry": row, "skill": _jsonify(package)}
        except Exception:
            if previous is None:
                self._runtime.registry.remove(str(row["id"]))
            else:
                self._runtime.registry.upsert(previous)
            raise

    async def uninstall(self, skill_id: str) -> dict[str, Any]:
        self._runtime.registry.remove(skill_id)
        return {"status": "uninstalled", "skill_id": skill_id}

    async def reload(self) -> dict[str, Any]:
        self._runtime.registry.reload()
        skills = await self.list()
        return {"status": "reloaded", "skills": skills["skills"]}