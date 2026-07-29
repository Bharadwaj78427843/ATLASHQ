from typing import Any
from app.ai.registry.registry import ProviderRegistry
from app.ai.interfaces.base import HealthStatus


class SystemHealth:
    def __init__(self, registry: ProviderRegistry):
        self._registry = registry

    async def check(self) -> dict[str, Any]:
        """Run health checks on all resolved active providers."""
        results = await self._registry.health_check_all()
        
        overall_status = "healthy"
        for name, result in results.items():
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = "unhealthy"
                break
            elif result.status == HealthStatus.DEGRADED and overall_status == "healthy":
                overall_status = "degraded"
                
        return {
            "status": overall_status,
            "providers": {
                name: {
                    "status": res.status.value,
                    "message": res.message,
                    "details": res.details
                } for name, res in results.items()
            }
        }
