"""
app/ai — AtlasHQ AI Platform Foundation (Sprint 5).

This package is the operating system beneath every future AI capability in
AtlasHQ. It defines vendor-neutral abstractions (interfaces), a provider
registry/factory for resolving concrete implementations from configuration,
and orchestration logic that composes providers into pipelines.

Hard rule: nothing outside `app/ai/<category>/` may import a concrete
provider class directly. Business logic must resolve providers through
`app.ai.registry.get_registry()` (or the `ProviderFactory`), keyed by the
active configuration — never by a hardcoded vendor name.
"""
