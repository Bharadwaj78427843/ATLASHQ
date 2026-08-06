from __future__ import annotations

from typing import Any

from app.ai.skills_runtime.errors import OutputValidationError
from app.ai.skills_runtime.schema import collect_schema_errors


class OutputValidator:
    def validate(self, expected: list[str], outputs: dict[str, Any]) -> None:
        missing = [key for key in expected if key not in outputs]
        if missing:
            raise OutputValidationError(f"Missing required outputs: {missing}")
        empty = [key for key in expected if outputs.get(key) in (None, "", [], {})]
        if empty:
            raise OutputValidationError(f"Empty required outputs: {empty}")

    def validate_schema(self, schema: dict[str, Any], outputs: Any) -> None:
        errors = collect_schema_errors(outputs, schema)
        if not errors:
            return
        messages = [f"{'.'.join(error.path) if error.path else '<root>'}: {error.message}" for error in errors]
        raise OutputValidationError("; ".join(messages))