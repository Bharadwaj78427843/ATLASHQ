from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.ai.skills_runtime.errors import SkillNotFoundError, SkillValidationError
from app.ai.skills_runtime.models import PolicyRule, SkillArtifacts, SkillInterfaces, SkillPackage, ToolPermissions, WorkflowStep
from app.ai.skills_runtime.registry import SkillRegistryService
from app.ai.skills_runtime.schema import collect_schema_errors


@lru_cache(maxsize=32)
def _read_json(path: str) -> dict[str, Any]:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class SkillLoader:
    def __init__(self, registry: SkillRegistryService) -> None:
        self._registry = registry

    def _load_yaml(self, path: Path) -> Any:
        if not path.exists():
            raise SkillNotFoundError(f"Missing YAML file: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise SkillNotFoundError(f"Missing JSON schema: {path}")
        return _read_json(str(path))

    def _validate(self, instance: Any, schema: dict[str, Any], name: str) -> None:
        errors = collect_schema_errors(instance, schema)
        if not errors:
            return
        lines = [f"{name}: {_path_text(error.path)}: {error.message}" for error in errors]
        raise SkillValidationError("; ".join(lines))

    def validate_manifest(self, manifest: dict[str, Any], *, skill_id: str = "skill") -> None:
        schema_dir = self._registry.repo_root / ".ai" / "skills" / "schema"
        package_schema = self._load_json(schema_dir / "skill-package.schema.json")
        workflow_schema = self._load_json(schema_dir / "workflow.schema.json")
        policies_schema = self._load_json(schema_dir / "policies.schema.json")
        tools_schema = self._load_json(schema_dir / "tools.schema.json")

        self._validate(manifest, package_schema, f"{skill_id}/skill.yaml")

        artifacts_block = manifest.get("artifacts", {}) if isinstance(manifest, dict) else {}
        if not isinstance(artifacts_block, dict):
            raise SkillValidationError(f"{skill_id}/skill.yaml: artifacts must be an object")

        skill_dir = self._registry.repo_root / ".ai" / "skills" / skill_id
        prompt_rel = artifacts_block.get("prompt")
        workflow_rel = artifacts_block.get("workflow")
        policies_rel = artifacts_block.get("policies")
        tools_rel = artifacts_block.get("tools")
        if not all(isinstance(rel, str) and rel for rel in [prompt_rel, workflow_rel, policies_rel, tools_rel]):
            raise SkillValidationError(f"{skill_id}/skill.yaml: artifacts block is incomplete")

        workflow_data = self._load_yaml(skill_dir / workflow_rel)
        policies_data = self._load_yaml(skill_dir / policies_rel)
        tools_data = self._load_yaml(skill_dir / tools_rel)

        self._validate(workflow_data, workflow_schema, f"{skill_id}/{workflow_rel}")
        self._validate(policies_data, policies_schema, f"{skill_id}/{policies_rel}")
        self._validate(tools_data, tools_schema, f"{skill_id}/{tools_rel}")

        contracts = manifest.get("contracts", {}) if isinstance(manifest, dict) else {}
        if isinstance(contracts, dict):
            for contract_name, contract_rel in contracts.items():
                if not isinstance(contract_rel, str) or not contract_rel:
                    raise SkillValidationError(f"{skill_id}/skill.yaml: contracts.{contract_name} must be a file path")
                contract_path = skill_dir / contract_rel
                if not contract_path.exists():
                    raise SkillNotFoundError(f"Missing contract schema: {contract_path}")
                self._load_json(contract_path)

    def load(self, skill_id: str) -> SkillPackage:
        manifest_path = self._registry.skill_manifest_path(skill_id)
        skill_dir = manifest_path.parent
        manifest = self._load_yaml(manifest_path)
        if not isinstance(manifest, dict):
            raise SkillValidationError(f"{skill_id}/skill.yaml must contain a mapping")

        self.validate_manifest(manifest, skill_id=skill_id)

        artifacts_block = manifest["artifacts"]
        artifacts = SkillArtifacts(
            prompt=artifacts_block["prompt"],
            workflow=artifacts_block["workflow"],
            policies=artifacts_block["policies"],
            tools=artifacts_block["tools"],
        )

        prompt_path = skill_dir / artifacts.prompt
        workflow_data = self._load_yaml(skill_dir / artifacts.workflow)
        policies_data = self._load_yaml(skill_dir / artifacts.policies)
        tools_data = self._load_yaml(skill_dir / artifacts.tools)

        prompt = prompt_path.read_text(encoding="utf-8")
        contracts = manifest.get("contracts", {}) if isinstance(manifest, dict) else {}
        if not isinstance(contracts, dict):
            contracts = {}

        input_schema = None
        output_schema = None
        if isinstance(contracts.get("inputs"), str):
            input_schema = self._load_json(skill_dir / contracts["inputs"])
        if isinstance(contracts.get("outputs"), str):
            output_schema = self._load_json(skill_dir / contracts["outputs"])

        workflow = [
            WorkflowStep(
                id=step["id"],
                description=step["description"],
                parallelizable=bool(step.get("parallelizable", False)),
                produces=list(step.get("produces", [])),
            )
            for step in workflow_data["steps"]
        ]

        policies = [
            PolicyRule(id=rule["id"], description=rule["description"], severity=rule["severity"])
            for rule in policies_data["rules"]
        ]

        permissions_data = tools_data["permissions"]
        permissions = ToolPermissions(
            can_edit_code=bool(permissions_data["can_edit_code"]),
            can_run_tests=bool(permissions_data["can_run_tests"]),
            can_release=bool(permissions_data["can_release"]),
            can_modify_policies=bool(permissions_data["can_modify_policies"]),
        )

        interfaces_data = manifest["interfaces"]
        interfaces = SkillInterfaces(
            inputs=list(interfaces_data.get("inputs", [])),
            outputs=list(interfaces_data.get("outputs", [])),
            requires=list(interfaces_data.get("requires", [])),
            produces=list(interfaces_data.get("produces", [])),
        )

        return SkillPackage(
            id=manifest["name"],
            name=manifest["name"],
            display_name=manifest["display_name"],
            version=manifest["version"],
            description=manifest["description"],
            owners=list(manifest.get("owners", [])),
            prompt=prompt,
            workflow=workflow,
            policies=policies,
            tools=list(tools_data["tools"]),
            permissions=permissions,
            interfaces=interfaces,
            contracts={key: value for key, value in contracts.items() if isinstance(key, str) and isinstance(value, str)},
            input_schema=input_schema,
            output_schema=output_schema,
            tests=list(manifest.get("tests", [])),
            knowledge=list(manifest.get("knowledge", [])),
            handoffs=list(manifest.get("handoffs", [])),
            success_criteria=list(manifest.get("success_criteria", [])),
        )

    def schema_bundle(self, skill_id: str) -> dict[str, Any]:
        manifest_path = self._registry.skill_manifest_path(skill_id)
        skill_dir = manifest_path.parent
        manifest = self._load_yaml(manifest_path)
        contracts = manifest.get("contracts", {}) if isinstance(manifest, dict) else {}
        if not isinstance(contracts, dict):
            contracts = {}
        bundle = {
            "package": self._load_json(self._registry.repo_root / ".ai" / "skills" / "schema" / "skill-package.schema.json"),
            "workflow": self._load_json(self._registry.repo_root / ".ai" / "skills" / "schema" / "workflow.schema.json"),
            "policies": self._load_json(self._registry.repo_root / ".ai" / "skills" / "schema" / "policies.schema.json"),
            "tools": self._load_json(self._registry.repo_root / ".ai" / "skills" / "schema" / "tools.schema.json"),
        }
        if isinstance(contracts.get("inputs"), str):
            bundle["inputs"] = self._load_json(skill_dir / contracts["inputs"])
        if isinstance(contracts.get("outputs"), str):
            bundle["outputs"] = self._load_json(skill_dir / contracts["outputs"])
        return bundle


def _path_text(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "<root>"