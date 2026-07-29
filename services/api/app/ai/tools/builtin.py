from __future__ import annotations

from pathlib import Path

from app.ai.interfaces.base import HealthCheckResult, HealthStatus
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.tools.base import BaseTool
from app.ai.tools.models import ToolCallResult, ToolContext, ToolPermission, ToolSpec


class KnowledgeSearchTool(BaseTool):
    def __init__(self, orchestrator: KnowledgeOrchestrator) -> None:
        super().__init__(
            ToolSpec(
                name="knowledge_search",
                description="Search Atlas knowledge index",
                schema={"query": "string", "top_k": "int"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )
        self._orchestrator = orchestrator

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        result = await self._orchestrator.search(
            args.get("query", ""),
            workspace_id=context.workspace_id,
            top_k=int(args.get("top_k", 5)),
        )
        return ToolCallResult(
            tool=self.spec.name,
            ok=True,
            output={
                "answer": result.answer,
                "chunks": [c.content for c in result.context_chunks],
            },
        )


class RepositorySearchTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="repository_search",
                description="Search repository files by substring",
                schema={"query": "string", "root": "string?"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        query = str(args.get("query", "")).lower()
        root = Path(args.get("root", "."))
        matches: list[str] = []
        if query:
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".lock"}:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if query in text.lower():
                    matches.append(str(path))
                if len(matches) >= 20:
                    break
        return ToolCallResult(tool=self.spec.name, ok=True, output={"matches": matches})


class FileTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="file_tool",
                description="Read a UTF-8 text file",
                schema={"path": "string", "max_chars": "int?"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        path = Path(args["path"])
        max_chars = int(args.get("max_chars", 4000))
        text = path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        return ToolCallResult(tool=self.spec.name, ok=True, output={"path": str(path), "content": text})


class GitHubTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="github_tool",
                description="Placeholder GitHub connector tool",
                schema={"action": "string", "repository": "string"},
                permissions=[ToolPermission(resource="organization", action="read")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        return ToolCallResult(tool=self.spec.name, ok=True, output={"status": "stub", "args": args})


class ProjectTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="project_tool",
                description="Project metadata operations",
                schema={"action": "string", "project_id": "string?"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        return ToolCallResult(tool=self.spec.name, ok=True, output={"status": "stub", "workspace": context.workspace_id})


class WorkspaceTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="workspace_tool",
                description="Workspace metadata operations",
                schema={"action": "string"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        return ToolCallResult(tool=self.spec.name, ok=True, output={"workspace_id": context.workspace_id})


class DeploymentTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            ToolSpec(
                name="deployment_tool",
                description="Deployment status and trigger tool",
                schema={"action": "string", "environment": "string?"},
                permissions=[ToolPermission(resource="organization", action="operate")],
            )
        )

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        return ToolCallResult(tool=self.spec.name, ok=True, output={"status": "stub", "action": args.get("action")})


class ConfigurationTool(BaseTool):
    def __init__(self, config: dict) -> None:
        super().__init__(
            ToolSpec(
                name="configuration_tool",
                description="Read active AI/runtime configuration",
                schema={"path": "string?"},
                permissions=[ToolPermission(resource="workspace", action="read")],
            )
        )
        self._config = config

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        return ToolCallResult(tool=self.spec.name, ok=True, output=self._config)


def build_default_tools(orchestrator: KnowledgeOrchestrator, config: dict) -> list[BaseTool]:
    return [
        KnowledgeSearchTool(orchestrator),
        RepositorySearchTool(),
        FileTool(),
        GitHubTool(),
        ProjectTool(),
        WorkspaceTool(),
        DeploymentTool(),
        ConfigurationTool(config),
    ]
