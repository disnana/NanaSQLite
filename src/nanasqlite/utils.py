"""
Utility module for NanaSQLite: Provides ExpiringDict and other helper classes.
(NanaSQLite用ユーティリティモジュール: 有効期限付き辞書やその他の補助クラスを提供)
"""

from __future__ import annotations

import asyncio
import collections.abc
import logging
import threading
import time
from collections.abc import Iterator
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ExpirationMode(str, Enum):
    """
    Modes for detecting and handling expired items.
    (有効期限切れの検知と処理モード)
    """

    LAZY = "lazy"  # Check on access only (アクセ時にのみチェック)
    SCHEDULER = "scheduler"  # Single background worker (単一のバックグラウンドワーカー)
    TIMER = "timer"  # Individual timers for each key (キーごとの個別タイマー)


class ExpiringDict(collections.abc.MutableMapping):
    """
    A dictionary-like object where keys expire after a set time.
    Supports multiple expiration modes for different scales and precision requirements.
    (キーが一定時間後に失効する辞書型オブジェクト。規模や精度に応じて複数の失効モードをサポート)
    """

    def __init__(
        self,
        expiration_time: float,
        mode: ExpirationMode = ExpirationMode.SCHEDULER,
        on_expire: Callable[[str, Any], None] | None = None,
    ):
        """
        Args:
            expiration_time: Time in seconds before a key expires. (失効までの時間（秒）)
            mode: Expiration detection mode. (失効検知モード)
            on_expire: Callback function called when an item expires. (失効時に呼ばれるコールバック)
        """
        self._data: dict[str, Any] = {}
        self._exptimes: dict[str, float] = {}  # key -> expiry (Unix timestamp)
        self._expiration_time = expiration_time
        self._mode = mode
        self._on_expire = on_expire

        # Mode specific structures
        self._timers: dict[str, threading.Timer] = {}
        self._async_tasks: dict[str, asyncio.Task] = {}
        self._scheduler_thread: threading.Thread | None = None
        self._scheduler_running = False
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        if self._mode == ExpirationMode.SCHEDULER:
            self._start_scheduler()

    def _start_scheduler(self) -> None:
        """Start the background scheduler thread if not already running."""
        with self._lock:
            if self._scheduler_running:
                return
            self._scheduler_running = True
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._scheduler_thread.start()

    def _scheduler_loop(self) -> None:
        """Single background worker loop to evict expired items."""
        while self._scheduler_running:
            now = time.time()
            expired_keys = []

            with self._lock:
                # _exptimes is insertion-ordered (oldest first) because
                # __setitem__ deletes+re-adds on update.  Walk from the
                # front and stop at the first non-expired key — O(k)
                # where k = number of expired entries, not O(n).
                if not self._exptimes:
                    sleep_time = 1.0
                else:
                    for key, expiry in self._exptimes.items():
                        if expiry <= now:
                            expired_keys.append(key)
                        else:
                            break
                    if expired_keys:
                        sleep_time = 0
                    else:
                        first_expiry = next(iter(self._exptimes.values()))
                        sleep_time = min(first_expiry - now, 1.0)

            for key in expired_keys:
                self._evict(key)

            if sleep_time > 0:
                self._stop_event.wait(timeout=sleep_time)

    def _evict(self, key: str) -> None:
        """Evict an item and trigger callback.

        IMPORTANT: The on_expire callback is invoked OUTSIDE self._lock
        to prevent cross-lock deadlocks when the callback acquires
        an external lock (e.g. NanaSQLite._lock).
        """
        callback_args: tuple[str, Any] | None = None
        with self._lock:
            if key in self._data:
                value = self._data.pop(key)
                self._exptimes.pop(key, None)
                if self._on_expire:
                    callback_args = (key, value)
                logger.debug("Key '%s' expired and removed.", key)

        # Fire callback outside lock to prevent deadlock
        if callback_args is not None and self._on_expire is not None:
            try:
                self._on_expire(*callback_args)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in ExpiringDict on_expire callback for key '%s': %s", callback_args[0], e)

    def _check_expiry(self, key: str) -> bool:
        """Check if a key is expired and remove it if it is (Lazy eviction)."""
        now = time.time()
        callback_args: tuple[str, Any] | None = None
        expired = False
        with self._lock:
            if key in self._exptimes and self._exptimes[key] <= now:
                expired = True
                if key in self._data:
                    value = self._data.pop(key)
                    self._exptimes.pop(key, None)
                    if self._on_expire:
                        callback_args = (key, value)
                    logger.debug("Key '%s' expired and removed.", key)
                else:
                    self._exptimes.pop(key, None)

        # Fire callback OUTSIDE the lock to prevent cross-lock deadlock
        if callback_args is not None and self._on_expire is not None:
            try:
                self._on_expire(*callback_args)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in ExpiringDict on_expire callback for key '%s': %s", callback_args[0], e)
        return expired


    def __setitem__(self, key: str, value: Any) -> None:
        expiry = time.time() + self._expiration_time
        with self._lock:
            # If item already exists, remove it first to maintain insertion order (for FIFO/Scheduler)
            if key in self._data:
                self._cancel_timer(key)
                del self._data[key]
                del self._exptimes[key]

            self._data[key] = value
            self._exptimes[key] = expiry

            if self._mode == ExpirationMode.TIMER:
                self._set_timer(key)

    def _set_timer(self, key: str) -> None:
        """Set individual timer (TIMER mode)."""
        # Try to use current event loop if available, else use threading.Timer
        try:
            loop = asyncio.get_running_loop()
            task = loop.call_later(self._expiration_time, self._evict, key)
            self._async_tasks[key] = task  # type: ignore
        except RuntimeError:
            timer = threading.Timer(self._expiration_time, self._evict, args=(key,))
            timer.daemon = True
            timer.start()
            self._timers[key] = timer

    def _cancel_timer(self, key: str) -> None:
        """Cancel individual timer (TIMER mode)."""
        if key in self._timers:
            self._timers[key].cancel()
            del self._timers[key]
        if key in self._async_tasks:
            self._async_tasks[key].cancel()
            del self._async_tasks[key]

    def __getitem__(self, key: str) -> Any:
        self._check_expiry(key)
        with self._lock:
            return self._data[key]

    def __delitem__(self, key: str) -> None:
        with self._lock:
            self._cancel_timer(key)
            if key in self._data:
                del self._data[key]
                del self._exptimes[key]

    def __iter__(self) -> Iterator[str]:
        # Clean up expired items during iteration to stay accurate
        keys = list(self._data)
        for key in keys:
            if not self._check_expiry(key):
                yield key

    def __len__(self) -> int:
        # Note: could be inaccurate if items expired but not yet evicted
        # But for performance we return current size.
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return not self._check_expiry(key) and key in self._data

    def set_on_expire_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Update the expiration callback."""
        self._on_expire = callback

    def clear(self) -> None:
        with self._lock:
            for key in list(self._timers):
                self._cancel_timer(key)
            self._data.clear()
            self._exptimes.clear()
            self._scheduler_running = False
            self._stop_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            # Ensure it's not the current thread trying to join itself
            if self._scheduler_thread is not threading.current_thread():
                self._scheduler_thread.join(timeout=2.0)
                if self._scheduler_thread.is_alive():
                    logger.warning("ExpiringDict scheduler thread did not exit within timeout; it will continue as daemon.")
        self._scheduler_thread = None

    def __del__(self):
        try:
            self._scheduler_running = False
            self._stop_event.set()
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                if self._scheduler_thread is not threading.current_thread():
                    self._scheduler_thread.join(timeout=1.0)
            self._scheduler_thread = None
        except Exception:  # pylint: disable=broad-exception-caught
            # Cleanup at exit/garbage collection is best-effort and should not raise during interpreter shutdown
            pass  # nosec B110
