import os
import shutil
import tempfile
import pytest
from app.services.repository_indexer import RepositoryIndexer
from app.schemas.knowledge import RepositoryMetadata

@pytest.fixture
def indexer():
    return RepositoryIndexer()

@pytest.fixture
def sample_repo():
    # Create a temporary directory structure mimicking a repository
    temp_dir = tempfile.mkdtemp()
    
    # Create ignored directories
    os.makedirs(os.path.join(temp_dir, ".git"))
    os.makedirs(os.path.join(temp_dir, "node_modules"))
    
    # Create source directories
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)
    
    # Create files
    files = {
        "README.md": b"# Test Repo",
        "LICENSE": b"MIT License",
        "package.json": b'{"name": "test"}',
        "pnpm-lock.yaml": b"lockfile",
        "Dockerfile": b"FROM ubuntu",
        "src/main.ts": b"console.log('hello');" * 100,  # ~2100 bytes
        "src/utils.js": b"function noop() {}",
        ".git/config": b"git config data",  # Should be ignored
        "node_modules/index.js": b"ignored lib"  # Should be ignored
    }
    
    for path, content in files.items():
        full_path = os.path.join(temp_dir, path)
        with open(full_path, "wb") as f:
            f.write(content)
            
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_analyze_repository(indexer, sample_repo):
    metadata = indexer.analyze(
        path=sample_repo, 
        provider="github", 
        repository_url="https://github.com/test/test", 
        default_branch="main"
    )
    
    # Validate Metadata Structure
    assert isinstance(metadata, RepositoryMetadata)
    assert metadata.provider == "github"
    assert metadata.repository_url == "https://github.com/test/test"
    assert metadata.default_branch == "main"
    assert metadata.index_status == "ready"
    
    # Validate Ignored Directories
    # Files: README.md, LICENSE, package.json, pnpm-lock.yaml, Dockerfile, src/main.ts, src/utils.js = 7 files
    assert metadata.statistics["file_count"] == 7
    # Folders: root and src (ignored .git and node_modules are pruned before counting inside them)
    # Actually root is not counted as a child dir. Only 'src' is counted. 
    # Wait, os.walk yields root, dirs, files. `len(dirs)` in root is 1 ('src' since .git and node_modules were pruned). 
    # Inside 'src', `len(dirs)` is 0. Total folder_count = 1.
    assert metadata.statistics["folder_count"] == 1
    
    # Validate Languages
    # Total language files: main.ts (1), utils.js (1), README.md (1), package.json (.json: 1), pnpm-lock.yaml (.yaml: 1) = 5
    assert metadata.languages["TypeScript"] == 20.0  # 1/5
    assert metadata.languages["JavaScript"] == 20.0  # 1/5
    assert metadata.languages["Markdown"] == 20.0    # 1/5
    assert metadata.languages["JSON"] == 20.0        # 1/5
    assert metadata.languages["YAML"] == 20.0        # 1/5
    
    # Validate Frameworks and Package Managers
    assert "Node.js" in metadata.frameworks
    assert "Docker" in metadata.frameworks
    assert "pnpm" in metadata.package_managers
    
    # Validate Directory Summary
    assert metadata.directory_summary["has_readme"] is True
    assert metadata.directory_summary["has_license"] is True
    assert metadata.directory_summary["has_dockerfile"] is True
    assert metadata.directory_summary["has_docker_compose"] is False
    assert metadata.directory_summary["has_gitignore"] is False
    
    # Validate Largest Files
    # src/main.ts is the largest file (~2100 bytes)
    largest = metadata.statistics["largest_files"][0]
    assert largest["path"] == os.path.join("src", "main.ts").replace("\\", "/") or largest["path"] == os.path.join("src", "main.ts")
    assert largest["size_bytes"] >= 2000

def test_analyze_non_existent_directory(indexer):
    metadata = indexer.analyze("/tmp/does-not-exist-12345")
    assert metadata.index_status == "failed"
    assert metadata.statistics["file_count"] == 0

def test_determinism(indexer, sample_repo):
    meta1 = indexer.analyze(sample_repo)
    meta2 = indexer.analyze(sample_repo)
    
    # Dump to model_dump to compare dictionaries completely, ignoring timestamp
    assert meta1.model_dump(exclude={'last_sync'}) == meta2.model_dump(exclude={'last_sync'})
