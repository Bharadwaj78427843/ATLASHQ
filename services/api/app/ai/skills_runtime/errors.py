class SkillRuntimeError(Exception):
    """Base skill runtime failure."""


class SkillNotFoundError(SkillRuntimeError):
    """Requested skill could not be resolved."""


class SkillValidationError(SkillRuntimeError):
    """Skill manifest or artifact validation failed."""


class DependencyResolutionError(SkillRuntimeError):
    """A dependency graph could not be resolved."""


class DependencyCycleError(DependencyResolutionError):
    """A dependency cycle was detected."""


class DependencyVersionError(DependencyResolutionError):
    """A dependency version constraint was not satisfied."""


class PolicyBlockedError(SkillRuntimeError):
    """Execution was blocked by policy."""


class ToolPermissionDeniedError(SkillRuntimeError):
    """A requested tool was not authorized."""


class OutputValidationError(SkillRuntimeError):
    """Skill output did not satisfy its contract."""


class SkillInstallError(SkillRuntimeError):
    """A skill could not be installed or updated."""
