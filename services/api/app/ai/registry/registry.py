"""
app/ai/registry/registry.py

The Provider Registry is the ONLY place in the platform where a concrete
provider implementation is chosen. Business logic (routers, services,
orchestration) resolves providers exclusively through `ProviderRegistry`
(or, for config-driven resolution, through `app.ai.factory.ProviderFactory`)
and never imports a provider class from `app/ai/<category>/` directly.

Responsibilities:
    - registration:        `register()`
    - discovery:            `discover()`
    - lazy loading:         `module_path` imported on first `resolve()`
    - capability lookup:    `capabilities()`
    - provider resolution:  `resolve()` / `get_active()`
    - health monitoring:    `health()` / `health_check_all()`
    - dependency graph:     `dependency_graph()` / `validate_dependencies()`
    - runtime switching:    `set_active()`
"""
from __future__ import annotations

import importlib
from typing import Any

from app.ai.exceptions.errors import ConfigurationError, ProviderNotFoundError
from app.ai.interfaces.base import BaseProvider, HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.registry.types import ProviderCategory, ProviderFactoryFn, ProviderRegistration


class ProviderRegistry:
    """In-process registry of AI providers, keyed by (category, name)."""

    def __init__(self) -> None:
        self._registrations: dict[tuple[ProviderCategory, str], ProviderRegistration] = {}
        self._instances: dict[tuple[ProviderCategory, str], BaseProvider] = {}
        self._active: dict[ProviderCategory, str] = {}

    # ── Registration ──────────────────────────────────────────────────────

    def register(
        self,
        category: ProviderCategory,
        name: str,
        *,
        factory: ProviderFactoryFn | None = None,
        provider_cls: type[BaseProvider] | None = None,
        module_path: str | None = None,
        depends_on: tuple[str, ...] = (),
        description: str = "",
        replace: bool = False,
    ) -> None:
        """Register a provider under `category`/`name`.

        Exactly one of `factory`, `provider_cls`, or `module_path` must be
        given. Registration never instantiates the provider (lazy loading).
        """
        key = (category, name)
        if key in self._registrations and not replace:
            raise ConfigurationError(
                f"Provider '{name}' is already registered for category '{category.value}'. "
                "Pass replace=True to override.",
                category=category.value,
                provider=name,
            )

        supplied = [x for x in (factory, provider_cls, module_path) if x is not None]
        if len(supplied) != 1:
            raise ConfigurationError(
                "register() requires exactly one of factory, provider_cls, module_path.",
                category=category.value,
                provider=name,
            )

        if provider_cls is not None:
            factory = _class_factory(provider_cls)

        self._registrations[key] = ProviderRegistration(
            category=category,
            name=name,
            factory=factory,
            module_path=module_path,
            depends_on=depends_on,
            description=description,
        )

    def unregister(self, category: ProviderCategory, name: str) -> None:
        key = (category, name)
        self._registrations.pop(key, None)
        self._instances.pop(key, None)

    # ── Discovery ─────────────────────────────────────────────────────────

    def discover(self, category: ProviderCategory | None = None) -> list[str]:
        """List registered provider names, optionally filtered by category."""
        return sorted(
            name
            for (cat, name) in self._registrations
            if category is None or cat == category
        )

    def is_registered(self, category: ProviderCategory, name: str) -> bool:
        return (category, name) in self._registrations

    # ── Resolution (lazy loading + caching) ──────────────────────────────

    async def resolve(
        self,
        category: ProviderCategory,
        name: str,
        config: dict[str, Any] | None = None,
    ) -> BaseProvider:
        """Return the (cached, initialized) provider instance for category/name.

        The first call builds the instance via its factory/module_path and
        awaits `initialize()`. Subsequent calls return the cached instance.
        """
        key = (category, name)
        if key in self._instances:
            return self._instances[key]

        registration = self._registrations.get(key)
        if registration is None:
            available = self.discover(category)
            raise ProviderNotFoundError(
                f"No provider named '{name}' registered for category '{category.value}'. "
                f"Available: {available or 'none'}.",
                category=category.value,
                provider=name,
            )

        factory = registration.factory or self._load_lazy_factory(registration)
        instance = factory(config or {})
        await instance.initialize()
        self._instances[key] = instance
        return instance

    def _load_lazy_factory(self, registration: ProviderRegistration) -> ProviderFactoryFn:
        assert registration.module_path is not None
        module_name, _, class_name = registration.module_path.partition(":")
        if not module_name or not class_name:
            raise ConfigurationError(
                f"Invalid module_path '{registration.module_path}'. Expected 'module:ClassName'.",
                category=registration.category.value,
                provider=registration.name,
            )
        module = importlib.import_module(module_name)
        provider_cls = getattr(module, class_name)
        factory = _class_factory(provider_cls)
        registration.factory = factory  # cache resolved factory for next time
        return factory

    # ── Active provider / runtime switching ─────────────────────────────

    def set_active(self, category: ProviderCategory, name: str) -> None:
        """Mark `name` as the active provider for `category` (runtime switch)."""
        if not self.is_registered(category, name):
            raise ProviderNotFoundError(
                f"Cannot activate unregistered provider '{name}' for category '{category.value}'.",
                category=category.value,
                provider=name,
            )
        self._active[category] = name

    def get_active_name(self, category: ProviderCategory) -> str | None:
        return self._active.get(category)

    async def get_active(
        self, category: ProviderCategory, config: dict[str, Any] | None = None
    ) -> BaseProvider:
        """Resolve whichever provider is currently active for `category`."""
        name = self._active.get(category)
        if name is None:
            raise ConfigurationError(
                f"No active provider configured for category '{category.value}'.",
                category=category.value,
            )
        return await self.resolve(category, name, config)

    # ── Capability lookup ─────────────────────────────────────────────────

    async def capabilities(
        self, category: ProviderCategory, name: str, config: dict[str, Any] | None = None
    ) -> ProviderCapabilities:
        provider = await self.resolve(category, name, config)
        return provider.capabilities()

    # ── Health monitoring ─────────────────────────────────────────────────

    async def health(self, category: ProviderCategory, name: str) -> HealthCheckResult:
        """Health of a single, already-resolved provider (or UNKNOWN if unresolved)."""
        instance = self._instances.get((category, name))
        if instance is None:
            return HealthCheckResult(status=HealthStatus.UNKNOWN, message="Provider not yet resolved.")
        return await instance.health()

    async def health_check_all(self) -> dict[str, HealthCheckResult]:
        """Health of every currently-resolved (instantiated) provider."""
        results: dict[str, HealthCheckResult] = {}
        for (category, name), instance in self._instances.items():
            results[f"{category.value}:{name}"] = await instance.health()
        return results

    # ── Dependency graph ──────────────────────────────────────────────────

    def dependency_graph(self) -> dict[str, list[str]]:
        """Return the declared dependency graph as {"category:name": [deps]}."""
        return {
            f"{reg.category.value}:{reg.name}": list(reg.depends_on)
            for reg in self._registrations.values()
        }

    def validate_dependencies(self) -> list[str]:
        """Return a list of problems: missing deps or dependency cycles."""
        problems: list[str] = []
        graph = self.dependency_graph()

        for node, deps in graph.items():
            for dep in deps:
                if dep not in graph:
                    problems.append(f"'{node}' depends on unregistered provider '{dep}'.")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, path: list[str]) -> None:
            if node in visited:
                return
            if node in visiting:
                cycle = " -> ".join(path + [node])
                problems.append(f"Dependency cycle detected: {cycle}")
                return
            visiting.add(node)
            for dep in graph.get(node, []):
                if dep in graph:  # skip already-reported missing deps
                    visit(dep, path + [node])
            visiting.discard(node)
            visited.add(node)

        for node in graph:
            visit(node, [])

        return problems

    # ── Teardown ──────────────────────────────────────────────────────────

    async def shutdown_all(self) -> None:
        """Shut down every currently-resolved provider and clear the cache."""
        for instance in self._instances.values():
            await instance.shutdown()
        self._instances.clear()


def _class_factory(provider_cls: type[BaseProvider]) -> ProviderFactoryFn:
    def factory(config: dict[str, Any]) -> BaseProvider:
        return provider_cls(config)

    return factory


# ── Process-wide singleton ────────────────────────────────────────────────

_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    """Return the process-wide `ProviderRegistry` singleton, creating it lazily."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the process-wide singleton. Intended for tests."""
    global _registry
    _registry = None
