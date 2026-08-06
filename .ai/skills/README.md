# AtlasHQ Skills Framework (Draft v0.2)

AtlasHQ Skills are programmable AI role packages.

A Skill is a deployable unit of behavior, not just a prompt.
Each package combines:
- prompt behavior
- workflow definition
- policy rules
- tool permissions
- interface contracts
- test assertions

## Package-First Layout

Each skill lives in its own folder:

1. .ai/skills/<skill_id>/skill.yaml
2. .ai/skills/<skill_id>/prompt.md
3. .ai/skills/<skill_id>/workflow.yaml
4. .ai/skills/<skill_id>/policies.yaml
5. .ai/skills/<skill_id>/tools.yaml
6. .ai/skills/<skill_id>/tests/*.yaml

Registry:
- .ai/skills/registry.yaml: active skills and entry points.

Schemas:
- .ai/skills/schema/skill-package.schema.json
- .ai/skills/schema/workflow.schema.json
- .ai/skills/schema/policies.schema.json
- .ai/skills/schema/tools.schema.json

Compatibility artifact:
- .ai/skills/examples/engineering_manager.skill.yaml
	- Flat legacy representation retained during migration.

## Runtime Loading Contract

1. Read .ai/skills/registry.yaml.
2. Load each skill.yaml entry.
3. Validate skill manifest against skill-package schema.
4. Resolve artifact references (prompt/workflow/policies/tools).
5. Validate each artifact against its schema.
6. Enforce permissions during tool invocation.
7. Execute workflow with policy checks.
8. Emit structured outputs for handoffs.

Validation command:
- python scripts/skills/validate_skill_package.py --skill engineering_manager

## Versioning Rules

- PATCH: Clarifications with no behavior change.
- MINOR: Backward-compatible behavior additions.
- MAJOR: Breaking behavior or contract changes.

## Why This Matters

This structure makes Skills installable, testable, shareable, and composable.
It shifts AtlasHQ from fixed agents to a programmable AI engineering organization model.
