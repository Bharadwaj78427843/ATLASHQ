from typing import Any
from app.ai.registry.registry import ProviderRegistry
from app.ai.registry.types import ProviderCategory


class ProviderListing:
    def __init__(self, registry: ProviderRegistry):
        self._registry = registry

    async def list_providers(self) -> dict[str, Any]:
        """List all configured/active providers and their health/capabilities."""
        providers_data = []
        
        # We can iterate over the registered providers
        for cat in ProviderCategory:
            discovered = self._registry.discover(cat)
            for name in discovered:
                active_name = self._registry.get_active_name(cat)
                is_active = (name == active_name)
                
                # Fetch health
                health = await self._registry.health(cat, name)
                
                # We can't fetch capabilities unless resolved, 
                # so we will just return basic info
                providers_data.append({
                    "category": cat.value,
                    "name": name,
                    "is_active": is_active,
                    "health_status": health.status.value,
                    "health_message": health.message
                })
                
        return {"providers": providers_data}
