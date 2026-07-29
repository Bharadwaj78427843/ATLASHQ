from app.ai.exceptions.errors import ProviderError


class KnowledgeProviderError(ProviderError):
    """Raised when a knowledge provider cannot complete an operation."""
