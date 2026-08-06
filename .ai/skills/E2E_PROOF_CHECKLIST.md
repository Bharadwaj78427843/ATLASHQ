# Engineering Manager Skill E2E Proof Checklist

Use this checklist before adding more role skill packages.

## Required Proof

1. Validate
- Run schema validation for manifest and artifacts.
- Command:
  - python scripts/skills/validate_skill_package.py --skill engineering_manager

2. Load
- Confirm orchestrator can load .ai/skills/engineering_manager/skill.yaml.
- Confirm artifact references resolve to existing files.

3. Execute
- Run one end-to-end execution with the Engineering Manager workflow.
- Confirm sequence includes sprint_discovery and release_gate.

4. Enforce Permissions
- Attempt one disallowed tool call and verify runtime blocks it.

5. Structured Outputs
- Confirm runtime emits the declared output contracts:
  - sprint_status_assessment
  - prioritized_execution_plan
  - release_readiness_report

If any item fails, do not add additional role skill packages yet.
