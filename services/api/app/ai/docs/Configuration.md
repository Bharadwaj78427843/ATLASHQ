# AI Platform — Configuration

The AI platform is configured entirely through `AIConfig`
(`app/ai/config/models.py`), assembled by `load_ai_config()`
(`app/ai/config/loader.py`) from four layers, lowest to highest precedence:

1. **Bundled defaults** — `app/ai/config/defaults.yaml` (everything set to
   `mock`, so a fresh checkout runs with zero external dependencies).
2. **External YAML file** — pass a `path`, or set `ATLAS_AI_CONFIG_PATH`.
3. **Environment variables** — `ATLAS_AI__<CATEGORY>__<KEY>`.
4. **Runtime overrides** — an explicit dict passed to `load_ai_config()`,
   the highest-precedence layer (used for tests / per-request overrides).

Each layer is deep-merged over the previous one.

## Shape

```yaml
ai:
  llm:
    provider: azure-openai
    options:
      api_key: ${AZURE_OPENAI_KEY}
      endpoint: https://example.openai.azure.com
  retrieval:
    provider: ragflow
    options: {}
  embeddings:
    provider: openai
    options: {}
  vectorstore:
    provider: pgvector
    options:
      dsn: postgresql://...
  documents:
    provider: mock
    options: {}
  memory:
    provider: redis
    options:
      url: redis://localhost:6379/0
  prompts:
    provider: filesystem
    options:
      root: app/ai/prompts/templates
  agents:
    provider: mock
    options: {}
```

Every category is a `ProviderSelection`: `provider` (the registered name)
plus an arbitrary `options` dict passed straight through to the provider's
constructor as its config.

## Environment variable overrides

`ATLAS_AI__` (double underscore) delimits the path into the `ai:` tree,
case-insensitively lowercased:

```
ATLAS_AI__LLM__PROVIDER=openai
ATLAS_AI__LLM__OPTIONS__API_KEY=sk-...
ATLAS_AI__VECTORSTORE__PROVIDER=pgvector
```

## Loading

```python
from app.ai.config.loader import load_ai_config

config = load_ai_config()                              # defaults + env
config = load_ai_config("config/ai.prod.yaml")          # + external file
config = load_ai_config(overrides={"llm": {"provider": "mock"}})  # + override
```

## Wiring providers from config

```python
from app.ai.utils.bootstrap import build_default_registry, activate_from_config
from app.ai.factory.factory import ProviderFactory

registry = build_default_registry()
config = load_ai_config()
activate_from_config(registry, config)  # marks each category's configured
                                         # provider as "active" for runtime switching

factory = ProviderFactory(registry, config)
llm = await factory.create_llm()  # resolves whatever `config.llm.provider` names
```

No code path other than `ProviderFactory`/`ProviderRegistry` should ever
read `config.llm.provider` to decide which class to instantiate.
