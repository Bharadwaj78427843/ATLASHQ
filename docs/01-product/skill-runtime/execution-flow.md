# Skill Runtime – Execution Flow

> **AtlasHQ Sprint 9 | Step-by-Step Execution Walkthrough**

This document traces a single `POST /ai/skills/engineering_manager/execute` request from
HTTP receipt to HTTP response, naming the exact file and function responsible at each stage.

---

## Full Execution Sequence

```
POST /ai/skills/engineering_manager/execute
{
  "prompt": "Prepare Sprint 9 execution plan",
  "policy_context": { "p0_defects": 0 }
}
```

---

### Stage 1 – HTTP Routing

**File:** `services/api/app/routers/skills.py`  
**Function:** `execute_skill(skill_id, request, sdk)`

FastAPI deserialises the request body into `SkillExecutionBody`, validates field types,
then calls `get_ai_sdk(request)` from `dependencies.py` to retrieve the `AtlasAISDK`
instance from `app.state.ai_sdk`.

```
routers/skills.py::execute_skill()
  └─ dependencies.py::get_ai_sdk()  → AtlasAISDK from app.state
```

---

### Stage 2 – SDK Dispatch

**File:** `services/api/app/ai/sdk/skills.py`  
**Class:** `SkillsPipeline`  
**Function:** `execute(request: SkillExecutionRequest)`

The SDK wraps the HTTP request body into a `SkillExecutionRequest` dataclass
and forwards it to the runtime.

```
sdk/skills.py::SkillsPipeline.execute(request)
  └─ skills_runtime/runtime.py::SkillRuntime.execute(request)
```

---

### Stage 3 – Registry Lookup

**File:** `services/api/app/ai/skills_runtime/registry.py`  
**Class:** `SkillRegistryService`  
**Functions:** `get(skill_id)`, `skill_manifest_path(skill_id)`, `known_skill_ids()`

The runtime calls:
1. `loader.load(skill_id)` — which calls `registry.skill_manifest_path(skill_id)` to resolve the YAML path
2. `registry.known_skill_ids()` — to provide the set of known skill IDs to the dependency resolver

```
registry.py::SkillRegistryService.skill_manifest_path("engineering_manager")
  └─ reads .ai/skills/registry.yaml (LRU cached)
  └─ returns Path(".ai/skills/engineering_manager/skill.yaml")
```

---

### Stage 4 – Skill Loading & Manifest Validation

**File:** `services/api/app/ai/skills_runtime/loader.py`  
**Class:** `SkillLoader`  
**Functions:** `load(skill_id)`, `validate_manifest(manifest)`

The loader:
1. Reads `skill.yaml` from disk
2. Loads the four JSON Schemas from `.ai/skills/schema/`
3. Validates `skill.yaml` → `skill-package.schema.json`
4. Loads and validates `workflow.yaml`, `policies.yaml`, `tools.yaml`
5. Optionally loads `inputs.schema.json` / `outputs.schema.json`
6. Constructs and returns the frozen `SkillPackage` dataclass

```
loader.py::SkillLoader.load("engineering_manager")
  ├─ _load_yaml(".ai/skills/engineering_manager/skill.yaml")
  ├─ validate_manifest(manifest)
  │    ├─ _validate(manifest, skill-package.schema.json)
  │    ├─ _validate(workflow_data, workflow.schema.json)
  │    ├─ _validate(policies_data, policies.schema.json)
  │    └─ _validate(tools_data, tools.schema.json)
  └─ returns SkillPackage(id="engineering_manager", ...)
```

---

### Stage 5 – Dependency Resolution

**File:** `services/api/app/ai/skills_runtime/dependency.py`  
**Class:** `DependencyResolver`  
**Function:** `resolve(skill, known_skill_ids)`

Iterates over `skill.interfaces.requires` and for each dependency:
- Checks it exists in `known_skill_ids`
- If it has a version constraint, loads the dependency and validates the semver
- Recursively resolves transitive dependencies
- Detects cycles via a DFS `stack`

```
dependency.py::DependencyResolver.resolve(skill, {"engineering_manager", ...})
  └─ DependencyResolver._collect(skill, known_ids, stack=["engineering_manager"], seen=set())
       ├─ "repository_analysis" not in known_ids → warning: "missing dependency: repository_analysis"
       └─ returns ["missing dependency: repository_analysis", "missing dependency: architecture_review"]
```

Result stored as `dependency_warnings` in the final response (non-fatal).

---

### Stage 6 – Policy Evaluation

**File:** `services/api/app/ai/skills_runtime/policy.py`  
**Class:** `PolicyEngine`  
**Function:** `evaluate(rules, context)`

Checks `block`-severity rules against `policy_context`:

```
policy.py::PolicyEngine.evaluate(
    rules=[PolicyRule("no_p0", ..., "block"), ...],
    context={"p0_defects": 0}
)
  ├─ no_p0: p0_defects=0 → no violation
  ├─ no_p1: p1_defects not set → no violation
  └─ returns []  (no violations)
```

If violations were returned here, `SkillRuntime` would return immediately with `status=blocked`.

---

### Stage 7 – Workflow Execution

**File:** `services/api/app/ai/skills_runtime/workflow_executor.py`  
**Class:** `WorkflowExecutor`  
**Function:** `run(skill, execution_id, request)`

Builds an `ExecutionContext`, then for each step in `skill.workflow`:

```
workflow_executor.py::WorkflowExecutor.run(skill, "550e8400-...", request)
  ├─ ExecutionContext(execution_id="550e8400-...", workspace_id="ws-abc", ...)
  │
  └─ for step in [understand_business, define_success, sprint_discovery, ...]:
       │
       ├─ Stage 7a: Permission Check
       │    permissions.py::ToolPermissionEngine.ensure_step_tools_allowed(skill, step.id, tools)
       │    → confirms tools in request.step_tools[step.id] ⊆ skill.tools
       │
       ├─ Stage 7b: Telemetry Span Start
       │    telemetry/hooks.py::TelemetryContext.timed("ai.skills_runtime.step", {skill, step})
       │
       ├─ Stage 7c: Model Invocation
       │    model_adapter.py::ModelAdapter.run_step(skill, step, prompt, metadata)
       │      └─ factory.create_llm() → LLMProvider.generate(LLMRequest)
       │         returns: "Step output text..."
       │
       ├─ Stage 7d: Memory Write (step)
       │    runtime/memory.py::RuntimeMemoryStore.append(context, "skill_steps", {...})
       │      └─ MemoryProvider.put(MemoryRecord(key=..., value=[...]))
       │
       └─ Stage 7e: Telemetry Span End
            telemetry records latency
```

After all steps:
```
  └─ Stage 7f: Memory Write (results)
       RuntimeMemoryStore.append(context, "skill_results", {skill, outputs})
```

---

### Stage 8 – Output Assembly

**File:** `services/api/app/ai/skills_runtime/workflow_executor.py`  
**Function:** `_build_declared_outputs(skill, step_outputs)`

Maps step outputs to declared interface output names using heuristic matching:

```
_build_declared_outputs(skill, step_outputs={
    "understand_business": "...",
    "sprint_discovery": "Sprint 9 is 85% complete...",
    "prioritize": "Priority 1: Integration tests...",
    "release_gate": "All P0/P1 defects resolved...",
    ...
})
  └─ "sprint_status_assessment" contains "status" → maps to sprint_discovery output
  └─ "prioritized_execution_plan" contains "plan" → maps to prioritize output
  └─ "release_readiness_report" contains "release" → maps to release_gate output
```

---

### Stage 9 – Output Validation

**File:** `services/api/app/ai/skills_runtime/output_validator.py`  
**Class:** `OutputValidator`  
**Function:** `validate(expected, outputs)` or `validate_schema(schema, outputs)`

```
output_validator.py::OutputValidator.validate(
    expected=["sprint_status_assessment", "prioritized_execution_plan", "release_readiness_report"],
    outputs={"sprint_status_assessment": "...", ...}
)
  ├─ all declared outputs present? → yes
  └─ all non-empty? → yes → validation passes
```

If `skill.output_schema` is set, `validate_schema()` is called instead for strict JSON Schema validation.

---

### Stage 10 – Telemetry (Outer Span)

**File:** `services/api/app/ai/telemetry/hooks.py`  
**Class:** `TelemetryContext`

The outer `telemetry.timed("ai.skills_runtime.execute")` span wraps the entire
Workflow Executor call, recording total execution latency via `MetricsHook.record_latency()`.

---

### Stage 11 – HTTP Response

**File:** `services/api/app/routers/skills.py`  
**Function:** `execute_skill()`

The `SkillExecutionResult` dataclass is serialised to JSON via `sdk/skills.py::_jsonify()`,
which recursively converts dataclasses, enums, and nested structures to plain dicts.

FastAPI validates the response against `SkillExecutionResponse` Pydantic model
and returns HTTP 200.

```
SkillExecutionResult → _jsonify() → dict → FastAPI serialisation → HTTP 200 JSON
```

---

## Execution Decision Tree

```
execute(request)
    │
    ├─[skill not found]────────────────→ HTTP 404
    │
    ├─[manifest invalid]───────────────→ HTTP 404 (SkillNotFoundError / SkillValidationError)
    │
    ├─[policy_violations present]──────→ HTTP 200, status=blocked
    │
    └─[execute workflow]
           │
           ├─[tool permission denied]──→ HTTP 200, status=failed, error="cannot use tool..."
           │
           ├─[LLM error]──────────────→ HTTP 200, status=failed, error="..."
           │
           ├─[output validation fails]→ HTTP 200, status=failed, error="Missing required outputs..."
           │
           └─[success]────────────────→ HTTP 200, status=completed
```

---

## Memory Key Schema

Memory is written under two keys per execution:

| Key | Scope | Contents |
|---|---|---|
| `skill_steps` | `{scope}:{identifier}` | `[{skill, step, output}, ...]` — one per step |
| `skill_results` | `{scope}:{identifier}` | `{skill, outputs}` — final output map |

Scope is resolved from `ExecutionContext` in priority order:
`memory_identifier → organization_id → project_id → session_id → workspace_id → execution_id`
