# Skill Author Guide

> **AtlasHQ Sprint 9 | How to Create a Skill Package**

---

## What is a Skill?

A **Skill** is a declarative AI workflow package. It specifies:
- **What steps** to execute (workflow)
- **What the AI is** (prompt)
- **What tools** it may use (tools + permissions)
- **What policies** gate execution (policies)
- **What it consumes and produces** (interfaces / contracts)

Skills are stored as directories under `.ai/skills/` and registered in `.ai/skills/registry.yaml`.

---

## Skill Package Structure

```
.ai/skills/
└── my_skill/
    ├── skill.yaml          # Main manifest (required)
    ├── prompt.md           # System prompt for the LLM (required)
    ├── workflow.yaml       # Ordered execution steps (required)
    ├── policies.yaml       # Release gates and guardrails (required)
    ├── tools.yaml          # Allowed tool names and permissions (required)
    ├── inputs.schema.json  # Input validation schema (optional)
    ├── outputs.schema.json # Output validation schema (optional)
    └── tests/              # Skill test cases (optional)
        └── basic.yaml
```

---

## Step 1 – Create the Manifest (`skill.yaml`)

```yaml
kind: AtlasHQSkillPackage
name: my_skill
display_name: My Custom Skill
version: 1.0.0
description: A short description of what this skill does.
owners:
  - your-team

artifacts:
  prompt: prompt.md
  workflow: workflow.yaml
  policies: policies.yaml
  tools: tools.yaml

# Optional: JSON Schema contracts
contracts:
  inputs: inputs.schema.json
  outputs: outputs.schema.json

interfaces:
  inputs:
    - input_data          # Named inputs the caller provides in policy_context/metadata
  outputs:
    - analysis_report     # Declared outputs; must be populated by WorkflowExecutor
  requires:
    - other_skill         # Optional: skill IDs this skill depends on
  produces:
    - report_artifact     # What this skill contributes to downstream consumers

knowledge:
  - docs/                 # Paths to reference knowledge

tests:
  - tests/basic.yaml

success_criteria:
  - Output analysis_report is complete and actionable.
```

---

## Step 2 – Write the System Prompt (`prompt.md`)

The prompt becomes the LLM system message for every step.

```markdown
You are a specialist AI assistant for AtlasHQ.

Your role is to [describe role].

Behaviour:
- Always produce structured, actionable output.
- Cite evidence from the repository when making claims.
- Do not speculate beyond available information.
```

**Guidelines:**
- Keep it focused — the prompt applies to ALL steps
- Use second-person ("You are...")
- Specify output format expectations

---

## Step 3 – Define the Workflow (`workflow.yaml`)

```yaml
steps:
  - id: analyze            # Unique step identifier
    description: Analyze the input data and identify key patterns.
    parallelizable: false  # Set true only for truly independent steps
    produces:
      - analysis_notes     # Optional: named artifacts this step produces

  - id: synthesize
    description: Synthesize findings into a structured report.
    parallelizable: false
```

**Rules:**
- Step `id` values must be unique within the workflow
- Steps execute **sequentially** in the declared order
- `parallelizable: true` is metadata only (parallel execution is not yet implemented)
- `produces` entries are informational — they do not gate output validation

---

## Step 4 – Declare Policies (`policies.yaml`)

```yaml
rules:
  - id: no_p0               # Unique rule ID
    description: P0 defects block release.
    severity: block          # 'block' stops execution; 'warn' emits a warning

  - id: coverage_min_80
    description: Test coverage must meet the 80% minimum.
    severity: block

  - id: review_required
    description: Requires peer review completion.
    severity: warn           # Non-blocking
```

**Built-in rule evaluations** (handled by `PolicyEngine`):

| Rule ID | Context key | Blocks when |
|---|---|---|
| `no_p0` | `p0_defects` (int) | `> 0` |
| `no_p1` | `p1_defects` (int) | `> 0` |
| `coverage_min_80` | `coverage_percent` (float) | `< 80.0` |
| `{any rule_id}` | `policy_results.{rule_id}` (bool) | `false` |

---

## Step 5 – Configure Tools (`tools.yaml`)

```yaml
tools:
  - terminal               # Names from the platform's ToolRegistry
  - read_file
  - write_file

permissions:
  can_edit_code: true
  can_run_tests: true
  can_release: false        # Must be explicitly enabled for release skills
  can_modify_policies: false
```

**Important:** The `tools` list is the allowlist for `ToolPermissionEngine`. Any tool not listed here will cause the execution to fail if requested via `step_tools`.

---

## Step 6 – Optional Contracts (JSON Schema)

Create `inputs.schema.json` and/or `outputs.schema.json` for strict validation.

Example `outputs.schema.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["analysis_report"],
  "properties": {
    "analysis_report": {
      "type": "string",
      "minLength": 100
    }
  }
}
```

Register in `skill.yaml` under `contracts`:
```yaml
contracts:
  outputs: outputs.schema.json
```

---

## Step 7 – Register the Skill

Add an entry to `.ai/skills/registry.yaml`:

```yaml
skills:
  - id: my_skill
    path: .ai/skills/my_skill
    version: 1.0.0
    status: active
    default: false
```

Or use the API:

```bash
curl -X POST http://localhost:8000/ai/skills/install \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_skill",
    "path": ".ai/skills/my_skill",
    "version": "1.0.0"
  }'
```

The install endpoint validates the package before committing to the registry.

---

## Step 8 – Validate Your Skill

```bash
curl -X POST http://localhost:8000/ai/skills/validate \
  -H "Content-Type: application/json" \
  -d '{ "skill_id": "my_skill" }'
```

---

## Step 9 – Test Execution

```bash
curl -X POST http://localhost:8000/ai/skills/my_skill/execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the current state",
    "workspace_id": "test-workspace",
    "policy_context": { "p0_defects": 0 }
  }'
```

---

## Output Mapping Logic

The `WorkflowExecutor._build_declared_outputs()` method maps workflow step outputs to declared interface outputs using heuristic name matching:

| Output name contains | Maps to step |
|---|---|
| `status` | `sprint_discovery` step output |
| `plan` | `prioritize` or `delegate` step output |
| `release` | `release_gate` or `manager_review` step output |
| anything else | Concatenation of all step outputs |

For precise mapping, define an `outputs.schema.json` contract.

---

## Dependency Declaration

Declare required skills in `interfaces.requires`:

```yaml
interfaces:
  requires:
    - repository_analysis        # Required: must exist in registry
    - architecture_review@>=2.0  # Required: must match semver constraint
    - qa_engineer?               # Optional: warning only if missing
```

The `DependencyResolver` checks all required skills exist in the registry, loads them
(triggering their own validation), and detects circular dependencies.
