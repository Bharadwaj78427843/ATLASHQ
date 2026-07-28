"""
app/services/workspace.py

Service layer for Workspaces, enforcing organizational RBAC.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.workspace import Workspace
from app.models.organization_member import MemberRole, MemberStatus
from app.repositories.workspace import WorkspaceRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceList

class WorkspaceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = WorkspaceRepository(session)
        self._member_repo = OrganizationMemberRepository(session)

    async def _require_member_role(
        self, user: User, organization_id: UUID, allowed_roles: set[MemberRole]
    ):
        """Verifies the user is an active member with one of the allowed roles."""
        member = await self._member_repo.get_by_org_and_user(organization_id, user.id)
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
        return member

    async def create_workspace(
        self, user: User, organization_id: UUID, payload: WorkspaceCreate
    ) -> Workspace:
        await self._require_member_role(
            user, organization_id, {MemberRole.OWNER, MemberRole.ADMIN}
        )
        try:
            return await self._repo.create(organization_id, payload)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A workspace with this slug already exists in the organization",
            )

    async def list_workspaces(
        self, user: User, organization_id: UUID, skip: int = 0, limit: int = 50
    ) -> WorkspaceList:
        await self._require_member_role(
            user, organization_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        items, total = await self._repo.list_by_organization(organization_id, skip, limit)
        return WorkspaceList(items=items, total=total, skip=skip, limit=limit)

    async def get_workspace(
        self, user: User, organization_id: UUID, workspace_id: UUID
    ) -> Workspace:
        await self._require_member_role(
            user, organization_id, {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER, MemberRole.VIEWER}
        )
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace or workspace.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return workspace

    async def update_workspace(
        self, user: User, organization_id: UUID, workspace_id: UUID, payload: WorkspaceUpdate
    ) -> Workspace:
        await self._require_member_role(
            user, organization_id, {MemberRole.OWNER, MemberRole.ADMIN}
        )
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace or workspace.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        
        try:
            return await self._repo.update(workspace, payload)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A workspace with this slug already exists in the organization",
            )

    async def delete_workspace(
        self, user: User, organization_id: UUID, workspace_id: UUID
    ) -> None:
        await self._require_member_role(
            user, organization_id, {MemberRole.OWNER, MemberRole.ADMIN}
        )
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace or workspace.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        await self._repo.delete(workspace)
