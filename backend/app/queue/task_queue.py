import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from app.monitoring.metrics import (
    QUEUE_SIZE,
    QUEUE_TASKS_COMPLETED_TOTAL,
    QUEUE_TASKS_FAILED_TOTAL,
    QUEUE_TASKS_SUBMITTED_TOTAL,
    QUEUE_TASK_DURATION_SECONDS,
)


logger = logging.getLogger("pricebiz")


@dataclass
class QueueTask:
    name: str
    function: Callable[..., Awaitable[Any]]
    args: tuple
    kwargs: dict


class TaskQueue:
    def __init__(
        self,
        max_size: int = 1000,
        worker_count: int = 4,
    ):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.worker_count = worker_count
        self.workers: list[asyncio.Task] = []
        self.running = False

    async def start(self):
        if self.running:
            return

        self.running = True

        for worker_id in range(self.worker_count):
            worker = asyncio.create_task(
                self._worker(worker_id)
            )
            self.workers.append(worker)

        logger.info(
            "Task queue started | workers=%s max_size=%s",
            self.worker_count,
            self.queue.maxsize,
        )

    async def stop(self):
        if not self.running:
            return

        logger.info(
            "Waiting for queued tasks | queue_size=%s",
            self.queue.qsize(),
        )

        await self.queue.join()

        self.running = False

        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(
            *self.workers,
            return_exceptions=True,
        )

        self.workers.clear()

        QUEUE_SIZE.set(0)

        logger.info("Task queue stopped")

    async def submit(
        self,
        name: str,
        function: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ):
        if not self.running:
            raise RuntimeError("Task queue is not running")

        task = QueueTask(
            name=name,
            function=function,
            args=args,
            kwargs=kwargs,
        )

        await self.queue.put(task)

        QUEUE_SIZE.set(self.queue.qsize())

        QUEUE_TASKS_SUBMITTED_TOTAL.labels(
            task=name,
        ).inc()

        logger.info(
            "Task queued | task=%s queue_size=%s",
            name,
            self.queue.qsize(),
        )

    async def _worker(self, worker_id: int):
        logger.info(
            "Task queue worker started | worker=%s",
            worker_id,
        )

        while True:
            task = await self.queue.get()

            QUEUE_SIZE.set(self.queue.qsize())

            start_time = time.perf_counter()

            try:
                logger.info(
                    "Processing queued task | "
                    "worker=%s task=%s",
                    worker_id,
                    task.name,
                )

                await task.function(
                    *task.args,
                    **task.kwargs,
                )

                duration = time.perf_counter() - start_time

                QUEUE_TASKS_COMPLETED_TOTAL.labels(
                    task=task.name,
                ).inc()

                QUEUE_TASK_DURATION_SECONDS.labels(
                    task=task.name,
                ).observe(duration)

                logger.info(
                    "Queued task completed | "
                    "worker=%s task=%s duration=%.3fs",
                    worker_id,
                    task.name,
                    duration,
                )

            except asyncio.CancelledError:
                raise

            except Exception:
                duration = time.perf_counter() - start_time

                QUEUE_TASKS_FAILED_TOTAL.labels(
                    task=task.name,
                ).inc()

                QUEUE_TASK_DURATION_SECONDS.labels(
                    task=task.name,
                ).observe(duration)

                logger.exception(
                    "Queued task failed | "
                    "worker=%s task=%s duration=%.3fs",
                    worker_id,
                    task.name,
                    duration,
                )

            finally:
                self.queue.task_done()
                QUEUE_SIZE.set(self.queue.qsize())


task_queue = TaskQueue(
    max_size=1000,
    worker_count=4,
)