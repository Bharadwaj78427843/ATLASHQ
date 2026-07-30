import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.routers.knowledge import get_services
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.knowledge import KnowledgeSourceResponse

@pytest.fixture
def mock_repo_service():
    service = AsyncMock()
    return service

@pytest_asyncio.fixture
async def client(mock_repo_service) -> AsyncClient:
    async def _override_user():
        return User(id=uuid.uuid4(), email="test@test.com")
        
    async def _override_services():
        return MagicMock(), MagicMock(), MagicMock(), mock_repo_service

    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[get_services] = _override_services
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_sync_repository_success(client: AsyncClient, mock_repo_service):
    source_id = uuid.uuid4()
    
    # Mock return value to match schema
    mock_repo_service.sync_repository.return_value = {
        "id": source_id,
        "workspace_id": uuid.uuid4(),
        "project_id": None,
        "name": "github://test/test",
        "source_type": "repository",
        "status": "validating",
        "size_bytes": 0,
        "uploaded_by": uuid.uuid4(),
        "storage_path": None,
        "created_at": "2026-07-30T12:00:00Z",
        "updated_at": "2026-07-30T12:00:00Z",
        "metadata_json": {}
    }
    
    resp = await client.post(f"/knowledge/repositories/{source_id}/sync")
    
    assert resp.status_code == 200
    mock_repo_service.sync_repository.assert_awaited_once_with(source_id)

@pytest.mark.asyncio
async def test_sync_repository_not_found(client: AsyncClient, mock_repo_service):
    source_id = uuid.uuid4()
    mock_repo_service.sync_repository.side_effect = ValueError("Knowledge source not found")
    
    resp = await client.post(f"/knowledge/repositories/{source_id}/sync")
    
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_sync_repository_already_in_progress(client: AsyncClient, mock_repo_service):
    source_id = uuid.uuid4()
    mock_repo_service.sync_repository.side_effect = ValueError("Repository sync is already in progress")
    
    resp = await client.post(f"/knowledge/repositories/{source_id}/sync")
    
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_sync_repository_invalid_source(client: AsyncClient, mock_repo_service):
    source_id = uuid.uuid4()
    mock_repo_service.sync_repository.side_effect = ValueError("Source is not a repository")
    
    resp = await client.post(f"/knowledge/repositories/{source_id}/sync")
    
    assert resp.status_code == 400
