"""
app/ai/utils/chunking.py

Generic, provider-agnostic text chunking used by the Knowledge Orchestrator
before handing text to an embedding provider. Deliberately simple (word
count based, fixed overlap) — real chunking strategies belong behind a
`RetrievalProvider`/future chunking provider, not the platform core.
"""
from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """Split `text` into overlapping chunks of roughly `chunk_size` words.

    Args:
        text: Source text to split.
        chunk_size: Target number of words per chunk.
        overlap: Number of words repeated between consecutive chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size.")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks
