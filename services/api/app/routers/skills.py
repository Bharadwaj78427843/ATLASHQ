from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.ai.sdk.sdk import AtlasAISDK
from app.ai.skills_runtime.models import SkillExecutionRequest
from app.dependencies import get_ai_sdk


router = APIRouter(prefix="/ai/skills", tags=["AI Skills"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class SkillValidateRequest(BaseModel):
    """Request body for skill manifest validation."""

    skill_id: str | None = Field(
        default=None,
        description="ID of a registered skill to validate. Mutually exclusive with `manifest`.",
        examples=["engineering_manager"],
    )
    manifest: dict[str, Any] | None = Field(
        default=None,
        description="Raw skill manifest dict to validate against the JSON Schema. Mutually exclusive with `skill_id`.",
    )


class SkillInstallRequest(BaseModel):
    """Request body for skill installation / upsert into the registry."""

    id: str = Field(description="Unique skill identifier.", examples=["my_skill"])
    path: str = Field(
        description="Repository-relative path to the skill directory (must contain skill.yaml).",
        examples=[".ai/skills/my_skill"],
    )
    version: str | None = Field(default=None, description="Semver version string.", examples=["1.0.0"])
    status: str = Field(default="active", description="Registry status. One of: active, inactive.", examples=["active"])
    default: bool = Field(default=False, description="Whether this skill is the default for its category.")


class SkillExecutionBody(BaseModel):
    """Request body for skill execution."""

    prompt: str = Field(description="User prompt forwarded to each workflow step.", examples=["Prepare Sprint 9 execution plan"])
    workspace_id: str | None = Field(default=None, description="Workspace context for memory scoping.")
    organization_id: str | None = Field(default=None, description="Organization context.")
    user_id: str | None = Field(default=None, description="Authenticated user initiating execution.")
    project_id: str | None = Field(default=None, description="Project context.")
    repository_id: str | None = Field(default=None, description="Repository context.")
    session_id: str | None = Field(default=None, description="Session identifier for continuity.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata forwarded to model adapter.")
    policy_context: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Key-value context evaluated by the Policy Engine. "
            "Well-known keys: `p0_defects` (int), `p1_defects` (int), `coverage_percent` (float)."
        ),
        examples=[{"p0_defects": 0, "p1_defects": 0, "coverage_percent": 92.0}],
    )
    step_tools: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of `step_id → [tool_name, …]` specifying which tools each step may invoke.",
    )
    permissions: dict[str, Any] = Field(default_factory=dict, description="Permission overrides for this execution.")
    memory: dict[str, Any] = Field(default_factory=dict, description="Memory configuration for this execution.")
    model: dict[str, Any] = Field(default_factory=dict, description="Model overrides (provider, temperature, etc.).")
    trace: dict[str, Any] = Field(default_factory=dict, description="Distributed tracing context (e.g. trace-id).")
    configuration: dict[str, Any] = Field(default_factory=dict, description="Arbitrary runtime configuration.")
    environment: dict[str, Any] = Field(default_factory=dict, description="Environment variables for the execution.")
    correlation_id: str | None = Field(default=None, description="Caller-supplied correlation identifier for observability.")
    request_metadata: dict[str, Any] = Field(default_factory=dict, description="Request-level metadata (e.g. source system).")
    deadline: datetime | None = Field(default=None, description="Execution deadline in UTC ISO-8601.")
    cancelled: bool = Field(default=False, description="Pre-cancelled flag; causes execution to abort immediately.")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SkillListResponse(BaseModel):
    """Response body for GET /ai/skills."""

    skills: list[dict[str, Any]] = Field(description="All registered skills with load status and metadata.")


class SkillDetailResponse(BaseModel):
    """Response body for GET /ai/skills/{skill_id}."""

    skill: dict[str, Any] = Field(description="Loaded SkillPackage serialised to a plain dict.")
    registry_entry: dict[str, Any] = Field(description="Raw entry from registry.yaml.")


class SkillSchemaResponse(BaseModel):
    """Response body for GET /ai/skills/{skill_id}/schema."""

    package: dict[str, Any] = Field(description="JSON Schema for skill.yaml.")
    workflow: dict[str, Any] = Field(description="JSON Schema for workflow.yaml.")
    policies: dict[str, Any] = Field(description="JSON Schema for policies.yaml.")
    tools: dict[str, Any] = Field(description="JSON Schema for tools.yaml.")


class SkillValidateResponse(BaseModel):
    """Response body for POST /ai/skills/validate."""

    skill_id: str = Field(description="Validated skill identifier.")
    valid: bool = Field(description="True when validation passes without errors.")
    skill: dict[str, Any] | None = Field(default=None, description="Loaded skill package when skill_id is used.")


class SkillInstallResponse(BaseModel):
    """Response body for POST /ai/skills/install."""

    status: str = Field(description="'installed' on success.", examples=["installed"])
    registry_entry: dict[str, Any] = Field(description="Registry row as stored.")
    skill: dict[str, Any] = Field(description="Loaded and validated SkillPackage.")


class SkillUninstallResponse(BaseModel):
    """Response body for POST /ai/skills/uninstall."""

    status: str = Field(description="'uninstalled' on success.", examples=["uninstalled"])
    skill_id: str = Field(description="ID of the removed skill.")


class SkillReloadResponse(BaseModel):
    """Response body for POST /ai/skills/reload."""

    status: str = Field(description="'reloaded' on success.", examples=["reloaded"])
    skills: list[dict[str, Any]] = Field(description="Current skill list after cache clear.")


class SkillExecutionResponse(BaseModel):
    """Response body for POST /ai/skills/{skill_id}/execute."""

    execution_id: str = Field(description="Unique UUID for this execution.")
    skill_id: str = Field(description="Identifier of the skill that was executed.")
    status: str = Field(description="One of: completed, failed, blocked.", examples=["completed"])
    outputs: dict[str, Any] = Field(description="Named output values declared by the skill interfaces.")
    traces: list[dict[str, Any]] = Field(description="Per-step execution traces with timing and output.")
    policy_violations: list[str] = Field(description="Policy rules that were violated (populated when status=blocked).")
    dependency_warnings: list[str] = Field(description="Non-fatal dependency resolution warnings.")
    error: str | None = Field(default=None, description="Error message when status=failed.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

_COMMON_ERRORS: dict[int | str, dict[str, Any]] = {
    503: {"description": "AI SDK not initialized (server startup incomplete)."},
    422: {"description": "Validation error in request body."},
}


@router.get(
    "",
    response_model=SkillListResponse,
    summary="List all registered skills",
    description=(
        "Returns all entries from the skill registry (`registry.yaml`) along with their loaded "
        "`SkillPackage` state. Invalid or unloadable skills are included with `valid: false` and "
        "an `error` field — they are never silently omitted."
    ),
    responses={
        200: {"description": "Skill list returned successfully."},
        **_COMMON_ERRORS,
    },
)
async def list_skills(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.skills.list()


@router.get(
    "/{skill_id}",
    response_model=SkillDetailResponse,
    summary="Get a specific skill",
    description=(
        "Loads and returns a single `SkillPackage` by its registry identifier. "
        "Performs full manifest + artifact validation on every call (results are LRU-cached)."
    ),
    responses={
        200: {"description": "Skill loaded successfully."},
        404: {"description": "Skill not found in registry."},
        **_COMMON_ERRORS,
    },
)
async def get_skill(skill_id: str, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    try:
        return await sdk.skills.get(skill_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/{skill_id}/schema",
    response_model=SkillSchemaResponse,
    summary="Get the JSON Schema bundle for a skill",
    description=(
        "Returns the complete JSON Schema bundle that governs the skill's structure: "
        "`package`, `workflow`, `policies`, `tools` schemas, plus optional `inputs`/`outputs` "
        "contract schemas when defined in `skill.yaml`."
    ),
    responses={
        200: {"description": "Schema bundle returned successfully."},
        404: {"description": "Skill not found in registry."},
        **_COMMON_ERRORS,
    },
)
async def get_skill_schema(skill_id: str, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    try:
        return await sdk.skills.schema(skill_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/validate",
    response_model=SkillValidateResponse,
    summary="Validate a skill manifest",
    description=(
        "Validates either a raw manifest dict or an already-registered skill by ID. "
        "Checks against all JSON Schemas (package, workflow, policies, tools) and verifies "
        "artifact file existence. Returns `valid: true` or raises a `422` with details."
    ),
    responses={
        200: {"description": "Validation passed."},
        422: {"description": "Validation failed — body contains error details."},
        **_COMMON_ERRORS,
    },
)
async def validate_skill(request: SkillValidateRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    try:
        return await sdk.skills.validate(skill_id=request.skill_id, manifest=request.manifest)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post(
    "/install",
    response_model=SkillInstallResponse,
    summary="Install or update a skill in the registry",
    description=(
        "Upserts a skill entry into `registry.yaml` and immediately loads the package to validate "
        "it. If loading fails the registry entry is rolled back to its previous state (or removed "
        "if this was a new installation), ensuring the registry never contains an invalid skill."
    ),
    responses={
        200: {"description": "Skill installed and validated successfully."},
        422: {"description": "Skill package failed validation after install — registry rolled back."},
        **_COMMON_ERRORS,
    },
)
async def install_skill(request: SkillInstallRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    try:
        return await sdk.skills.install(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post(
    "/uninstall",
    response_model=SkillUninstallResponse,
    summary="Uninstall a skill from the registry",
    description=(
        "Removes the skill entry from `registry.yaml`. Does not delete skill files from disk. "
        "The skill becomes immediately unavailable for execution."
    ),
    responses={
        200: {"description": "Skill uninstalled successfully."},
        404: {"description": "Skill not found in registry."},
        422: {"description": "`skill_id` is required in the request body."},
        **_COMMON_ERRORS,
    },
)
async def uninstall_skill(request: SkillValidateRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    if not request.skill_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="skill_id is required")
    try:
        return await sdk.skills.uninstall(request.skill_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/reload",
    response_model=SkillReloadResponse,
    summary="Reload the skill registry cache",
    description=(
        "Clears the in-process LRU caches for the registry and YAML/JSON file readers, "
        "then re-discovers all skills. Use this after manually editing `registry.yaml` or "
        "skill artifact files without restarting the server."
    ),
    responses={
        200: {"description": "Cache cleared and skill list refreshed."},
        **_COMMON_ERRORS,
    },
)
async def reload_skills(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.skills.reload()


@router.post(
    "/{skill_id}/execute",
    response_model=SkillExecutionResponse,
    summary="Execute a skill",
    description=(
        "Runs a registered skill end-to-end through the Skill Runtime pipeline:\n\n"
        "1. **Registry** — looks up the skill entry\n"
        "2. **Loader** — loads and validates the SkillPackage (manifest + artifacts)\n"
        "3. **Dependency Resolver** — checks required skill dependencies\n"
        "4. **Policy Engine** — evaluates `policy_context` against `block`-severity rules\n"
        "5. **Workflow Executor** — runs each workflow step sequentially\n"
        "   - **Permission Engine** — validates `step_tools` against the skill's allowed tool list\n"
        "   - **Model Adapter** — calls the active LLM provider for each step\n"
        "   - **Memory** — appends step output and final results to the runtime memory store\n"
        "   - **Telemetry** — records spans and latency for each step\n"
        "6. **Output Validator** — validates declared outputs (or JSON Schema if provided)\n\n"
        "Returns `status: completed` on success, `blocked` on policy violations, or `failed` on errors."
    ),
    responses={
        200: {"description": "Execution result returned (check `status` field for outcome)."},
        404: {"description": "Skill not found in registry."},
        **_COMMON_ERRORS,
    },
)
async def execute_skill(skill_id: str, request: SkillExecutionBody, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    try:
        return await sdk.skills.execute(
            SkillExecutionRequest(
                skill_id=skill_id,
                prompt=request.prompt,
                workspace_id=request.workspace_id,
                organization_id=request.organization_id,
                user_id=request.user_id,
                project_id=request.project_id,
                repository_id=request.repository_id,
                session_id=request.session_id,
                metadata=request.metadata,
                policy_context=request.policy_context,
                step_tools=request.step_tools,
                permissions=request.permissions,
                memory=request.memory,
                model=request.model,
                trace=request.trace,
                configuration=request.configuration,
                environment=request.environment,
                correlation_id=request.correlation_id,
                request_metadata=request.request_metadata,
                deadline=request.deadline,
                cancelled=request.cancelled,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
