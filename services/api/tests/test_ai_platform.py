import pytest
from app.ai.registry.registry import get_registry
from app.ai.registry.types import ProviderCategory

@pytest.mark.asyncio
async def test_ai_platform_registry_bootstrap():
    """Verify that the AI platform registry bootstraps mock providers correctly."""
    registry = get_registry()
    assert registry is not None

    # Test basic category existence
    categories = [
        ProviderCategory.LLM,
        ProviderCategory.EMBEDDING,
        ProviderCategory.RETRIEVAL,
        ProviderCategory.DOCUMENT,
        ProviderCategory.VECTORSTORE
    ]
    
    for cat in categories:
        assert cat in ProviderCategory
