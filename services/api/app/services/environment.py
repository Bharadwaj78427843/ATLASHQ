"""
app/services/environment.py

Service layer for Environments, enforcing organizational RBAC.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.environment import Environment
from app.models.organization_member import MemberRole, MemberStatus
from app.repositories.environment import EnvironmentRepository
from app.repositories.project import ProjectRepository
from app.repositories.workspace import WorkspaceRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate, EnvironmentList

class EnvironmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = EnvironmentRepository(session)
        self._project_repo = ProjectRepository(session)
        self._ws_repo = WorkspaceRepository(session)
        self._member_repo = OrganizationMemberRepository(session)

    async def _require_project_and_role(
        self, user: User, workspace_id: UUID, project_id: UUID, allowed_roles: set[MemberRole]
    ):
        """Verifies project belongs to workspace, workspace exists, and user has allowed role."""
        project = await self._project_repo.get_by_id(project_id)
        if not project or project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
            
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
            
        member = await self._member_repo.get_by_org_and_user(workspace.organization_id, user.id)
        if not member or member.status != MemberStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not an active member of this organization",
            )
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation",
            )
        return project, member

    async def create_environment(
        self, user: User, workspace_id: UUID, project_id: UUID, payload: EnvironmentCreate
    ) -> Environment:
        # OWNER, ADMIN, and MEMBER can create environments
        await self._require_project_and_role(
            user, workspace_id, project_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        return await self._repo.create(project_id, payload)

    async def list_environments(
        self, user: User, workspace_id: UUID, project_id: UUID, skip: int = 0, limit: int = 50
    ) -> EnvironmentList:
        # All roles can list
        await self._require_project_and_role(
            user, workspace_id, project_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        items, total = await self._repo.list_by_project(project_id, skip, limit)
        return EnvironmentList(items=items, total=total, skip=skip, limit=limit)

    async def get_environment(
        self, user: User, workspace_id: UUID, project_id: UUID, environment_id: UUID
    ) -> Environment:
        await self._require_project_and_role(
            user, workspace_id, project_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        env = await self._repo.get_by_id(environment_id)
        if not env or env.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        return env

    async def update_environment(
        self, user: User, workspace_id: UUID, project_id: UUID, environment_id: UUID, payload: EnvironmentUpdate
    ) -> Environment:
        await self._require_project_and_role(
            user, workspace_id, project_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        env = await self._repo.get_by_id(environment_id)
        if not env or env.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        
        return await self._repo.update(env, payload)

    async def delete_environment(
        self, user: User, workspace_id: UUID, project_id: UUID, environment_id: UUID
    ) -> None:
        await self._require_project_and_role(
            user, workspace_id, project_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        env = await self._repo.get_by_id(environment_id)
        if not env or env.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        await self._repo.delete(env)
