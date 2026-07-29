"""
app/ai/config/loader.py

Loads AI platform configuration from (in increasing precedence):
    1. bundled `defaults.yaml`
    2. an external YAML file (path or `ATLAS_AI_CONFIG_PATH` env var)
    3. environment variables (`ATLAS_AI__<CATEGORY>__<KEY>`, double
       underscore delimited, e.g. `ATLAS_AI__LLM__PROVIDER=azure-openai`
       or `ATLAS_AI__LLM__OPTIONS__API_KEY=...`)
    4. explicit runtime `overrides` dict passed by the caller

Each layer is deep-merged over the previous one.
"""
from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Mapping

import yaml

from app.ai.config.models import AIConfig
from app.ai.exceptions.errors import ConfigurationError

_DEFAULTS_PATH = Path(__file__).parent / "defaults.yaml"
_ENV_PREFIX = "ATLAS_AI__"
_PATH_ENV_VAR = "ATLAS_AI_CONFIG_PATH"

_ENV_ALIAS_TO_CONFIG_PATH: dict[str, tuple[str, ...]] = {
    "KNOWLEDGE_PROVIDER": ("knowledge", "provider"),
    "LLM_PROVIDER": ("llm", "provider"),
    "VECTOR_PROVIDER": ("vectorstore", "provider"),
    "EMBED_PROVIDER": ("embeddings", "provider"),
    "OPENAI_API_KEY": ("llm", "options", "api_key"),
    "OPENAI_MODEL": ("llm", "options", "model"),
    "OPENAI_EMBED_MODEL": ("embeddings", "options", "model"),
    "RAGFLOW_BASE_URL": ("knowledge", "options", "base_url"),
    "RAGFLOW_API_KEY": ("knowledge", "options", "api_key"),
    "QDRANT_URL": ("vectorstore", "options", "url"),
    "QDRANT_API_KEY": ("vectorstore", "options", "api_key"),
    "DEFAULT_AGENT": ("runtime", "default_agent"),
    "ENABLE_STREAMING": ("runtime", "enable_streaming"),
    "ENABLE_MEMORY": ("runtime", "enable_memory"),
    "ENABLE_PLANNER": ("runtime", "enable_planner"),
    "MAX_PARALLEL_TASKS": ("runtime", "max_parallel_tasks"),
    "MAX_TOOL_RETRIES": ("runtime", "max_tool_retries"),
    "DEFAULT_TIMEOUT": ("runtime", "default_timeout"),
}


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge `override` into `base`, returning a new dict."""
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"Could not read AI config file '{path}': {exc}") from exc
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in AI config file '{path}': {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"AI config file '{path}' must contain a mapping at the top level.")
    return data


def _apply_env_overrides(config: dict[str, Any], environ: Mapping[str, str]) -> dict[str, Any]:
    """Apply `ATLAS_AI__...` environment variables onto the `ai:` section."""
    merged = copy.deepcopy(config)
    ai_section = merged.setdefault("ai", {})

    for env_key, value in environ.items():
        if not env_key.startswith(_ENV_PREFIX):
            continue
        parts = [p.lower() for p in env_key[len(_ENV_PREFIX):].split("__") if p]
        if not parts:
            continue
        node = ai_section
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value

    # Also support sprint-level simple aliases (without ATLAS_AI__ prefix).
    def _coerce_alias_value(raw: str):
        lowered = raw.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if raw.isdigit():
            return int(raw)
        return raw

    for env_key, path_parts in _ENV_ALIAS_TO_CONFIG_PATH.items():
        value = environ.get(env_key)
        if value is None:
            continue
        node = ai_section
        for part in path_parts[:-1]:
            node = node.setdefault(part, {})
        node[path_parts[-1]] = _coerce_alias_value(value)

    return merged


def load_ai_config(
    path: str | os.PathLike[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> AIConfig:
    """Build the effective `AIConfig`, merging defaults, file, env, and overrides.

    Args:
        path: Optional external YAML file. Falls back to `ATLAS_AI_CONFIG_PATH`
            if unset, and skipped entirely if neither is provided/exists.
        environ: Environment mapping to read overrides from (defaults to
            `os.environ`); overridable for tests.
        overrides: Highest-precedence overrides, shaped like the `ai:` block
            content, e.g. `{"llm": {"provider": "openai"}}`.
    """
    environ = environ if environ is not None else os.environ
    merged = _load_yaml_file(_DEFAULTS_PATH)

    external_path = path or environ.get(_PATH_ENV_VAR)
    if external_path:
        external = Path(external_path)
        if external.exists():
            merged = _deep_merge(merged, _load_yaml_file(external))
        elif path is not None:
            # An explicitly-requested path that doesn't exist is a hard error;
            # a missing value from the env var is silently ignored.
            raise ConfigurationError(f"AI config file not found: {external}")

    merged = _apply_env_overrides(merged, environ)

    if overrides:
        merged = _deep_merge(merged, {"ai": dict(overrides)})

    ai_section = merged.get("ai", {})
    return AIConfig(**ai_section)
