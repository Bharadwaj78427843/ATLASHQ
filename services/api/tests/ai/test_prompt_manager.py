"""
tests/ai/test_prompt_manager.py

Sprint 5 — filesystem prompt provider + PromptManager: loading, rendering,
namespaces, versioning.
"""
import pytest

from app.ai.exceptions.errors import PromptError
from app.ai.prompts.manager import PromptManager
from app.ai.prompts.providers import FilesystemPromptProvider


@pytest.fixture
def provider() -> FilesystemPromptProvider:
    return FilesystemPromptProvider()  # uses the bundled app/ai/prompts/templates root


@pytest.mark.asyncio
async def test_list_prompts_default_namespace(provider: FilesystemPromptProvider):
    names = await provider.list_prompts("default")
    assert "system-greeting" in names


@pytest.mark.asyncio
async def test_get_prompt_resolves_latest_version(provider: FilesystemPromptProvider):
    template = await provider.get_prompt("system-greeting")
    assert template.version == "v1"
    assert "workspace_name" in template.variables
    assert "user_name" in template.variables


@pytest.mark.asyncio
async def test_get_prompt_unknown_raises_prompt_error(provider: FilesystemPromptProvider):
    with pytest.raises(PromptError):
        await provider.get_prompt("does-not-exist")


@pytest.mark.asyncio
async def test_prompt_manager_render(provider: FilesystemPromptProvider):
    manager = PromptManager(provider)
    rendered = await manager.render("system-greeting", user_name="Ada", workspace_name="Acme")
    assert "Ada" in rendered
    assert "Acme" in rendered
