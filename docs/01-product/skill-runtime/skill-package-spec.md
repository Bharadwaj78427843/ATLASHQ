# Skill Package Specification

> **AtlasHQ Sprint 9 | Complete File Format Reference**
> Schemas: `.ai/skills/schema/`

---

## Overview

A Skill Package is a directory containing five required files and optional contract schemas.
All files are validated against JSON Schemas at load time.

---

## 1. `skill.yaml` — Main Manifest

**Schema:** `.ai/skills/schema/skill-package.schema.json`

### Required Fields

| Field | Type | Constraints | Description |
|---|---|---|---|
| `kind` | string | Must be `"AtlasHQSkillPackage"` | Document type identifier |
| `name` | string | `^[a-z0-9_\-]+$` | Registry identifier (lowercase, no spaces) |
| `display_name` | string | 3–120 chars | Human-readable name |
| `version` | string | Semver: `X.Y.Z[-prerelease]` | Package version |
| `description` | string | 10–2000 chars | What the skill does |
| `artifacts` | object | See below | Required artifact file paths |
| `interfaces` | object | See below | Input/output declarations |
| `tests` | array | `tests/*.yaml`, min 1 | Test case files |

### `artifacts` Object

All four subfields are required. Paths are relative to the skill directory.

| Field | Pattern | Description |
|---|---|---|
| `prompt` | `*.md` | System prompt for the LLM |
| `workflow` | `*.yaml` or `*.yml` | Workflow step definitions |
| `policies` | `*.yaml` or `*.yml` | Policy rules |
| `tools` | `*.yaml` or `*.yml` | Tool allowlist and permissions |

### `interfaces` Object

All four subfields are required.

| Field | Type | Description |
|---|---|---|
| `inputs` | `string[]` (min 1) | Named inputs the caller provides |
| `outputs` | `string[]` (min 1) | Named outputs this skill declares |
| `requires` | `string[]` (min 1) | Skill IDs this skill depends on |
| `produces` | `string[]` (min 1) | Artifact names this skill contributes |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `owners` | `string[]` | Team/person identifiers |
| `knowledge` | `string[]` | Paths to knowledge sources |
| `handoffs` | `object[]` | Downstream skill handoff configuration |
| `success_criteria` | `string[]` | Human-readable completion conditions |
| `contracts` | `object` | Map of contract name → schema file path |

### `handoffs` Array Item

```yaml
handoffs:
  - to_skill: backend_engineer     # target skill ID
    when: implementation required  # trigger condition (string)
    payload:
      - prioritized_execution_plan # output names forwarded
```

### `contracts` Object (optional)

Declares JSON Schema files for strict input/output validation.

```yaml
contracts:
  inputs: inputs.schema.json
  outputs: outputs.schema.json
```

---

## 2. `workflow.yaml` — Execution Steps

**Schema:** `.ai/skills/schema/workflow.schema.json`

```yaml
steps:
  - id: step_identifier         # Required: unique within workflow
    description: "Step description for the LLM context."  # Required: min 5 chars
    parallelizable: false        # Optional: default false
    produces:                    # Optional: named artifacts this step produces
      - artifact_name
```

### Step Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique step identifier |
| `description` | string (min 5) | Yes | Step purpose, included in LLM prompt |
| `parallelizable` | boolean | No (default: false) | Execution hint (informational) |
| `produces` | `string[]` | No | Artifact names produced |

---

## 3. `policies.yaml` — Release Gates

**Schema:** `.ai/skills/schema/policies.schema.json`

```yaml
rules:
  - id: no_p0               # Required: rule identifier
    description: "P0 defects block release."  # Required: min 3 chars
    severity: block          # Required: 'block' | 'warn'
```

### Rule Fields

| Field | Type | Required | Values | Description |
|---|---|---|---|---|
| `id` | string | Yes | — | Unique rule identifier |
| `description` | string (min 3) | Yes | — | Human-readable explanation |
| `severity` | string | Yes | `block`, `warn` | `block` stops execution; `warn` is logged only |

### Built-in Rule Evaluation

The `PolicyEngine` has built-in logic for these rule IDs:

| Rule ID | `policy_context` key | Block condition |
|---|---|---|
| `no_p0` | `p0_defects` | `int(value) > 0` |
| `no_p1` | `p1_defects` | `int(value) > 0` |
| `coverage_min_80` | `coverage_percent` | `float(value) < 80.0` |

For any other rule ID, provide `policy_results.{rule_id}: false` in the context to trigger a violation.

---

## 4. `tools.yaml` — Tool Allowlist

**Schema:** `.ai/skills/schema/tools.schema.json`

```yaml
tools:
  - terminal
  - read_file
  - write_file

permissions:
  can_edit_code: true      # May modify source files
  can_run_tests: true      # May run test commands
  can_release: false       # May trigger release processes
  can_modify_policies: false  # May alter policy definitions
```

### `tools` Array

List of tool names from the platform's `ToolRegistry`. Any tool name not in this list
will cause a `ToolPermissionDeniedError` if requested via `step_tools` in the execution request.

### `permissions` Object

| Field | Type | Default | Description |
|---|---|---|---|
| `can_edit_code` | boolean | true | Allow source file modifications |
| `can_run_tests` | boolean | true | Allow running test suites |
| `can_release` | boolean | false | Allow triggering releases |
| `can_modify_policies` | boolean | false | Allow altering policy files |

---

## 5. `registry.yaml` — Skill Registry

**Location:** `.ai/skills/registry.yaml`

```yaml
skills:
  - id: my_skill              # Unique registry identifier (must match skill.yaml name)
    path: .ai/skills/my_skill # Repository-relative path to skill directory
    version: 1.0.0            # Semver version string
    status: active            # 'active' | 'inactive'
    default: false            # Whether this is the default skill for its category
```

### Registry Entry Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Must match `name` in `skill.yaml` |
| `path` | string | Yes | Relative path from repository root |
| `version` | string | No | Semver; informational only |
| `status` | string | No (default: active) | `active` entries are loaded by default |
| `default` | boolean | No (default: false) | Marks the default skill |

---

## 6. Optional Contract Schemas

### `inputs.schema.json`

Validated against the `metadata` field of `SkillExecutionRequest`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sprint_objectives"],
  "properties": {
    "sprint_objectives": { "type": "string", "minLength": 10 }
  }
}
```

### `outputs.schema.json`

Validated against the `outputs` dict returned by the Workflow Executor.  
When present, this schema takes precedence over the interface-based output validation.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["analysis_report"],
  "properties": {
    "analysis_report": { "type": "string", "minLength": 50 },
    "confidence_score": { "type": "number", "minimum": 0, "maximum": 1 }
  }
}
```

---

## 7. Dependency Syntax (`interfaces.requires`)

```yaml
interfaces:
  requires:
    - other_skill              # Required; must exist in registry
    - other_skill@>=1.2.0     # Required with semver constraint
    - optional_skill?          # Optional; warning only if missing
    - optional_skill@==2.0.0?  # Optional with version constraint
```

### Supported Version Operators

| Operator | Meaning |
|---|---|
| `>=` | Greater than or equal |
| `<=` | Less than or equal |
| `>` | Strictly greater |
| `<` | Strictly less |
| `==` or `=` | Exact match |
| (none) | Exact match |

---

## 8. Validation Error Reference

| Error | Cause | Fix |
|---|---|---|
| `SkillValidationError: skill.yaml must contain a mapping` | YAML parse failure or empty file | Check YAML syntax |
| `SkillValidationError: artifacts block is incomplete` | Missing prompt/workflow/policies/tools | Add all four artifact files |
| `SkillNotFoundError: Missing YAML file: ...` | Artifact file path is wrong | Check path relative to skill dir |
| `SkillValidationError: {skill_id}/skill.yaml: name: ...` | Violates `^[a-z0-9_-]+$` pattern | Use lowercase, underscores only |
| `SkillValidationError: artifacts block is incomplete` | artifacts.prompt/workflow/policies/tools missing | Declare all four in artifacts |
| `DependencyCycleError: Dependency cycle detected` | Circular `requires` | Remove the cycle |
| `DependencyVersionError: version mismatch` | Required version not met | Update dependency or constraint |
