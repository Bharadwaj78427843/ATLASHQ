from app.ai.exceptions.errors import AgentError


class RuntimeError(AgentError):
    """Base runtime failure."""


class ExecutionCancelledError(RuntimeError):
    """Execution has been cancelled by request."""


class ExecutionTimeoutError(RuntimeError):
    """Execution exceeded configured timeout."""


class PermissionDeniedError(RuntimeError):
    """Tool call denied by runtime permission check."""
