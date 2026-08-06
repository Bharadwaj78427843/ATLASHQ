# Skill Runtime – Extension Guide

> **AtlasHQ Sprint 9 | How to Extend the Skill Runtime**

---

## Extension Points

The Skill Runtime is designed for extension at six points:

1. **LLM Provider** — swap or add a new model backend
2. **Memory Provider** — swap or add a storage backend
3. **Telemetry Backend** — wire a real observability system
4. **Policy Rules** — add custom release gates
5. **Output Formats** — add JSON Schema contracts
6. **Tool Registry** — add new tools for skills to use

---

## 1. Adding a New LLM Provider

**Interface:** `app/ai/interfaces/llm.py` — `LLMProvider`

```python
from app.ai.interfaces.llm import LLMProvider, LLMRequest, LLMResponse

class MyCustomLLMProvider(LLMProvider):
    provider_name = "my_llm"

    async def initialize(self) -> None:
        # Set up API client
        self._client = MyClient(api_key=os.environ["MY_LLM_API_KEY"])

    async def generate(self, request: LLMRequest) -> LLMResponse:
        response = await self._client.chat(
            messages=[{"role": m.role, "content": m.content} for m in request.messages]
        )
        return LLMResponse(content=response.text, usage=...)

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY)
```

**Register at startup** (`app/ai/utils/bootstrap.py` or `main.py`):

```python
registry.register(
    ProviderCategory.LLM,
    "my_llm",
    provider_cls=MyCustomLLMProvider,
)
```

**Activate in config** (`.env` or `ai_config.yaml`):

```yaml
llm:
  provider: my_llm
```

The `ModelAdapter` in the Skill Runtime calls `factory.create_llm()`, which resolves the
active LLM provider automatically.

---

## 2. Adding a New Memory Provider

**Interface:** `app/ai/interfaces/memory.py` — `MemoryProvider`

```python
from app.ai.interfaces.memory import MemoryProvider, MemoryKey, MemoryRecord

class RedisMemoryProvider(MemoryProvider):
    provider_name = "redis"

    async def initialize(self) -> None:
        self._redis = await aioredis.create_redis_pool(os.environ["REDIS_URL"])

    async def get(self, key: MemoryKey) -> MemoryRecord | None:
        value = await self._redis.get(f"{key.scope}:{key.identifier}")
        if value is None:
            return None
        return MemoryRecord(key=key, value=json.loads(value))

    async def put(self, record: MemoryRecord) -> None:
        await self._redis.set(
            f"{record.key.scope}:{record.key.identifier}",
            json.dumps(record.value)
        )

    async def clear(self, scope_prefix: str) -> None:
        # Pattern delete all keys matching scope_prefix
        ...
```

Register and activate the same way as an LLM provider, using `ProviderCategory.MEMORY`.

---

## 3. Wiring a Real Telemetry Backend

**File:** `app/ai/telemetry/hooks.py`

Implement `TracingHook` and/or `MetricsHook`:

```python
from app.ai.telemetry.hooks import TracingHook, MetricsHook
from opentelemetry import trace

class OTelTracingHook:
    def __init__(self):
        self._tracer = trace.get_tracer("atlas.ai")
        self._spans: dict = {}

    def start_span(self, name: str, attributes: dict | None = None):
        span = self._tracer.start_span(name, attributes=attributes)
        ctx = trace.use_span(span, end_on_exit=False)
        ctx.__enter__()
        return (span, ctx)

    def end_span(self, span_ctx, error: BaseException | None = None):
        span, ctx = span_ctx
        if error:
            span.record_exception(error)
        ctx.__exit__(None, None, None)
        span.end()
```

**Wire in `main.py`** before the lifespan yields:

```python
from app.ai.telemetry.hooks import TelemetryContext
from my_telemetry import OTelTracingHook, DatadogMetricsHook

telemetry = TelemetryContext(
    tracing=OTelTracingHook(),
    metrics=DatadogMetricsHook(),
)
# Pass to build_skill_runtime and AgentRuntime
skill_runtime = await build_skill_runtime(factory, telemetry=telemetry)
```

---

## 4. Adding Custom Policy Rules

**File:** `app/ai/skills_runtime/policy.py`

Extend `PolicyEngine.evaluate()` to handle new rule IDs:

```python
class PolicyEngine:
    def evaluate(self, rules: list[PolicyRule], context: dict) -> list[str]:
        violations = []
        # ... existing built-in checks ...

        for rule in rules:
            if rule.severity != "block":
                continue
            # Add your custom rule:
            if rule.id == "require_ci_green" and not context.get("ci_passing", True):
                violations.append(f"{rule.id}: {rule.description} (ci_passing=False)")
                continue

        return violations
```

Then declare the rule in your skill's `policies.yaml`:

```yaml
rules:
  - id: require_ci_green
    description: CI pipeline must be passing before release.
    severity: block
```

And pass the context during execution:

```json
{
  "policy_context": { "ci_passing": false }
}
```

---

## 5. Adding JSON Schema Output Contracts

Create `outputs.schema.json` in your skill directory:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["analysis_report", "confidence_score"],
  "properties": {
    "analysis_report": { "type": "string", "minLength": 100 },
    "confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
  },
  "additionalProperties": false
}
```

Register in `skill.yaml`:

```yaml
contracts:
  outputs: outputs.schema.json
```

The `OutputValidator.validate_schema()` method will be called instead of
the interface-based check, enabling strict type and structure enforcement.

---

## 6. Adding New Tools

**File:** `app/ai/tools/` — register in `build_default_tools()`

```python
from app.ai.tools.registry import ToolRegistry
from app.ai.tools.base import Tool, ToolResult

class FileWriterTool(Tool):
    name = "write_file"
    description = "Write content to a file"

    async def execute(self, path: str, content: str) -> ToolResult:
        Path(path).write_text(content)
        return ToolResult(success=True, output=f"Written: {path}")
```

Register in `build_default_tools()`:

```python
def build_default_tools(orchestrator, config):
    return [
        # ... existing tools ...
        FileWriterTool(),
    ]
```

Then declare it in your skill's `tools.yaml`:

```yaml
tools:
  - write_file
```

---

## Extension Anti-Patterns

| ❌ Don't | ✅ Do instead |
|---|---|
| Add a second `SkillRuntime` class | Extend `SkillRuntime.execute()` |
| Add a second `SkillRegistryService` | Reuse the existing service |
| Add a second `SkillLoader` | Extend `SkillLoader` methods |
| Bypass the `PolicyEngine` | Add rules to `policies.yaml` |
| Bypass `ToolPermissionEngine` | Add tools to `tools.yaml` |
| Hard-code provider selection | Use `ProviderFactory` and `ProviderRegistry` |
