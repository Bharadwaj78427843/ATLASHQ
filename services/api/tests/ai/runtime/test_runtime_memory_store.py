import pytest

from app.ai.interfaces.memory import MemoryKey
from app.ai.memory.mock import MockMemoryProvider
from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.memory import RuntimeMemoryStore


@pytest.mark.asyncio
async def test_runtime_memory_store_uses_scoped_keys_and_clears_workspace_scope():
    provider = MockMemoryProvider()
    store = RuntimeMemoryStore(provider)
    context = ExecutionContext(
        execution_id="exec-1",
        workspace_id="workspace-1",
        memory_scope="workspace",
    )

    await store.append(context, "skill_steps", {"step": "discover"})
    await store.write(context, "skill_results", {"status": "completed"})

    scoped_steps = await provider.get(MemoryKey(scope="workspace:workspace-1", identifier="skill_steps"))
    scoped_results = await provider.get(MemoryKey(scope="workspace:workspace-1", identifier="skill_results"))

    assert scoped_steps is not None
    assert scoped_steps.value == [{"step": "discover"}]
    assert scoped_results is not None
    assert scoped_results.value == {"status": "completed"}

    assert await store.read(context, "skill_steps") == [{"step": "discover"}]
    assert await store.read(context, "skill_results") == [{"status": "completed"}]

    await store.clear_workspace("workspace-1")

    assert await provider.get(MemoryKey(scope="workspace:workspace-1", identifier="skill_steps")) is None
    assert await provider.get(MemoryKey(scope="workspace:workspace-1", identifier="skill_results")) is None
