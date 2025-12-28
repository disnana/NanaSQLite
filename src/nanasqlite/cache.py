from __future__ import annotations

import logging
from abc import abstractmethod
from collections import OrderedDict
from collections.abc import MutableMapping
from enum import Enum
from typing import Any, Callable, Protocol

logger = logging.getLogger(__name__)

# Try to import C-optimized LRU (optional dependency)
_FAST_LRU: Any = None
try:
    from lru import LRU

    _FAST_LRU = LRU
    HAS_FAST_LRU = True
except ImportError:
    HAS_FAST_LRU = False


class CacheType(str, Enum):
    """Available cache strategies"""

    UNBOUNDED = "unbounded"
    LRU = "lru"
    TTL = "ttl"


class CacheStrategy(Protocol):
    """Protocol defining the interface for all cache implementations"""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get item from cache. Returns None if not found."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove item from cache."""
        pass

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Completely remove key from cache knowledge (forget it exists or not)."""
        pass

    @abstractmethod
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def mark_cached(self, key: str) -> None:
        """Mark a key as 'known' (cached) even if value is not loaded yet."""
        pass

    @abstractmethod
    def is_cached(self, key: str) -> bool:
        """Check if we have knowledge about this key (either value or existence)."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear entire cache."""
        pass

    @abstractmethod
    def get_data(self) -> MutableMapping[str, Any]:
        """Return reference to internal data storage (for legacy compatibility/inspection)."""
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        """Current number of items in cache."""
        pass


class UnboundedCache(CacheStrategy):
    """
    Default behavior: Infinite growth, maximum speed.
    Equivalent to v1.2.x logic using standard user Dict + Set.
    If max_size is set, uses FIFO eviction.
    """

    def __init__(self, max_size: int | None = None):
        self._max_size = max_size
        self._data: dict[str, Any] = {}
        self._cached_keys: set[str] = set()

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        if self._max_size and self._max_size > 0:
            if key not in self._data and len(self._data) >= self._max_size:
                # FIFO:最初に追加された要素を削除 (Python 3.7+)
                oldest_key = next(iter(self._data))
                del self._data[oldest_key]
                self._cached_keys.discard(oldest_key)

        self._data[key] = value
        self._cached_keys.add(key)

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        self._cached_keys.add(key)

    def invalidate(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        self._cached_keys.discard(key)

    def contains(self, key: str) -> bool:
        return key in self._data

    def mark_cached(self, key: str) -> None:
        self._cached_keys.add(key)

    def is_cached(self, key: str) -> bool:
        return key in self._cached_keys

    def clear(self) -> None:
        self._data.clear()
        self._cached_keys.clear()

    def get_data(self) -> MutableMapping[str, Any]:
        return self._data

    @property
    def size(self) -> int:
        return len(self._data)


class StdLRUCache(CacheStrategy):
    """
    Standard Library LRU implementation using OrderedDict.
    Safe fallback if C extensions are not available.
    """

    def __init__(self, max_size: int):
        self._max_size = max_size
        self._data: OrderedDict[str, Any] = OrderedDict()
        # For LRU, is_cached logic is unified with containment.
        # If it's evicted, it's no longer "cached", so we must fetch again.

    def get(self, key: str) -> Any | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)  # Mark used
        return self._data[key]

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self._max_size:
            self._data.popitem(last=False)  # Evict oldest

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def invalidate(self, key: str) -> None:
        self.delete(key)

    def contains(self, key: str) -> bool:
        return key in self._data

    def mark_cached(self, key: str) -> None:
        # In strict LRU, we can't just "mark" likely.
        # But to support the logic of "key is known to exist",
        # we might need to store it. For now, we only store actual values.
        pass

    def is_cached(self, key: str) -> bool:
        # In LRU mode, if it's in the map, it's cached.
        # If it's not, we consider it "not cached" (needs DB fetch)
        return key in self._data

    def clear(self) -> None:
        self._data.clear()

    def get_data(self) -> MutableMapping[str, Any]:
        return self._data

    @property
    def size(self) -> int:
        return len(self._data)


class FastLRUCache(CacheStrategy):
    """
    High-performance LRU implementation using lru-dict (C extension).
    """

    def __init__(self, max_size: int):
        if not HAS_FAST_LRU or _FAST_LRU is None:
            raise ImportError("lru-dict is not installed. Use 'fast_lru' extra or fallback to StdLRUCache.")
        self._data = _FAST_LRU(max_size)

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def invalidate(self, key: str) -> None:
        self.delete(key)

    def contains(self, key: str) -> bool:
        return key in self._data

    def mark_cached(self, key: str) -> None:
        pass

    def is_cached(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data.clear()

    def get_data(self) -> MutableMapping[str, Any]:
        # lru-dict behaves like a dict
        return self._data  # type: ignore

    @property
    def size(self) -> int:
        return len(self._data)


class TTLCache(CacheStrategy):
    """
    有効期限付きキャッシュ (TTL)
    """

    def __init__(
        self,
        ttl: float,
        max_size: int | None = None,
        on_expire: Callable[[str, Any], None] | None = None,
    ):
        """
        Args:
            ttl: 有効期限（秒）
            max_size: 最大保持件数 (FIFO併用、None の場合は無制限)
            on_expire: 有効期限切れ時のコールバック
        """
        from .utils import ExpiringDict

        self._data = ExpiringDict(expiration_time=ttl, on_expire=on_expire)
        self._max_size = max_size
        self._cached_keys: set[str] = set()

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        if self._max_size and self._max_size > 0:
            if key not in self._data and len(self._data) >= self._max_size:
                oldest_key = next(iter(self._data))
                del self._data[oldest_key]
                self._cached_keys.discard(oldest_key)

        self._data[key] = value
        self._cached_keys.add(key)

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        self._cached_keys.discard(key)

    def clear(self) -> None:
        self._data.clear()
        self._cached_keys.clear()

    def mark_cached(self, key: str) -> None:
        self._cached_keys.add(key)

    def is_cached(self, key: str) -> bool:
        return key in self._data or key in self._cached_keys

    def invalidate(self, key: str) -> None:
        self.delete(key)

    def contains(self, key: str) -> bool:
        return key in self._data

    @property
    def size(self) -> int:
        return len(self._data)

    def get_data(self) -> MutableMapping[str, Any]:
        return self._data


def create_cache(
    strategy: str | CacheType = CacheType.UNBOUNDED,
    size: int | None = None,
    ttl: float | None = None,
    on_expire: Callable[[str, Any], None] | None = None,
) -> CacheStrategy:
    """Factory to create appropriate cache instance"""
    # Normalize strategy
    if isinstance(strategy, CacheType):
        strategy = strategy.value

    if strategy == CacheType.LRU:
        if size is None or size <= 0:
            raise ValueError("cache_size must be a positive integer when using LRU strategy")

        if HAS_FAST_LRU:
            logger.info(f"Using FastLRUCache (lru-dict) with size {size}")
            return FastLRUCache(size)
        else:
            logger.warning(f"lru-dict not found. Falling back to standard LRUCache (OrderedDict) with size {size}")
            return StdLRUCache(size)

    if strategy == CacheType.TTL:
        if ttl is None or ttl <= 0:
            raise ValueError("cache_ttl must be a positive value when using TTL strategy")
        return TTLCache(ttl, max_size=size, on_expire=on_expire)

    return UnboundedCache(max_size=size)
