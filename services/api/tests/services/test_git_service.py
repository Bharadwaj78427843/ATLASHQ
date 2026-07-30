import os
import pytest
from unittest.mock import patch, AsyncMock
from app.services.git_service import (
    GitCloneService,
    InvalidRepositoryUrl,
    RepositoryNotFound,
    CloneFailed,
    PullFailed,
    GitCloneResult
)

@pytest.fixture
def git_service():
    return GitCloneService()

@pytest.mark.asyncio
async def test_validate_url(git_service):
    assert git_service.validate_url("https://github.com/facebook/react") is True
    assert git_service.validate_url("https://github.com/facebook/react.git") is True
    assert git_service.validate_url("http://github.com/facebook/react") is False
    assert git_service.validate_url("https://gitlab.com/facebook/react") is False
    assert git_service.validate_url("git@github.com:facebook/react.git") is False

@pytest.mark.asyncio
async def test_clone_invalid_url(git_service):
    with pytest.raises(InvalidRepositoryUrl):
        await git_service.clone_or_pull("invalid-url", "/tmp/repo")

@pytest.mark.asyncio
@patch('app.services.git_service.GitCloneService._run_command')
@patch('os.path.exists')
async def test_clone_new_repository_success(mock_exists, mock_run_command, git_service):
    # Setup mocks
    mock_exists.return_value = False  # .git doesn't exist, meaning it's new
    
    async def mock_run(*args, **kwargs):
        if args[1] == "clone":
            return (0, "", "")
        if args[1] == "symbolic-ref":
            return (0, "refs/remotes/origin/main", "")
        return (0, "", "")

    mock_run_command.side_effect = mock_run

    result = await git_service.clone_or_pull("https://github.com/test/repo", "/tmp/repo")

    assert result.path == "/tmp/repo"
    assert result.default_branch == "main"
    assert result.newly_cloned is True
    
    # Assert clone command was called
    calls = mock_run_command.call_args_list
    assert calls[0].args == ("git", "clone", "--depth", "1", "https://github.com/test/repo", "/tmp/repo")

@pytest.mark.asyncio
@patch('app.services.git_service.GitCloneService._run_command')
@patch('os.path.exists')
async def test_pull_existing_repository_success(mock_exists, mock_run_command, git_service):
    mock_exists.return_value = True  # .git exists
    
    async def mock_run(*args, **kwargs):
        if args[1] == "pull":
            return (0, "Already up to date.", "")
        if args[1] == "symbolic-ref":
            return (0, "refs/remotes/origin/main", "")
        return (0, "", "")

    mock_run_command.side_effect = mock_run

    result = await git_service.clone_or_pull("https://github.com/test/repo", "/tmp/repo")

    assert result.path == "/tmp/repo"
    assert result.default_branch == "main"
    assert result.newly_cloned is False

    calls = mock_run_command.call_args_list
    assert calls[0].args == ("git", "pull")
    assert calls[0].kwargs["cwd"] == "/tmp/repo"

@pytest.mark.asyncio
@patch('app.services.git_service.GitCloneService._run_command')
@patch('os.path.exists')
async def test_clone_repository_not_found(mock_exists, mock_run_command, git_service):
    mock_exists.return_value = False
    
    async def mock_run(*args, **kwargs):
        if args[1] == "clone":
            return (128, "", "fatal: repository 'https://github.com/test/repo/' not found")
        return (0, "", "")

    mock_run_command.side_effect = mock_run

    with pytest.raises(RepositoryNotFound):
        await git_service.clone_or_pull("https://github.com/test/repo", "/tmp/repo")

@pytest.mark.asyncio
@patch('app.services.git_service.GitCloneService._run_command')
@patch('os.path.exists')
async def test_pull_failed(mock_exists, mock_run_command, git_service):
    mock_exists.return_value = True
    
    async def mock_run(*args, **kwargs):
        if args[1] == "pull":
            return (1, "", "error: merge conflict")
        return (0, "", "")

    mock_run_command.side_effect = mock_run

    with pytest.raises(PullFailed):
        await git_service.clone_or_pull("https://github.com/test/repo", "/tmp/repo")

@pytest.mark.asyncio
@patch('app.services.git_service.GitCloneService._run_command')
async def test_detect_default_branch_fallback(mock_run_command, git_service):
    async def mock_run(*args, **kwargs):
        if args[1] == "symbolic-ref":
            return (1, "", "error")
        if args[1] == "branch":
            return (0, "  origin/master\n", "")
        return (0, "", "")

    mock_run_command.side_effect = mock_run

    branch = await git_service._detect_default_branch("/tmp/repo")
    assert branch == "master"
