from __future__ import annotations

from app.ai.skills_runtime.models import PolicyRule


class PolicyEngine:
    def evaluate(self, rules: list[PolicyRule], context: dict) -> list[str]:
        violations: list[str] = []
        p0 = int(context.get("p0_defects", 0) or 0)
        p1 = int(context.get("p1_defects", 0) or 0)
        coverage = context.get("coverage_percent")
        explicit = context.get("policy_results", {})

        for rule in rules:
            if rule.severity != "block":
                continue
            if rule.id == "no_p0" and p0 > 0:
                violations.append(f"{rule.id}: {rule.description} (p0_defects={p0})")
                continue
            if rule.id == "no_p1" and p1 > 0:
                violations.append(f"{rule.id}: {rule.description} (p1_defects={p1})")
                continue
            if rule.id == "coverage_min_80" and coverage is not None and float(coverage) < 80.0:
                violations.append(f"{rule.id}: {rule.description} (coverage_percent={coverage})")
                continue
            if isinstance(explicit, dict) and rule.id in explicit and not bool(explicit[rule.id]):
                violations.append(f"{rule.id}: {rule.description}")

        return violations
