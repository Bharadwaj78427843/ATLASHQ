# Skill Runtime – Architecture Guide

> **AtlasHQ Sprint 9 | Skill Runtime Architecture**
> Document version: 1.0.0 | Implementation: `services/api/app/ai/skills_runtime/`

---

## 1. Purpose

The **Skill Runtime** is AtlasHQ's execution engine for structured AI workflows. It transforms an
opaque "ask AI a question" interaction into a traceable, policy-governed, permission-bounded
multi-step execution that produces declared, validated outputs.

Engineering Managers use Skills to delegate repeatable workflows — sprint planning, code review
orchestration, release gate evaluation — to the AI platform with full auditability.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         REST API Layer                              │
│              POST /ai/skills/{skill_id}/execute                     │
│              routers/skills.py  →  dependencies.get_ai_sdk()        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                     AtlasAISDK.skills.execute()
                     sdk/skills.py:SkillsPipeline
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SkillRuntime.execute()                         │
│                   skills_runtime/runtime.py                         │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Registry   │  │    Loader    │  │   Dependency Resolver    │  │
│  │ registry.py  │  │  loader.py   │  │    dependency.py         │  │
│  │              │→ │              │→ │                          │  │
│  │ YAML file +  │  │ YAML + JSON  │  │ SemVer + cycle detect    │  │
│  │ LRU cache    │  │ validation   │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Policy Engine                             │   │
│  │                      policy.py                              │   │
│  │  Evaluates P0/P1/coverage rules → block or continue         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  WorkflowExecutor.run()                      │   │
│  │               skills_runtime/workflow_executor.py            │   │
│  │                                                              │   │
│  │  for each step in skill.workflow:                            │   │
│  │    ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐   │   │
│  │    │ Permission Eng. │  │ ModelAdapter │  │   Memory    │   │   │
│  │    │ permissions.py  │→ │model_adapter │→ │runtime/     │   │   │
│  │    │ tool allowlist  │  │ LLM.generate │  │memory.py    │   │   │
│  │    └─────────────────┘  └──────────────┘  └─────────────┘   │   │
│  │                              ↕                               │   │
│  │                      Telemetry spans                         │   │
│  │                      telemetry/hooks.py                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   OutputValidator                            │   │
│  │                  output_validator.py                         │   │
│  │  Checks declared outputs exist + JSON Schema if provided     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 SkillRegistryService (`registry.py`)

Manages the YAML-based skill catalogue.

| Responsibility | Implementation |
|---|---|
| List all registered skills | `list(active_only=True)` |
| Look up a skill by ID | `get(skill_id)` |
| Resolve manifest path | `skill_manifest_path(skill_id)` |
| Install / update a skill | `upsert(row)` |
| Remove a skill | `remove(skill_id)` |
| Clear LRU cache | `reload()` |

**Storage:** `.ai/skills/registry.yaml`  
**Cache:** `@lru_cache(maxsize=8)` on the YAML reader; cleared by `reload()`.

### 3.2 SkillLoader (`loader.py`)

Loads a `SkillPackage` from disk, performing full schema validation.

Validation layers:
1. `skill.yaml` → `skill-package.schema.json`
2. `workflow.yaml` → `workflow.schema.json`
3. `policies.yaml` → `policies.schema.json`
4. `tools.yaml` → `tools.schema.json`
5. Optional `inputs.schema.json` / `outputs.schema.json` contracts

### 3.3 DependencyResolver (`dependency.py`)

Walks `interfaces.requires` and resolves transitive dependencies with:
- **Semver parsing** — `SemVer.parse()` with `>=`, `<=`, `>`, `<`, `==`
- **Cycle detection** — maintains a `stack` during DFS traversal
- **Optional deps** — suffix `?` on a dependency name degrades to warning

### 3.4 PolicyEngine (`policy.py`)

Evaluates `policy_context` against `block`-severity rules from `policies.yaml`.

Built-in rule IDs:
- `no_p0` — blocks if `p0_defects > 0`
- `no_p1` — blocks if `p1_defects > 0`
- `coverage_min_80` — blocks if `coverage_percent < 80`
- Any `policy_results.{rule_id} = false` — blocks

Returns a list of violation strings; non-empty list triggers `BLOCKED` status.

### 3.5 ToolPermissionEngine (`permissions.py`)

Validates `step_tools[step_id]` against `skill.tools` (loaded from `tools.yaml`).  
Raises `ToolPermissionDeniedError` for any tool not in the allowlist.

### 3.6 WorkflowExecutor (`workflow_executor.py`)

Iterates over `skill.workflow` steps sequentially:
1. Validates step tools (Permission Engine)
2. Calls `ModelAdapter.run_step()` inside a telemetry span
3. Appends step output to memory (`RuntimeMemoryStore.append`)
4. Appends final skill results to memory

### 3.7 ModelAdapter (`model_adapter.py`)

Bridges the Skill Runtime to the LLM provider layer.

For each step:
- Creates an `LLMRequest` with system prompt (skill's `prompt.md`) + user content (step context)
- Calls `ProviderFactory.create_llm()` → `LLM.generate()`
- Returns the response content string

### 3.8 OutputValidator (`output_validator.py`)

Two validation modes:
- **Interface mode** — checks every key in `interfaces.outputs` is present and non-empty
- **Schema mode** — validates outputs dict against `outputs.schema.json` using jsonschema

### 3.9 TelemetryContext (`telemetry/hooks.py`)

Vendor-neutral observability hooks. Default implementation: no-ops.

Records:
- `ai.skills_runtime.execute` — full execution span
- `ai.skills_runtime.step` — per-step span with `{skill, step}` tags

Integrate a real backend by implementing `TracingHook`, `MetricsHook`, and wiring them at startup.

### 3.10 RuntimeMemoryStore (`runtime/memory.py`)

Scoped memory facade over the configured `MemoryProvider`.

Scope resolution order: `memory_identifier` → `organization_id` → `project_id` → `session_id` → `workspace_id` → `execution_id`.

Writes two keys per execution:
- `skill_steps` — list of `{skill, step, output}` records (one per step)
- `skill_results` — `{skill, outputs}` final summary

---

## 4. Data Models

### SkillPackage (frozen dataclass)

```python
@dataclass(frozen=True)
class SkillPackage:
    id: str                          # Registry identifier
    name: str                        # Matches skill.yaml 'name'
    display_name: str
    version: str                     # Semver
    description: str
    owners: list[str]
    prompt: str                      # Contents of prompt.md
    workflow: list[WorkflowStep]     # Ordered steps
    policies: list[PolicyRule]
    tools: list[str]                 # Allowed tool names
    permissions: ToolPermissions
    interfaces: SkillInterfaces      # inputs, outputs, requires, produces
    contracts: dict[str, str]        # contract name → schema file path
    input_schema: dict | None        # Parsed inputs.schema.json
    output_schema: dict | None       # Parsed outputs.schema.json
    tests: list[str]
    knowledge: list[str]
    handoffs: list[dict]
    success_criteria: list[str]
```

### SkillExecutionResult (dataclass)

```python
@dataclass
class SkillExecutionResult:
    execution_id: str
    skill_id: str
    status: SkillExecutionStatus     # completed | failed | blocked
    outputs: dict[str, Any]
    traces: list[SkillStepTrace]
    policy_violations: list[str]
    dependency_warnings: list[str]
    error: str | None
```

---

## 5. Execution Flow Summary

```
execute(request)
  │
  ├─ load skill           → SkillLoader.load(skill_id)
  ├─ resolve deps         → DependencyResolver.resolve(skill, known_ids)
  ├─ evaluate policies    → PolicyEngine.evaluate(skill.policies, context)
  │    └─ violations?     → return BLOCKED result
  │
  └─ telemetry span start
       │
       └─ WorkflowExecutor.run(skill, execution_id, request)
              │
              for step in skill.workflow:
                ├─ check step tools  → ToolPermissionEngine
                ├─ telemetry span
                ├─ LLM call          → ModelAdapter.run_step()
                └─ memory write      → RuntimeMemoryStore.append()
              │
              memory write (final results)
              │
       └─ telemetry span end
       │
       ├─ output validation → OutputValidator.validate() or validate_schema()
       └─ return COMPLETED result
```

---

## 6. Security Boundaries

| Boundary | Enforcement |
|---|---|
| Tool allowlist | `ToolPermissionEngine` — denies any tool not in `tools.yaml` |
| Policy gates | `PolicyEngine` — blocks execution before any LLM call |
| Registry rollback | `SkillsPipeline.install()` — rolls back invalid installs atomically |
| Dependency isolation | `DependencyResolver` — prevents unknown or cyclic skill dependencies |
| Error leakage | All errors returned as `error` string; no stack traces in HTTP responses |

---

## 7. Extension Points

| Extension | How |
|---|---|
| Add a new LLM provider | Implement `LLMProvider` interface, register via `ProviderRegistry` |
| Add a new memory backend | Implement `MemoryProvider` interface |
| Add a real telemetry backend | Implement `TracingHook` + `MetricsHook`, wire in `main.py` |
| Add a new policy rule | Add rule to `policies.yaml`, implement check in `PolicyEngine.evaluate()` |
| Add a new output format | Extend `OutputValidator` or add a JSON Schema contract |

See `extension-guide.md` for detailed instructions.
