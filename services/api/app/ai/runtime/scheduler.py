from __future__ import annotations

import asyncio
from collections import deque


class RuntimeScheduler:
    """Simple bounded scheduler for execution tasks."""

    def __init__(self, max_parallel_tasks: int = 4) -> None:
        self._max_parallel_tasks = max_parallel_tasks
        self._sem = asyncio.Semaphore(max_parallel_tasks)

    async def run(self, coro):
        async with self._sem:
            return await coro
