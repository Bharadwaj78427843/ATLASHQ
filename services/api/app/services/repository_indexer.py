from datetime import datetime, timezone
from typing import Dict, List, Optional
import os
import heapq
import logging

from app.schemas.knowledge import RepositoryMetadata

logger = logging.getLogger(__name__)

class RepositoryIndexer:
    """
    A pure service that analyzes a cloned repository directory.
    Extracts metadata, language breakdowns, frameworks, and statistics.
    Independent of git operations, database, and background jobs.
    """
    IGNORED_DIRS = {
        ".git", "node_modules", ".next", "dist", "build", "venv", "__pycache__", 
        ".pytest_cache", ".idea", ".vscode", "coverage", "out", ".mypy_cache", ".ruff_cache"
    }

    LANGUAGE_EXTENSIONS = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "JavaScript (React)", ".tsx": "TypeScript (React)",
        ".html": "HTML", ".css": "CSS", ".json": "JSON", ".md": "Markdown",
        ".go": "Go", ".rs": "Rust", ".java": "Java", ".c": "C", ".cpp": "C++",
        ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".sh": "Shell", ".yml": "YAML",
        ".yaml": "YAML", ".toml": "TOML", ".xml": "XML", ".sql": "SQL"
    }

    FRAMEWORK_FILES = {
        "package.json": "Node.js",
        "pyproject.toml": "Python (Poetry/UV)",
        "requirements.txt": "Python",
        "Cargo.toml": "Rust",
        "pom.xml": "Java (Maven)",
        "go.mod": "Go",
        "next.config.js": "Next.js",
        "next.config.ts": "Next.js",
        "vite.config.ts": "Vite",
        "vite.config.js": "Vite",
        "manage.py": "Django",
        "artisan": "Laravel",
        "docker-compose.yml": "Docker",
        "Dockerfile": "Docker"
    }

    PACKAGE_MANAGERS = {
        "pnpm-lock.yaml": "pnpm",
        "package-lock.json": "npm",
        "yarn.lock": "yarn",
        "uv.lock": "uv",
        "poetry.lock": "poetry",
        "Pipfile.lock": "pipenv",
        "Cargo.lock": "cargo",
        "go.sum": "go modules"
    }

    def analyze(self, path: str, provider: str = "unknown", repository_url: str = "unknown", default_branch: str = "main") -> RepositoryMetadata:
        logger.info(f"Starting repository indexer for path: {path}")
        
        file_count = 0
        folder_count = 0
        total_size = 0
        languages: Dict[str, int] = {}
        frameworks = set()
        package_managers = set()
        largest_files = []  # min-heap of (size, rel_path)
        
        directory_summary = {
            "has_readme": False,
            "has_license": False,
            "has_dockerfile": False,
            "has_docker_compose": False,
            "has_gitignore": False
        }

        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return self._build_empty_metadata(provider, repository_url, default_branch)

        for root, dirs, files in os.walk(path):
            # Prune ignored directories in-place to stop traversal
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS]
            folder_count += len(dirs)

            for file in files:
                file_count += 1
                filepath = os.path.join(root, file)
                
                # We can skip symlinks if we want, but let's just use getsize
                try:
                    if os.path.islink(filepath):
                        size = 0
                    else:
                        size = os.path.getsize(filepath)
                except OSError:
                    size = 0
                    
                total_size += size

                # Track top 10 largest files
                rel_path = os.path.relpath(filepath, path)
                if len(largest_files) < 10:
                    heapq.heappush(largest_files, (size, rel_path))
                else:
                    heapq.heappushpop(largest_files, (size, rel_path))

                # Language by extension
                ext = os.path.splitext(file)[1].lower()
                if ext in self.LANGUAGE_EXTENSIONS:
                    lang = self.LANGUAGE_EXTENSIONS[ext]
                    languages[lang] = languages.get(lang, 0) + 1

                # Detect frameworks
                if file in self.FRAMEWORK_FILES:
                    frameworks.add(self.FRAMEWORK_FILES[file])
                
                # Detect package managers
                if file in self.PACKAGE_MANAGERS:
                    package_managers.add(self.PACKAGE_MANAGERS[file])

                # Check specific significant files
                lname = file.lower()
                if "readme" in lname:
                    directory_summary["has_readme"] = True
                if "license" in lname:
                    directory_summary["has_license"] = True
                if lname == "dockerfile":
                    directory_summary["has_dockerfile"] = True
                if lname in ("docker-compose.yml", "docker-compose.yaml"):
                    directory_summary["has_docker_compose"] = True
                if lname == ".gitignore":
                    directory_summary["has_gitignore"] = True

        # Sort largest files descending by size
        largest_files_sorted = sorted([{"path": p, "size_bytes": s} for s, p in largest_files], key=lambda x: x["size_bytes"], reverse=True)
        
        # Calculate language breakdown as percentages based on file count
        total_lang_files = sum(languages.values())
        lang_percentages = {}
        if total_lang_files > 0:
            for lang, count in languages.items():
                lang_percentages[lang] = round((count / total_lang_files) * 100, 2)

        statistics = {
            "file_count": file_count,
            "folder_count": folder_count,
            "total_size_bytes": total_size,
            "largest_files": largest_files_sorted
        }

        return RepositoryMetadata(
            provider=provider,
            repository_url=repository_url,
            default_branch=default_branch,
            index_status="ready",
            last_sync=datetime.now(timezone.utc),
            languages=lang_percentages,
            frameworks=sorted(list(frameworks)),
            package_managers=sorted(list(package_managers)),
            statistics=statistics,
            directory_summary=directory_summary
        )

    def _build_empty_metadata(self, provider: str, url: str, branch: str) -> RepositoryMetadata:
        """Fallback for empty or non-existent directories."""
        return RepositoryMetadata(
            provider=provider,
            repository_url=url,
            default_branch=branch,
            index_status="failed",
            last_sync=datetime.now(timezone.utc),
            languages={},
            frameworks=[],
            package_managers=[],
            statistics={
                "file_count": 0,
                "folder_count": 0,
                "total_size_bytes": 0,
                "largest_files": []
            },
            directory_summary={
                "has_readme": False,
                "has_license": False,
                "has_dockerfile": False,
                "has_docker_compose": False,
                "has_gitignore": False
            }
        )
