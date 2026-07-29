from __future__ import annotations

from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.base import KnowledgeProvider
from app.ai.knowledge.native import NativeKnowledgeProvider
from app.ai.knowledge.ragflow import RAGFlowKnowledgeProvider
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry


class KnowledgeProviderFactory:
    """Builds knowledge providers from AI config without changing SDK code."""

    def __init__(self, provider_factory: ProviderFactory, telemetry: TelemetryContext | None = None) -> None:
        self._provider_factory = provider_factory
        self._telemetry = telemetry or get_telemetry()

    def create(self) -> KnowledgeProvider:
        selection = self._provider_factory.selection_for("knowledge")
        if selection.provider == "native":
            return NativeKnowledgeProvider(factory=self._provider_factory, telemetry=self._telemetry)
        if selection.provider == "ragflow":
            return RAGFlowKnowledgeProvider(config=selection.options, telemetry=self._telemetry)
        if selection.provider == "mock":
            return NativeKnowledgeProvider(factory=self._provider_factory, telemetry=self._telemetry)
        raise ValueError(f"Unsupported knowledge provider: {selection.provider}")
