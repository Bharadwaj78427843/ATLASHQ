"""
tests/ai/test_config.py

Sprint 5 — AI Platform configuration loader tests.
"""
import pytest

from app.ai.config.loader import load_ai_config
from app.ai.exceptions.errors import ConfigurationError


def test_defaults_are_all_mock():
    config = load_ai_config(environ={})
    assert config.knowledge.provider == "native"
    assert config.llm.provider == "mock"
    assert config.retrieval.provider == "mock"
    assert config.embeddings.provider == "mock"
    assert config.vectorstore.provider == "mock"
    assert config.memory.provider == "mock"
    assert config.prompts.provider == "filesystem"


def test_env_override_wins_over_defaults():
    config = load_ai_config(environ={"ATLAS_AI__LLM__PROVIDER": "openai"})
    assert config.llm.provider == "openai"
    # Untouched categories keep their defaults.
    assert config.retrieval.provider == "mock"


def test_env_override_sets_nested_options():
    config = load_ai_config(
        environ={
            "ATLAS_AI__LLM__PROVIDER": "azure-openai",
            "ATLAS_AI__LLM__OPTIONS__API_KEY": "secret-value",
        }
    )
    assert config.llm.provider == "azure-openai"
    assert config.llm.options["api_key"] == "secret-value"


def test_explicit_overrides_win_over_env():
    config = load_ai_config(
        environ={"ATLAS_AI__LLM__PROVIDER": "openai"},
        overrides={"llm": {"provider": "mock"}},
    )
    assert config.llm.provider == "mock"


def test_missing_explicit_path_raises_configuration_error():
    with pytest.raises(ConfigurationError):
        load_ai_config("does/not/exist.yaml", environ={})


def test_plain_env_aliases_are_supported():
    config = load_ai_config(
        environ={
            "KNOWLEDGE_PROVIDER": "ragflow",
            "LLM_PROVIDER": "openai",
            "VECTOR_PROVIDER": "qdrant",
            "EMBED_PROVIDER": "openai",
            "RAGFLOW_BASE_URL": "https://ragflow.local",
            "RAGFLOW_API_KEY": "rf-key",
        }
    )
    assert config.knowledge.provider == "ragflow"
    assert config.llm.provider == "openai"
    assert config.vectorstore.provider == "qdrant"
    assert config.embeddings.provider == "openai"
    assert config.knowledge.options["base_url"] == "https://ragflow.local"
