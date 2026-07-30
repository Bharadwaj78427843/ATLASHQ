import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.knowledge import IndexingService, StorageService
from app.services.git_service import GitCloneService, GitCloneResult
from app.services.repository_indexer import RepositoryIndexer
from app.models.knowledge import KnowledgeSource, IndexJob
from app.schemas.knowledge import RepositoryMetadata

@pytest.fixture
def mock_repository():
    return MagicMock()

@pytest.fixture
def mock_orchestrator():
    return AsyncMock()

@pytest.fixture
def mock_git_service():
    return AsyncMock(spec=GitCloneService)

@pytest.fixture
def mock_indexer():
    return MagicMock(spec=RepositoryIndexer)

@pytest.fixture
def mock_storage():
    return MagicMock(spec=StorageService)

@pytest.fixture
def indexing_service(mock_repository, mock_orchestrator, mock_git_service, mock_indexer, mock_storage):
    return IndexingService(
        repository=mock_repository,
        orchestrator=mock_orchestrator,
        git_service=mock_git_service,
        indexer=mock_indexer,
        storage_service=mock_storage
    )

@pytest.mark.asyncio
async def test_index_repository_success(indexing_service, mock_repository, mock_git_service, mock_indexer, mock_storage):
    source_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    job_id = uuid.uuid4()

    source = KnowledgeSource(
        id=source_id,
        workspace_id=workspace_id,
        name="github://test/repo",
        source_type="repository",
        metadata_json={"provider": "github", "repository": "test/repo"}
    )
    job = IndexJob(id=job_id, source_id=source_id, status="cloning")

    mock_repository.get_source.return_value = source
    mock_repository.create_index_job.return_value = job

    # Mock Workspace Query
    mock_workspace = MagicMock()
    mock_workspace.organization_id = "org_123"
    mock_repository.db.query.return_value.filter.return_value.first.return_value = mock_workspace

    mock_storage.get_repository_path.return_value = "/tmp/repo"
    mock_git_service.clone_or_pull.return_value = GitCloneResult(path="/tmp/repo", default_branch="main", newly_cloned=True)
    
    mock_metadata = MagicMock(spec=RepositoryMetadata)
    mock_metadata.model_dump.return_value = {"languages": {"Python": 100}}
    mock_indexer.analyze.return_value = mock_metadata

    await indexing_service.index_source(source_id)

    # Asserts
    mock_git_service.clone_or_pull.assert_called_once_with("https://github.com/test/repo", "/tmp/repo")
    mock_indexer.analyze.assert_called_once_with("/tmp/repo", "github", "https://github.com/test/repo", "main")
    
    assert source.metadata_json == {"languages": {"Python": 100}}
    
    # Assert status updates
    calls = mock_repository.update_source_status.call_args_list
    assert calls[0].args == (source_id, "cloning")
    assert calls[1].args == (source_id, "indexing")
    assert calls[2].args == (source_id, "ready")

    job_calls = mock_repository.update_index_job.call_args_list
    assert job_calls[0].args == (job_id, "indexing")
    assert job_calls[1].args == (job_id, "completed")

@pytest.mark.asyncio
async def test_index_repository_clone_failure(indexing_service, mock_repository, mock_git_service):
    source_id = uuid.uuid4()
    job_id = uuid.uuid4()

    source = KnowledgeSource(
        id=source_id,
        source_type="repository",
        metadata_json={"provider": "github", "repository": "test/repo"}
    )
    job = IndexJob(id=job_id, source_id=source_id, status="cloning")

    mock_repository.get_source.return_value = source
    mock_repository.create_index_job.return_value = job
    
    mock_git_service.clone_or_pull.side_effect = Exception("Git error")

    await indexing_service.index_source(source_id)

    mock_repository.update_source_status.assert_any_call(source_id, "failed")
    mock_repository.update_index_job.assert_any_call(job_id, "failed", progress=0.0)
