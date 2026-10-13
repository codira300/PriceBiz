from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any, Optional

from app.monitoring.metrics import (
    CACHE_HITS_TOTAL,
    CACHE_MISSES_TOTAL,
    CACHE_SIZE,
)


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(
        self,
        *,
        max_entries: int = 2048,
    ):
        self.max_entries = max_entries
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()

    def get(
        self,
        key: str,
    ) -> Optional[Any]:
        now = monotonic()

        with self._lock:
            entry = self._entries.get(key)

            if entry is None:
                CACHE_MISSES_TOTAL.labels(
                    namespace=self._namespace(key)
                ).inc()
                return None

            if entry.expires_at <= now:
                self._entries.pop(key, None)
                CACHE_SIZE.set(len(self._entries))

                CACHE_MISSES_TOTAL.labels(
                    namespace=self._namespace(key)
                ).inc()

                return None

            self._entries.move_to_end(key)

            CACHE_HITS_TOTAL.labels(
                namespace=self._namespace(key)
            ).inc()

            return deepcopy(entry.value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int,
    ):
        if ttl <= 0:
            return

        expires_at = monotonic() + ttl

        with self._lock:
            self._entries[key] = CacheEntry(
                value=deepcopy(value),
                expires_at=expires_at,
            )

            self._entries.move_to_end(key)

            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)

            CACHE_SIZE.set(len(self._entries))

    def delete(
        self,
        key: str,
    ):
        with self._lock:
            self._entries.pop(key, None)
            CACHE_SIZE.set(len(self._entries))

    def delete_prefix(
        self,
        prefix: str,
    ):
        with self._lock:
            keys_to_delete = [
                key
                for key in self._entries
                if key.startswith(prefix)
            ]

            for key in keys_to_delete:
                self._entries.pop(key, None)

            CACHE_SIZE.set(len(self._entries))

    def clear(self):
        with self._lock:
            self._entries.clear()
            CACHE_SIZE.set(0)

    @staticmethod
    def _namespace(key: str) -> str:
        return key.split(":", 1)[0]


cache = TTLCache(
    max_entries=2048,
)