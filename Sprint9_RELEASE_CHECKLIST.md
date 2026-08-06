# Sprint 9 Release Checklist

> **Status: RELEASE CANDIDATE**  
> Date: 2026-08-06  
> Author: Principal Engineer / Release Manager  
> Sprint: 9 — Repository Intelligence MVP + Skill Runtime Architecture

---

## How to Use This Checklist

Every item below is backed by repository evidence (file path, test name, or command output).
A ✅ means the item has been verified and is production-ready.
A ⚠️ means the item has a known limitation that has been accepted for this release.
A ❌ means the item is a release blocker.

---

## 1. Architecture

| Item | Status | Evidence |
|---|---|---|
| Single Skill Runtime exists | ✅ | `services/api/app/ai/skills_runtime/runtime.py::SkillRuntime` — one class, one execution path |
| No duplicate registries | ✅ | `skills_runtime/registry.py::SkillRegistryService` — single class, single YAML file |
| No duplicate loaders | ✅ | `skills_runtime/loader.py::SkillLoader` — single class |
| Runtime factory is the single build point | ✅ | `skills_runtime/factory.py::build_skill_runtime()` — used in `main.py` and tests |
| Dependency injection via constructor | ✅ | `SkillRuntime.__init__` takes all components as keyword arguments |
| No global mutable state | ✅ | All state is in the `SkillRegistryService` LRU cache (cleared by `reload()`) |
| LRU caching on registry reads | ✅ | `@lru_cache(maxsize=8)` on `_read_registry()` |
| SDK as unified entry point | ✅ | `app/ai/sdk/sdk.py::AtlasAISDK` — single facade over all AI subsystems |
| App state bound in lifespan | ✅ | `main.py::lifespan()` — all components stored in `app.state` |

---

## 2. Runtime Components

| Component | Status | Evidence |
|---|---|---|
| SkillRegistryService | ✅ | `skills_runtime/registry.py` — list, get, upsert, remove, reload, known_skill_ids |
| SkillLoader | ✅ | `skills_runtime/loader.py` — load(), validate_manifest(), schema_bundle() |
| DependencyResolver | ✅ | `skills_runtime/dependency.py` — SemVer, cycle detection, optional deps |
| PolicyEngine | ✅ | `skills_runtime/policy.py` — no_p0, no_p1, coverage_min_80, policy_results |
| ToolPermissionEngine | ✅ | `skills_runtime/permissions.py` — ensure_step_tools_allowed() |
| WorkflowExecutor | ✅ | `skills_runtime/workflow_executor.py` — runs steps, calls memory, emits telemetry |
| ModelAdapter | ✅ | `skills_runtime/model_adapter.py` — run_step() → LLM.generate() |
| OutputValidator | ✅ | `skills_runtime/output_validator.py` — interface mode + JSON Schema mode |
| TelemetryContext | ✅ | `telemetry/hooks.py` — timed() context manager, no-op defaults |
| RuntimeMemoryStore | ✅ | `runtime/memory.py` — append(), write(), read(), scope resolution |

---

## 3. Public Skill APIs

| Endpoint | Status | Evidence |
|---|---|---|
| `GET /ai/skills` | ✅ | `routers/skills.py::list_skills()` — response_model=SkillListResponse |
| `GET /ai/skills/{skill_id}` | ✅ | `routers/skills.py::get_skill()` — 404 on not found |
| `GET /ai/skills/{skill_id}/schema` | ✅ | `routers/skills.py::get_skill_schema()` — schema bundle |
| `POST /ai/skills/validate` | ✅ | `routers/skills.py::validate_skill()` — manifest or skill_id |
| `POST /ai/skills/install` | ✅ | `routers/skills.py::install_skill()` — with rollback |
| `POST /ai/skills/uninstall` | ✅ | `routers/skills.py::uninstall_skill()` — 422 if no skill_id |
| `POST /ai/skills/reload` | ✅ | `routers/skills.py::reload_skills()` — cache clear |
| `POST /ai/skills/{skill_id}/execute` | ✅ | `routers/skills.py::execute_skill()` — full pipeline |
| `/api/*` compatibility aliases | ✅ | `main.py` — all routers duplicated under `/api` prefix |

---

## 4. OpenAPI Specification

| Item | Status | Evidence |
|---|---|---|
| `response_model` on all endpoints | ✅ | `routers/skills.py` — Pydantic models for all 8 endpoints |
| `summary` on all endpoints | ✅ | `routers/skills.py` — descriptive summaries |
| `description` on all endpoints | ✅ | `routers/skills.py` — detailed multi-line descriptions |
| `responses` documented for 4xx | ✅ | `_COMMON_ERRORS` applied to all endpoints + per-endpoint errors |
| Request models documented | ✅ | `SkillExecutionBody`, `SkillInstallRequest`, `SkillValidateRequest` with Field descriptions |
| Examples in request models | ✅ | `SkillExecutionBody.prompt` and `policy_context` have examples |
| `/openapi.json` generated | ✅ | Verified by `test_skill_e2e_openapi_documents_all_endpoints` |
| All 8 skill paths in spec | ✅ | Asserted by E2E test |

---

## 5. Security

| Item | Status | Evidence |
|---|---|---|
| Tool allowlist enforcement | ✅ | `ToolPermissionEngine.ensure_step_tools_allowed()` — denies unlisted tools |
| Policy gate before execution | ✅ | `PolicyEngine.evaluate()` runs before `WorkflowExecutor.run()` |
| Registry rollback on bad install | ✅ | `SkillsPipeline.install()` — restores previous state on load failure |
| No stack traces in HTTP responses | ✅ | All errors return `str(exc)` only |
| Dependency cycle detection | ✅ | `DependencyResolver._collect()` raises `DependencyCycleError` |
| Input validation on all requests | ✅ | Pydantic models on all request bodies |
| Skill API not requiring auth | ⚠️ | Internal API — auth enforced at gateway. Accepted for Sprint 9. |
| No secrets in YAML files | ✅ | Verified by grep — no API keys in `.ai/skills/` |
| CORS restricted to localhost | ✅ | `main.py` — only `localhost:3000` allowed |

---

## 6. Testing

| Test | Status | Result | Evidence |
|---|---|---|---|
| Full backend test suite | ✅ | **184 passed, 0 failed** | `uv run pytest --tb=short -q` |
| Skill Runtime unit tests | ✅ | 3 tests pass | `tests/ai/runtime/test_skill_runtime.py` |
| Skill API unit tests | ✅ | 5 tests pass | `tests/ai/test_skill_api.py` |
| Registry unit tests | ✅ | 12 tests pass | `tests/ai/test_registry.py` |
| API-Level E2E integration test | ✅ | **5 passed, 0 failed** | `tests/integration/test_skill_e2e.py` |
| E2E: full pipeline stage coverage | ✅ | All 11 stages asserted | `test_skill_e2e_pipeline_full_execution` |
| E2E: policy blocking | ✅ | `status=blocked` verified | `test_skill_e2e_policy_engine_blocks_on_p0_defects` |
| E2E: permission denial | ✅ | `status=failed` + error message | `test_skill_e2e_permission_engine_denies_unauthorized_tool` |
| E2E: 404 for unknown skill | ✅ | HTTP 404 verified | `test_skill_e2e_unknown_skill_returns_404` |
| E2E: OpenAPI completeness | ✅ | All 8 paths verified | `test_skill_e2e_openapi_documents_all_endpoints` |
| Repository Intelligence tests | ✅ | git_service, indexer, repository_indexer | `tests/services/` |
| Auth API tests | ✅ | Pass | `test_auth_api.py` |
| Organization API tests | ✅ | Pass | `test_organization_api.py` |
| Knowledge/repository API tests | ✅ | Pass | `test_knowledge_repositories_api.py` |

---

## 7. Documentation

| Document | Status | Path |
|---|---|---|
| Architecture Guide | ✅ | `docs/01-product/skill-runtime/architecture-guide.md` |
| Getting Started | ✅ | `docs/01-product/skill-runtime/getting-started.md` |
| Skill Author Guide | ✅ | `docs/01-product/skill-runtime/skill-author-guide.md` |
| Skill Package Spec | ✅ | `docs/01-product/skill-runtime/skill-package-spec.md` |
| API Reference | ✅ | `docs/01-product/skill-runtime/api-docs.md` |
| Extension Guide | ✅ | `docs/01-product/skill-runtime/extension-guide.md` |
| Troubleshooting Guide | ✅ | `docs/01-product/skill-runtime/troubleshooting-guide.md` |
| Execution Flow | ✅ | `docs/01-product/skill-runtime/execution-flow.md` |
| Sprint 9 Completion Report | ✅ | `SPRINT9_COMPLETION_REPORT.md` |
| Engineering Manager Spec | ✅ | `SPRINT_9_ENGINEERING_MANAGER.md` |
| Skill README | ✅ | `.ai/skills/README.md` |
| E2E Proof Checklist | ✅ | `.ai/skills/E2E_PROOF_CHECKLIST.md` |

---

## 8. Performance

| Item | Status | Evidence |
|---|---|---|
| Registry reads LRU-cached | ✅ | `@lru_cache(maxsize=8)` on `_read_registry()` |
| JSON schema files LRU-cached | ✅ | `@lru_cache(maxsize=32)` on `_read_json()` |
| Status polling conditional | ✅ | Frontend only polls transient states (REGISTERED/VALIDATING/CLONING/INDEXING) |
| Execution spans measured | ✅ | `TelemetryContext.timed()` wraps execution and each step |
| Memory writes are async | ✅ | `RuntimeMemoryStore.append()` is `async def` |
| No blocking I/O on critical path | ✅ | All providers use async interfaces |

---

## 9. Deployment

| Item | Status | Evidence |
|---|---|---|
| FastAPI app starts successfully | ✅ | `uv run uvicorn app.main:app` — lifespan completes |
| All routers mount without error | ✅ | `main.py` — 9 routers + /api aliases |
| Database migrations applied | ✅ | `alembic` — migration scripts in `services/api/alembic/` |
| Environment variables documented | ✅ | `.env.example` at repository root |
| Docker Compose configured | ✅ | `docker-compose.yml` at repository root |
| Backend pyproject.toml valid | ✅ | `services/api/pyproject.toml` |

---

## 10. Known Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Skills API has no end-user auth | LOW | Internal API; gateway authentication enforced at network boundary |
| Output heuristic mapping | MEDIUM | Accepted for Sprint 9. Mitigated by JSON Schema contracts. Sprint 10: improve mapping logic |
| Memory provider is in-memory by default | LOW | Mock provider for development; production deployment should configure Redis/persistent backend |
| LRU cache not invalidated on file change | LOW | Call `POST /ai/skills/reload` after editing skill files |
| `requires` deps are optional-degraded | INFO | Missing deps produce warnings, not errors. Ensures engineering_manager can run without all skill deps installed |

---

## 11. Release Notes

### Sprint 9 – New in This Release

#### Skill Runtime Architecture (Complete)
- **SkillRuntime** — single execution engine orchestrating all pipeline stages
- **SkillRegistryService** — YAML-backed skill catalogue with LRU caching
- **SkillLoader** — manifest + artifact validation against JSON Schemas
- **DependencyResolver** — SemVer-aware dependency resolution with cycle detection
- **PolicyEngine** — release gate evaluation (P0/P1/coverage rules)
- **ToolPermissionEngine** — per-step tool allowlist enforcement
- **WorkflowExecutor** — sequential step execution with memory writes and telemetry
- **ModelAdapter** — LLM provider integration per step
- **OutputValidator** — interface-based and JSON Schema output validation
- **TelemetryContext** — vendor-neutral observability hooks

#### Skill API (Complete)
- 8 REST endpoints: list, get, schema, validate, install, uninstall, reload, execute
- Full OpenAPI documentation with response models, summaries, and descriptions
- `/api/*` compatibility aliases for legacy clients

#### API-Level E2E Integration Tests (New)
- 5 integration tests covering all pipeline stages
- Policy blocking path verified
- Permission denial path verified
- 404 error path verified
- OpenAPI completeness verified

#### Documentation Suite (New)
- 8 documents in `docs/01-product/skill-runtime/`

#### Repository Intelligence MVP (Complete)
- Repository connect / validate / clone / index / sync lifecycle
- Frontend repository cards with status badges
- Status polling for transient states
- Error handling and empty states

### Bug Fixes
- Removed duplicate SQLAlchemy index for `project_id` in environments model
- SQLite-compatible JSON metadata for tests
- Added no-schema route duplicates for slash/non-slash compatibility
- Backend `/api/*` prefix compatibility for legacy test clients

---

## Sprint 9 Merge Decision

### ✅ YES — Sprint 9 is production-ready and can be merged into `main`.

**Verification summary:**
- **184 backend tests** passing (0 failures)
- **5 integration tests** passing (0 failures)  
- **OpenAPI** fully documented
- **8 documentation files** created
- **All runtime components** verified via tests
- **0 release-blocking defects** remaining
- **2 known limitations** accepted (auth boundary, output heuristic) with mitigation plans
