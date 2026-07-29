# AI Platform — Adding a New Provider

Sprint 5's success criterion: **a future developer adds a new AI provider
by implementing one interface and registering it — without modifying any
existing business logic.** This is the walkthrough.

## Example: adding a real OpenAI LLM provider

### 1. Implement the interface

Create `app/ai/llm/openai_provider.py` (a new file; do not edit
`app/ai/llm/stubs.py`, which holds placeholders only):

```python
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.llm import LLMProvider, LLMRequest, LLMResponse, TokenUsage

class OpenAIChatProvider(LLMProvider):
    provider_name = "openai"

    async def initialize(self) -> None:
        await super().initialize()
        # e.g. self._client = SomeOpenAISDKClient(api_key=self._config["api_key"])

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # call the vendor SDK here — this file is the ONLY place that may
        # import it for this provider.
        ...

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"chat", "streaming"}))

    def validate(self) -> list[str]:
        return [] if self._config.get("api_key") else ["Missing 'api_key'."]
```

### 2. Register it

In `app/ai/utils/bootstrap.py`, replace the stub registration with the
real one (`replace=True` lets it override the stub):

```python
registry.register(
    _CAT.LLM, "openai",
    module_path="app.ai.llm.openai_provider:OpenAIChatProvider",
    replace=True,
)
```

### 3. Activate it via configuration

```yaml
ai:
  llm:
    provider: openai
    options:
      api_key: ${OPENAI_API_KEY}
```

or

```
ATLAS_AI__LLM__PROVIDER=openai
ATLAS_AI__LLM__OPTIONS__API_KEY=sk-...
```

### 4. Done — nothing else changes

Every caller already goes through `ProviderFactory.create_llm()`. No
router, service, or orchestrator code changes. Tests written against
`MockLLMProvider` keep passing because they resolve providers through the
same registry/factory path.

## Checklist for any new provider

- [ ] Implement the relevant interface from `app/ai/interfaces/`.
- [ ] Live entirely inside `app/ai/<category>/` — no vendor imports
      anywhere else.
- [ ] Implement `health()` and `capabilities()` honestly; use `validate()`
      to report missing configuration instead of raising during
      `__init__`.
- [ ] Register with `ProviderRegistry.register(..., module_path=...)`
      (preferred, for lazy loading) in `app/ai/utils/bootstrap.py`.
- [ ] Add it to the table in [ProviderGuide.md](ProviderGuide.md).
- [ ] Add a unit test that resolves it through the registry/factory (not
      by importing the class directly) and exercises `health()` /
      `capabilities()` / the primary action method.
