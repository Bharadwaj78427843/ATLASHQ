# Skill Runtime – API Reference

> **AtlasHQ Sprint 9 | REST API Documentation**
> Base URL: `http://localhost:8000` (development) | Router prefix: `/ai/skills`
> OpenAPI spec: `GET /openapi.json`

---

## Authentication

The Skill API is an **internal platform API**. It does not require end-user authentication tokens in the current release. Authentication is enforced at the gateway/network boundary.

For endpoints requiring user identity context, pass `user_id` in the request body.

---

## Common Response Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `404` | Skill not found in registry |
| `422` | Request validation error or skill validation failure |
| `503` | AI SDK not initialized (server still starting) |

---

## Endpoints

---

### `GET /ai/skills`

List all registered skills.

**Response:** `SkillListResponse`

```json
{
  "skills": [
    {
      "valid": true,
      "registry_entry": {
        "id": "engineering_manager",
        "path": ".ai/skills/engineering_manager",
        "version": "2.1.0",
        "status": "active"
      },
      "skill": {
        "id": "engineering_manager",
        "name": "engineering_manager",
        "display_name": "Engineering Manager",
        "version": "2.1.0",
        "description": "...",
        "workflow": [...],
        "policies": [...],
        "interfaces": {...},
        "tools": ["terminal", ...]
      }
    },
    {
      "valid": false,
      "registry_entry": { "id": "broken_skill", ... },
      "skill_id": "broken_skill",
      "error": "Missing YAML file: ..."
    }
  ]
}
```

**Notes:**
- Invalid or unloadable skills are included with `valid: false` — never silently omitted.
- `active_only=False` is used internally — all registry entries are returned.

---

### `GET /ai/skills/{skill_id}`

Get a specific skill by ID.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `skill_id` | string | Registry skill identifier |

**Response:** `SkillDetailResponse`

```json
{
  "skill": { ...SkillPackage... },
  "registry_entry": { "id": "engineering_manager", ... }
}
```

**Errors:**
- `404` — Skill not found in registry or fails to load

---

### `GET /ai/skills/{skill_id}/schema`

Get the JSON Schema bundle for a skill.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `skill_id` | string | Registry skill identifier |

**Response:** `SkillSchemaResponse`

```json
{
  "package": { ...skill-package.schema.json... },
  "workflow": { ...workflow.schema.json... },
  "policies": { ...policies.schema.json... },
  "tools": { ...tools.schema.json... },
  "inputs": { ...inputs.schema.json if present... },
  "outputs": { ...outputs.schema.json if present... }
}
```

**Notes:**
- `inputs` and `outputs` keys are only present when `contracts` are defined in `skill.yaml`

---

### `POST /ai/skills/validate`

Validate a skill manifest or registered skill.

**Request Body:** `SkillValidateRequest`

```json
{
  "skill_id": "engineering_manager"
}
```

or:

```json
{
  "manifest": {
    "kind": "AtlasHQSkillPackage",
    "name": "my_skill",
    ...
  }
}
```

**Response:** `SkillValidateResponse`

```json
{
  "skill_id": "engineering_manager",
  "valid": true,
  "skill": { ...SkillPackage if skill_id was used... }
}
```

**Errors:**
- `422` — Validation failed. Response body contains error details.

---

### `POST /ai/skills/install`

Install or update a skill in the registry.

**Request Body:** `SkillInstallRequest`

```json
{
  "id": "my_skill",
  "path": ".ai/skills/my_skill",
  "version": "1.0.0",
  "status": "active",
  "default": false
}
```

**Response:** `SkillInstallResponse`

```json
{
  "status": "installed",
  "registry_entry": { "id": "my_skill", ... },
  "skill": { ...SkillPackage... }
}
```

**Notes:**
- Registry is rolled back if the package fails validation after install.
- Use `POST /ai/skills/reload` after installing to clear caches.

**Errors:**
- `422` — Skill validation failed after install; registry was rolled back.

---

### `POST /ai/skills/uninstall`

Uninstall a skill from the registry.

**Request Body:** `SkillValidateRequest` (only `skill_id` is used)

```json
{
  "skill_id": "my_skill"
}
```

**Response:** `SkillUninstallResponse`

```json
{
  "status": "uninstalled",
  "skill_id": "my_skill"
}
```

**Notes:**
- Does not delete skill files from disk.
- Skill becomes immediately unavailable for execution.

**Errors:**
- `404` — Skill not found in registry.
- `422` — `skill_id` not provided.

---

### `POST /ai/skills/reload`

Reload the skill registry cache.

**Response:** `SkillReloadResponse`

```json
{
  "status": "reloaded",
  "skills": [...SkillListResponse.skills...]
}
```

**Notes:**
- Clears in-process LRU caches for registry YAML and artifact file readers.
- Use after manually editing `registry.yaml` or skill files without restarting.

---

### `POST /ai/skills/{skill_id}/execute`

Execute a skill through the complete runtime pipeline.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `skill_id` | string | Registry skill identifier |

**Request Body:** `SkillExecutionBody`

```json
{
  "prompt": "Prepare Sprint 9 execution plan",
  "workspace_id": "ws-abc123",
  "organization_id": "org-xyz",
  "user_id": "user-001",
  "project_id": "proj-sprint9",
  "repository_id": "repo-atlashq",
  "session_id": "sess-001",
  "policy_context": {
    "p0_defects": 0,
    "p1_defects": 0,
    "coverage_percent": 92.0
  },
  "step_tools": {
    "execute": ["terminal", "read_file"]
  },
  "correlation_id": "req-12345",
  "metadata": {},
  "model": {},
  "deadline": null,
  "cancelled": false
}
```

**Request Body Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | **Yes** | User request forwarded to every step |
| `workspace_id` | string | No | Memory scoping identifier |
| `organization_id` | string | No | Organization context |
| `user_id` | string | No | Authenticated user |
| `project_id` | string | No | Project context |
| `repository_id` | string | No | Repository context |
| `session_id` | string | No | Session for continuity |
| `policy_context` | object | No | Key-value pairs for policy evaluation |
| `step_tools` | object | No | `{step_id: [tool_name, ...]}` |
| `correlation_id` | string | No | Caller tracing identifier |
| `metadata` | object | No | Forwarded to model adapter |
| `model` | object | No | Model provider overrides |
| `trace` | object | No | Distributed trace context |
| `configuration` | object | No | Runtime configuration overrides |
| `environment` | object | No | Environment variables |
| `request_metadata` | object | No | Request-level metadata |
| `deadline` | datetime (UTC) | No | Execution deadline |
| `cancelled` | boolean | No | Pre-cancel flag |

**Response:** `SkillExecutionResponse`

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "skill_id": "engineering_manager",
  "status": "completed",
  "outputs": {
    "sprint_status_assessment": "Sprint 9 is 85% complete...",
    "prioritized_execution_plan": "Priority 1: Integration tests...",
    "release_readiness_report": "All P0/P1 defects resolved..."
  },
  "traces": [
    {
      "step_id": "understand_business",
      "status": "completed",
      "started_at": "2026-08-06T10:00:00Z",
      "finished_at": "2026-08-06T10:00:02Z",
      "message": "Confirm business objective and customer impact.",
      "output": "..."
    }
  ],
  "policy_violations": [],
  "dependency_warnings": [],
  "error": null
}
```

**Response Status Values:**

| `status` | Meaning | `traces` | `outputs` | `error` |
|---|---|---|---|---|
| `completed` | All steps ran, outputs validated | Populated | Populated | null |
| `blocked` | Policy engine blocked execution | Empty | Empty | set |
| `failed` | Execution error (permission, LLM, validation) | Partial | Empty | set |

**Errors:**
- `404` — Skill not found in registry.

---

## Data Types

### SkillExecutionBody Fields — `policy_context` Keys

| Key | Type | Effect |
|---|---|---|
| `p0_defects` | int | Triggers `no_p0` rule if `> 0` |
| `p1_defects` | int | Triggers `no_p1` rule if `> 0` |
| `coverage_percent` | float | Triggers `coverage_min_80` if `< 80.0` |
| `policy_results.{rule_id}` | bool | Triggers `{rule_id}` if `false` |

### SkillStepTrace Fields

| Field | Type | Description |
|---|---|---|
| `step_id` | string | Workflow step identifier |
| `status` | string | `running` \| `completed` \| `failed` |
| `started_at` | datetime | Step start time (UTC) |
| `finished_at` | datetime \| null | Step completion time |
| `message` | string | Step description |
| `output` | string \| null | LLM output for this step |
