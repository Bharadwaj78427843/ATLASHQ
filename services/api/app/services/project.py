"""
app/services/project.py

Service layer for Projects, enforcing organizational RBAC.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.project import Project
from app.models.organization_member import MemberRole, MemberStatus
from app.repositories.project import ProjectRepository
from app.repositories.workspace import WorkspaceRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectList

class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = ProjectRepository(session)
        self._ws_repo = WorkspaceRepository(session)
        self._member_repo = OrganizationMemberRepository(session)

    async def _require_workspace_and_role(
        self, user: User, workspace_id: UUID, allowed_roles: set[MemberRole]
    ):
        """Verifies workspace exists and user has allowed role in its organization."""
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
        return workspace, member

    async def create_project(
        self, user: User, workspace_id: UUID, payload: ProjectCreate
    ) -> Project:
        # OWNER, ADMIN, and MEMBER can create projects (only VIEWER cannot)
        await self._require_workspace_and_role(
            user, workspace_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        return await self._repo.create(workspace_id, payload)

    async def list_projects(
        self, user: User, workspace_id: UUID, skip: int = 0, limit: int = 50
    ) -> ProjectList:
        # All roles can list
        await self._require_workspace_and_role(
            user, workspace_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        items, total = await self._repo.list_by_workspace(workspace_id, skip, limit)
        return ProjectList(items=items, total=total, skip=skip, limit=limit)

    async def get_project(
        self, user: User, workspace_id: UUID, project_id: UUID
    ) -> Project:
        await self._require_workspace_and_role(
            user, workspace_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        project = await self._repo.get_by_id(project_id)
        if not project or project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    async def update_project(
        self, user: User, workspace_id: UUID, project_id: UUID, payload: ProjectUpdate
    ) -> Project:
        await self._require_workspace_and_role(
            user, workspace_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        project = await self._repo.get_by_id(project_id)
        if not project or project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        
        return await self._repo.update(project, payload)

    async def delete_project(
        self, user: User, workspace_id: UUID, project_id: UUID
    ) -> None:
        await self._require_workspace_and_role(
            user, workspace_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}
        )
        project = await self._repo.get_by_id(project_id)
        if not project or project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        await self._repo.delete(project)
