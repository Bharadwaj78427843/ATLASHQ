# Skill Runtime – Troubleshooting Guide

> **AtlasHQ Sprint 9 | Error Reference and Debugging Guide**

---

## Debugging Checklist

Before diving into specific errors, run this checklist:

1. **Is the API running?** `curl http://localhost:8000/health`
2. **Is the registry valid?** `curl http://localhost:8000/ai/skills`
3. **Is the skill loadable?** `curl http://localhost:8000/ai/skills/{skill_id}`
4. **Does validation pass?** `curl -X POST .../validate`
5. **Check API logs** — `uvicorn` outputs to stderr
6. **Reload caches** — `curl -X POST .../reload`

---

## Error Reference

### `SkillNotFoundError`

**HTTP Status:** 404

**Causes and fixes:**

| Cause | Error message | Fix |
|---|---|---|
| Skill ID not in registry | `Skill 'my_skill' not found in registry` | Add entry to `registry.yaml` or call `POST /ai/skills/install` |
| Registry file not found | `Unable to discover repository root with .ai/skills/registry.yaml` | Ensure `.ai/skills/registry.yaml` exists from the project root |
| Missing artifact file | `Missing YAML file: .ai/skills/my_skill/workflow.yaml` | Create the missing file |
| Wrong path in registry | `Skill 'my_skill' has no path in registry` | Set `path` in registry entry |

---

### `SkillValidationError`

**HTTP Status:** 422

**Causes and fixes:**

| Error message | Fix |
|---|---|
| `skill.yaml must contain a mapping` | Check YAML syntax (indentation, special characters) |
| `artifacts block is incomplete` | Ensure all four artifact fields are set: `prompt`, `workflow`, `policies`, `tools` |
| `{skill_id}/skill.yaml: kind: ...` | `kind` must be exactly `"AtlasHQSkillPackage"` |
| `name: does not match pattern` | Use only lowercase letters, digits, underscores, hyphens |
| `version: does not match pattern` | Use semver format: `1.0.0` or `1.0.0-beta` |
| `description: is too short` | Minimum 10 characters |
| `tests: is too short` | Must have at least one test file in `tests/*.yaml` |
| `interfaces: requires, produces` | All four interface fields are required even if empty `[]` |
| `{skill_id}/workflow.yaml: steps[0].description: ...` | Step description minimum 5 characters |
| `{skill_id}/policies.yaml: rules[0].severity: ...` | Severity must be `block` or `warn` |
| `contracts.{name} must be a file path` | Ensure contract value is a string file path |
| `Missing contract schema: ...` | Create the referenced JSON Schema file |

---

### `DependencyCycleError`

**HTTP Status:** 500 (surfaced as `status=failed` in execution response)

**Message:** `Dependency cycle detected: skill_a -> skill_b -> skill_a`

**Fix:** Audit `interfaces.requires` in the affected skills and break the cycle. Circular dependencies are not allowed.

---

### `DependencyVersionError`

**Message:** `dependency version mismatch: other_skill requires >=2.0.0, found 1.5.0`

**Fix:** Either:
- Update `other_skill` to version `>=2.0.0`
- Relax the constraint in `interfaces.requires`
- Mark the dependency optional with `?` suffix if appropriate

---

### `PolicyBlockedError` / `status=blocked`

**Cause:** One or more `block`-severity policy rules were violated.

**Debug steps:**
1. Check `policy_violations` in the response for which rules triggered
2. Check your `policy_context` in the execution request
3. Review `policies.yaml` to understand the rule conditions

**Common violations:**

| Violation | Context key to fix |
|---|---|
| `no_p0: P0 defects block release` | Set `p0_defects: 0` |
| `no_p1: P1 defects block release` | Set `p1_defects: 0` |
| `coverage_min_80: ...` | Set `coverage_percent: 85.0` (≥ 80) |

---

### `ToolPermissionDeniedError` / `status=failed`

**Message:** `Skill 'my_skill' cannot use tool 'super_admin_shell' in step 'execute'. Allowed: ['read_file', 'terminal']`

**Fix:**
- Remove the unauthorized tool from `step_tools` in the request
- Or add the tool to `tools.yaml` if it should be allowed

---

### `OutputValidationError` / `status=failed`

**Message:** `Missing required outputs: ['analysis_report']`  
or: `Empty required outputs: ['sprint_status_assessment']`

**Causes:**
- Workflow Executor could not map step outputs to declared interface outputs
- All steps returned empty strings (LLM issue)
- Output name mismatch between `interfaces.outputs` and mapping logic

**Fixes:**
- Check that `interfaces.outputs` names contain keywords: `status`, `plan`, `release`
- Or add an `outputs.schema.json` contract for precise mapping
- Check LLM provider is configured and returning output (`curl .../health`)
- Add test assertions to your skill's test YAML files

---

### `503 Service Unavailable` — "AI SDK not initialized"

**Cause:** The FastAPI lifespan has not completed startup. This happens if:
- The app is still initialising
- The lifespan threw an exception during startup
- A dependency provider failed to initialise

**Debug:**
- Check startup logs for exceptions in the lifespan function (`main.py`)
- Ensure all required environment variables are set (AI config)
- Try `GET /health` — if it returns 200 the basic API is up

---

## Performance Issues

### Slow Skill Loading

**Cause:** JSON Schema files are LRU-cached but registry YAML is re-read on each request after cache invalidation.

**Fix:** Don't call `POST /ai/skills/reload` in hot paths. The cache is automatically populated after the first load.

### Slow Execution

**Cause:** LLM API latency is proportional to prompt length × number of steps.

**Optimise:**
- Reduce `prompt.md` size
- Reduce the number of workflow steps
- Use a faster LLM provider (`model` override in request body)
- Consider marking independent steps `parallelizable: true` for future parallel execution support

---

## Registry Issues

### Skill shows `valid: false` in list

```json
{
  "valid": false,
  "registry_entry": { "id": "my_skill", ... },
  "error": "Missing YAML file: .ai/skills/my_skill/workflow.yaml"
}
```

**Fix:** Repair the listed error. Then call `POST /ai/skills/reload` to re-validate.

### Registry YAML not found on startup

**Error:** `SkillNotFoundError: Unable to discover repository root with .ai/skills/registry.yaml`

**Fix:** The registry discovery walks upward from the `skills_runtime/` package directory.
Ensure `.ai/skills/registry.yaml` exists at the repository root (i.e., where `.git/` is).

---

## Testing Skills

Run unit tests:
```bash
cd services/api
uv run pytest tests/ai/ -v
```

Run integration tests:
```bash
uv run pytest tests/integration/ -v
```

Run a specific skill test:
```bash
uv run pytest tests/ai/runtime/test_skill_runtime.py -v
```

---

## Logging

The Skill Runtime logs via `atlas.ai` logger (stdlib). To increase verbosity:

```python
import logging
logging.getLogger("atlas.ai").setLevel(logging.DEBUG)
```

Or set in `logging.ini` / environment:
```
ATLAS_LOG_LEVEL=DEBUG
```

Key log events:
- `ai.skills_runtime.execute` — execution start/end with latency
- `ai.skills_runtime.step` — per-step start/end
- Memory provider operations — see `MemoryProvider` implementation logs
