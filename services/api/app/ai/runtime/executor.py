from __future__ import annotations

import asyncio
import time
from typing import Any

from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.events import RuntimeEvent, RuntimeEventType
from app.ai.runtime.exceptions import ExecutionCancelledError, ExecutionTimeoutError
from app.ai.runtime.interfaces import EventPublisher
from app.ai.runtime.models import AgentExecutionResult, ExecutionPlan, ExecutionStatus, StepResult, StepStatus
from app.ai.runtime.scheduler import RuntimeScheduler


class RuntimeExecutor:
    def __init__(
        self,
        *,
        event_publisher: EventPublisher,
        scheduler: RuntimeScheduler,
        max_tool_retries: int = 2,
    ) -> None:
        self._event_publisher = event_publisher
        self._scheduler = scheduler
        self._max_tool_retries = max_tool_retries
        self._cancelled: set[str] = set()

    def cancel(self, execution_id: str) -> None:
        self._cancelled.add(execution_id)

    def _check_cancelled(self, execution_id: str) -> None:
        if execution_id in self._cancelled:
            raise ExecutionCancelledError("Execution cancelled by request.")

    async def _run_step(self, context: ExecutionContext, agent, step) -> StepResult:
        self._check_cancelled(context.execution_id)
        await self._event_publisher.publish(
            RuntimeEvent(context.execution_id, RuntimeEventType.STEP_STARTED, f"Executing step: {step.task}", {"step_id": step.id})
        )
        started = time.perf_counter()
        attempts = 0
        while True:
            try:
                output, evidence = await agent.execute_step(context, step)
                duration_ms = int((time.perf_counter() - started) * 1000)
                await self._event_publisher.publish(
                    RuntimeEvent(context.execution_id, RuntimeEventType.STEP_COMPLETED, f"Completed step: {step.task}", {"step_id": step.id})
                )
                return StepResult(step_id=step.id, status=StepStatus.COMPLETED, output=output, evidence=evidence, duration_ms=duration_ms)
            except ExecutionCancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                attempts += 1
                if attempts > self._max_tool_retries:
                    duration_ms = int((time.perf_counter() - started) * 1000)
                    await self._event_publisher.publish(
                        RuntimeEvent(context.execution_id, RuntimeEventType.ERROR, f"Step failed: {step.task}", {"step_id": step.id, "error": str(exc)})
                    )
                    return StepResult(step_id=step.id, status=StepStatus.FAILED, error=str(exc), duration_ms=duration_ms)

    async def execute(self, context: ExecutionContext, plan: ExecutionPlan, agent, timeout_seconds: int | None = None) -> AgentExecutionResult:
        async def _execute_internal() -> AgentExecutionResult:
            self._check_cancelled(context.execution_id)
            steps: list[StepResult] = []
            parallel, sequential = [], []
            for step in plan.steps:
                (parallel if step.parallelizable else sequential).append(step)

            for step in sequential:
                self._check_cancelled(context.execution_id)
                steps.append(await self._run_step(context, agent, step))

            if parallel:
                await self._event_publisher.publish(
                    RuntimeEvent(context.execution_id, RuntimeEventType.WAITING, "Waiting for parallel steps")
                )
                tasks = [self._scheduler.run(self._run_step(context, agent, step)) for step in parallel]
                steps.extend(await asyncio.gather(*tasks))

            failed = [s for s in steps if s.status == StepStatus.FAILED]
            status = ExecutionStatus.FAILED if failed else ExecutionStatus.COMPLETED
            answer = await agent.finalize(context, plan, steps)
            evidence = [ev for step in steps for ev in step.evidence]
            return AgentExecutionResult(
                execution_id=context.execution_id,
                status=status,
                answer=answer,
                steps=steps,
                evidence=evidence,
            )

        try:
            if timeout_seconds:
                return await asyncio.wait_for(_execute_internal(), timeout=timeout_seconds)
            return await _execute_internal()
        except asyncio.TimeoutError as exc:
            raise ExecutionTimeoutError("Execution timed out.") from exc
