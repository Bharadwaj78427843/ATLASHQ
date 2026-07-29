# AI Platform — Provider Registry

`app/ai/registry/registry.py` defines `ProviderRegistry`, the only place a
concrete provider is instantiated.

## Responsibilities

| Responsibility | Method(s) |
|---|---|
| Registration | `register()`, `unregister()` |
| Discovery | `discover()`, `is_registered()` |
| Lazy loading | `module_path="module:ClassName"` imported on first `resolve()` |
| Resolution (with caching) | `resolve()` |
| Runtime switching | `set_active()`, `get_active_name()`, `get_active()` |
| Capability lookup | `capabilities()` |
| Health monitoring | `health()`, `health_check_all()` |
| Dependency graph | `dependency_graph()`, `validate_dependencies()` |
| Teardown | `shutdown_all()` |

## Registration

```python
registry.register(
    ProviderCategory.LLM,
    "azure-openai",
    module_path="app.ai.llm.stubs:AzureOpenAIProvider",
)
```

Exactly one of `factory`, `provider_cls`, or `module_path` must be given:

- `provider_cls` — an already-imported class; wrapped into a factory.
- `factory` — a callable `(config: dict) -> BaseProvider` for advanced
  construction (e.g. needing extra dependencies).
- `module_path` — `"module:ClassName"`, imported lazily. This is the
  default used by `app/ai/utils/bootstrap.py` so registering every known
  provider costs nothing until it's actually resolved.

## Resolution & caching

```python
provider = await registry.resolve(ProviderCategory.LLM, "mock", {"model": "mock-llm-v1"})
```

The first call builds the instance (via its factory) and awaits
`initialize()`. The instance is cached by `(category, name)`; subsequent
`resolve()` calls for the same key return the cached instance without
re-initializing.

## Runtime switching

```python
registry.set_active(ProviderCategory.LLM, "openai")
llm = await registry.get_active(ProviderCategory.LLM)
```

`set_active()` requires the target to already be registered. This is how
the platform supports switching providers without restarting — combined
with `AIConfig` overrides, a running process can be told "use `anthropic`
for LLM from now on."

## Health monitoring

```python
result = await registry.health(ProviderCategory.LLM, "mock")
all_results = await registry.health_check_all()  # only resolved providers
```

`health_check_all()` only reports on providers that have been resolved at
least once — an unresolved provider hasn't allocated any resources to
report on.

## Dependency graph

Providers may declare `depends_on=("other-provider-name", ...)` at
registration time (e.g. an agent that depends on a specific memory
provider). `validate_dependencies()` detects both missing dependencies and
cycles:

```python
problems = registry.validate_dependencies()
assert problems == []
```

## Singleton

`get_registry()` returns a process-wide singleton; `reset_registry()`
clears it (used by tests). Application code should generally use
`app/ai/utils/bootstrap.py::build_default_registry()` to get a fully-wired
registry rather than registering providers by hand.
