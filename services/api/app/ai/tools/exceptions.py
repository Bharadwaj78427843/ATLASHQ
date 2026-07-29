from app.ai.runtime.exceptions import PermissionDeniedError


class ToolError(Exception):
    """Generic tool framework error."""


class ToolNotFoundError(ToolError):
    """Requested tool was not registered."""


class ToolExecutionError(ToolError):
    """Tool execution failed."""


class ToolPermissionError(PermissionDeniedError):
    """Tool was invoked without required permission."""
