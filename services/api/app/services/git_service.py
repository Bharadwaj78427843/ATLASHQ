import asyncio
import logging
import os
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Domain Exceptions
class InvalidRepositoryUrl(Exception):
    """Raised when the repository URL is not a valid public GitHub URL."""
    pass

class RepositoryNotFound(Exception):
    """Raised when the repository cannot be cloned (e.g., not found, private, or typo)."""
    pass

class CloneFailed(Exception):
    """Raised when the git clone command fails for another reason."""
    pass

class PullFailed(Exception):
    """Raised when the git pull command fails on an existing repository."""
    pass


class GitCloneResult:
    """Structured result object for clone operations."""
    def __init__(self, path: str, default_branch: str, newly_cloned: bool):
        self.path = path
        self.default_branch = default_branch
        self.newly_cloned = newly_cloned


class GitCloneService:
    """
    A service responsible exclusively for Git operations.
    Supports only public GitHub repositories.
    Converts subprocess failures into domain-specific exceptions.
    """

    def validate_url(self, url: str) -> bool:
        """
        Validates that the URL points to a public GitHub repository.
        Expected formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        """
        pattern = r"^https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?$"
        if not re.match(pattern, url):
            logger.warning(f"Validation failed for URL: {url}")
            return False
        return True

    async def _run_command(self, *args: str, cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """Runs an async subprocess and returns (return_code, stdout, stderr)."""
        process = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode().strip(), stderr.decode().strip()

    async def _detect_default_branch(self, target_path: str) -> str:
        """Detects the default branch of a cloned repository."""
        # Try symbolic-ref first
        code, out, err = await self._run_command("git", "symbolic-ref", "refs/remotes/origin/HEAD", cwd=target_path)
        if code == 0 and out:
            # output typically looks like refs/remotes/origin/main
            return out.split("/")[-1].strip()
            
        # Fallback to listing branches if symbolic-ref fails
        code, out, err = await self._run_command("git", "branch", "-r", cwd=target_path)
        if code == 0 and "origin/main" in out:
            return "main"
        if code == 0 and "origin/master" in out:
            return "master"

        logger.warning(f"Could not reliably detect default branch for {target_path}. Falling back to 'main'.")
        return "main"

    async def clone_or_pull(self, url: str, target_path: str) -> GitCloneResult:
        """
        Clones a new repository using --depth 1 or pulls updates if it already exists.
        Validates URL and ensures domain exceptions are thrown on failure.
        """
        if not self.validate_url(url):
            raise InvalidRepositoryUrl(f"Only public GitHub URLs are supported. Got: {url}")

        git_dir = os.path.join(target_path, ".git")
        is_new = not os.path.exists(git_dir)

        if is_new:
            logger.info(f"Cloning repository: {url} into {target_path}")
            # Ensure parent exists, but for cloning, we can let git create the final directory
            # If target_path exists and is empty, git clone can use it.
            # If it doesn't exist, git clone will create it.
            
            # To avoid git complaining about existing non-empty dir, we just run clone.
            # If the user created target_path, we clone inside it or remove it.
            # Safe way: git clone url target_path
            code, out, err = await self._run_command("git", "clone", "--depth", "1", url, target_path)
            
            if code != 0:
                logger.error(f"Clone failed for {url}. Error: {err}")
                if "not found" in err.lower() or "authentication failed" in err.lower() or "could not read username" in err.lower():
                    raise RepositoryNotFound(f"Repository not found or is private: {url}")
                raise CloneFailed(f"Failed to clone repository {url}: {err}")
        else:
            logger.info(f"Pulling updates for repository: {url} at {target_path}")
            code, out, err = await self._run_command("git", "pull", cwd=target_path)
            if code != 0:
                logger.error(f"Pull failed for {url}. Error: {err}")
                raise PullFailed(f"Failed to pull repository {url}: {err}")

        # Detect the default branch
        default_branch = await self._detect_default_branch(target_path)
        logger.info(f"Detected default branch '{default_branch}' for {url}")

        return GitCloneResult(
            path=target_path,
            default_branch=default_branch,
            newly_cloned=is_new
        )
