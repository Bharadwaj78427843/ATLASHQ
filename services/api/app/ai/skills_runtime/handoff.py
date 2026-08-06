"""
app/ai/skills_runtime/handoff.py

Protocol for managing handoffs between skills in an orchestration graph.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SkillHandoff:
    from_skill: str
    to_skill: str
    payload: dict[str, Any]
    trigger: str
    execution_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HandoffProtocol:
    def __init__(self) -> None:
        self._history: list[SkillHandoff] = []

    def create_handoff(
        self,
        from_skill: str,
        to_skill: str,
        payload: dict[str, Any],
        trigger: str,
        execution_id: str,
    ) -> SkillHandoff:
        handoff = SkillHandoff(
            from_skill=from_skill,
            to_skill=to_skill,
            payload=payload,
            trigger=trigger,
            execution_id=execution_id,
        )
        self._history.append(handoff)
        return handoff

    def resolve_inputs(
        self, target_skill: str, execution_id: str, available_outputs: dict[str, dict[str, Any]], requires: list[str]
    ) -> dict[str, Any]:
        """
        Resolve required inputs for a target skill based on available outputs from previously executed skills.
        `available_outputs` is a map of { skill_id: { output_key: output_value } }.
        """
        resolved: dict[str, Any] = {}
        for req in requires:
            # req could be "skill_id.output_key" or just "output_key"
            match = re.match(r"^([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)$", req)
            if match:
                source_skill, key = match.groups()
                if source_skill in available_outputs and key in available_outputs[source_skill]:
                    resolved[req] = available_outputs[source_skill][key]
            else:
                # search all available outputs
                found = False
                for source_skill, outputs in available_outputs.items():
                    if req in outputs:
                        resolved[req] = outputs[req]
                        found = True
                        break
                if not found:
                    pass # We just don't resolve it if missing, validation might catch it later

        return resolved
