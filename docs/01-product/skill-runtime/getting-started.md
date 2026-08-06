# Skill Runtime – Getting Started

> **AtlasHQ Sprint 9 | Quick Start Guide**

This guide walks you through executing your first Skill in under 5 minutes.

---

## Prerequisites

- AtlasHQ API running locally (`uv run uvicorn app.main:app --reload` from `services/api/`)
- An HTTP client (curl, HTTPie, Postman, or the frontend)

---

## Step 1 – List Available Skills

```bash
curl http://localhost:8000/ai/skills
```

Expected response:

```json
{
  "skills": [
    {
      "valid": true,
      "registry_entry": {
        "id": "engineering_manager",
        "path": ".ai/skills/engineering_manager",
        "version": "1.0.0",
        "status": "active"
      },
      "skill": {
        "id": "engineering_manager",
        "display_name": "Engineering Manager",
        ...
      }
    }
  ]
}
```

---

## Step 2 – Inspect a Skill

```bash
curl http://localhost:8000/ai/skills/engineering_manager
```

This returns the full `SkillPackage` including all workflow steps, policies, and interface declarations.

---

## Step 3 – Execute a Skill

```bash
curl -X POST http://localhost:8000/ai/skills/engineering_manager/execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Prepare Sprint 9 execution plan",
    "workspace_id": "my-workspace",
    "policy_context": {
      "p0_defects": 0,
      "p1_defects": 0,
      "coverage_percent": 92.0
    }
  }'
```

Expected response:

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "skill_id": "engineering_manager",
  "status": "completed",
  "outputs": {
    "sprint_status_assessment": "...",
    "prioritized_execution_plan": "...",
    "release_readiness_report": "..."
  },
  "traces": [
    { "step_id": "sprint_discovery", "status": "completed", "output": "..." },
    { "step_id": "prioritize", "status": "completed", "output": "..." },
    ...
  ],
  "policy_violations": [],
  "dependency_warnings": [],
  "error": null
}
```

---

## Step 4 – Understanding the Response

| Field | Meaning |
|---|---|
| `execution_id` | Unique UUID for this run. Reference in logs and memory. |
| `status` | `completed` \| `failed` \| `blocked` |
| `outputs` | Named output values declared by the skill's interfaces |
| `traces` | Per-step records with timing and model output |
| `policy_violations` | Non-empty when `status=blocked` |
| `dependency_warnings` | Optional dependency warnings (non-fatal) |
| `error` | Error message when `status=failed` |

---

## Step 5 – Policy Context

Policy context lets you communicate environment conditions to the Policy Engine.
The `engineering_manager` skill blocks if P0 defects are present:

```bash
curl -X POST http://localhost:8000/ai/skills/engineering_manager/execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ship Sprint 9",
    "policy_context": { "p0_defects": 1 }
  }'
```

Response:

```json
{
  "status": "blocked",
  "policy_violations": ["no_p0: No P0 defects permitted for release (p0_defects=1)"],
  "traces": [],
  "outputs": {}
}
```

---

## Step 6 – Validate a Skill

Before installing a new skill, validate its manifest:

```bash
curl -X POST http://localhost:8000/ai/skills/validate \
  -H "Content-Type: application/json" \
  -d '{ "skill_id": "engineering_manager" }'
```

---

## Next Steps

- 📖 **Skill Author Guide** — `skill-author-guide.md`
- 📖 **Skill Package Spec** — `skill-package-spec.md`
- 📖 **API Reference** — `api-docs.md`
- 📖 **Troubleshooting** — `troubleshooting-guide.md`
