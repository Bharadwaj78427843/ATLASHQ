from __future__ import annotations

from app.ai.skills_runtime.errors import ToolPermissionDeniedError
from app.ai.skills_runtime.models import SkillPackage


class ToolPermissionEngine:
    def ensure_step_tools_allowed(self, skill: SkillPackage, step_id: str, tools: list[str]) -> None:
        allowed = set(skill.tools)
        for tool in tools:
            if tool not in allowed:
                raise ToolPermissionDeniedError(
                    f"Skill '{skill.name}' cannot use tool '{tool}' in step '{step_id}'. Allowed: {sorted(allowed)}"
                )
