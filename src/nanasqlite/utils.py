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
            # List of (key, expiry_at_detection_time) pairs for CAS eviction
            expired_keys: list[tuple[str, float]] = []

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
                            # Record the expiry timestamp seen at detection time
                            # for the Compare-and-Delete check in _evict.
                            expired_keys.append((key, expiry))
                        else:
                            break
                    if expired_keys:
                        sleep_time = 0
                    else:
                        first_expiry = next(iter(self._exptimes.values()))
                        sleep_time = min(first_expiry - now, 1.0)

            for key, expected_expiry in expired_keys:
                self._evict(key, expected_expiry)

            if sleep_time > 0:
                self._stop_event.wait(timeout=sleep_time)

    def _evict(self, key: str, expected_expiry: float | None = None) -> None:
        """Evict an item and trigger callback.

        Uses a Compare-and-Delete pattern: if ``expected_expiry`` is supplied
        (as recorded by the scheduler at detection time), eviction is skipped
        when the key's current expiry timestamp differs — indicating the key
        was refreshed by a concurrent write between detection and eviction.
        This eliminates the F-005 race condition where a scheduler-identified
        expired key is deleted after being legitimately updated.

        IMPORTANT: The on_expire callback is invoked OUTSIDE self._lock
        to prevent cross-lock deadlocks when the callback acquires
        an external lock (e.g. NanaSQLite._lock).
        """
        callback_args: tuple[str, Any] | None = None
        with self._lock:
            if key in self._data:
                current_expiry = self._exptimes.get(key)
                # F-005 fix: CAS check — skip eviction if the key has been
                # refreshed (new expiry differs from the one seen at detection).
                if expected_expiry is not None and current_expiry != expected_expiry:
                    logger.debug(
                        "Key '%s' skipped eviction: expiry updated (was %.3f, now %s).",
                        key, expected_expiry, current_expiry,
                    )
                else:
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
        # PERF-11: Optimistic lock-free pre-check before acquiring the lock.
        # Individual dict.get() is atomic under CPython's GIL, so reading
        # _exptimes without the lock is safe.  The common case for a
        # non-expired key avoids the RLock acquire/release overhead entirely.
        expiry = self._exptimes.get(key)
        if expiry is None:
            return False  # Key is not tracked; treat as not expired.
        now = time.time()
        if expiry > now:
            return False  # Still valid — fast path, no lock needed.

        # Key might be expired.  Do the full check under the lock.
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
                # PERF-B: Only call _cancel_timer in TIMER mode; in SCHEDULER mode
                # _timers/_async_tasks are always empty so the call is pure overhead.
                if self._mode == ExpirationMode.TIMER:
                    self._cancel_timer(key)
                del self._data[key]
                del self._exptimes[key]

            self._data[key] = value
            self._exptimes[key] = expiry

            if self._mode == ExpirationMode.TIMER:
                self._set_timer(key)

    def _set_timer(self, key: str) -> None:
        """Set individual timer (TIMER mode)."""
        # Capture expiry at scheduling time for the CAS check in _evict.
        # If the key is updated before the timer fires, the new __setitem__
        # call will cancel this timer and schedule a fresh one with a new expiry,
        # so the CAS check here is a safety belt for edge cases.
        expected_expiry = self._exptimes.get(key)
        try:
            loop = asyncio.get_running_loop()
            task = loop.call_later(self._expiration_time, self._evict, key, expected_expiry)
            self._async_tasks[key] = task  # type: ignore
        except RuntimeError:
            timer = threading.Timer(self._expiration_time, self._evict, args=(key, expected_expiry))
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
        # BUG-04 fix: check expiry and read value atomically under the same lock.
        # Previously _check_expiry() ran outside the lock, so a concurrent
        # scheduler eviction between the check and the dict read caused a spurious
        # KeyError for a key that was still valid at call time.
        callback_args: tuple[str, Any] | None = None
        key_expired = False
        result: Any = None  # initialized here to satisfy static analysis
        with self._lock:
            if key in self._exptimes and self._exptimes[key] <= time.time():
                key_expired = True
                value = self._data.pop(key, None)
                self._exptimes.pop(key, None)
                if value is not None and self._on_expire:
                    callback_args = (key, value)
            else:
                result = self._data[key]  # may raise KeyError if absent

        # Fire callback OUTSIDE the lock to prevent cross-lock deadlock
        if callback_args is not None and self._on_expire is not None:
            try:
                self._on_expire(*callback_args)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in ExpiringDict on_expire callback for key '%s': %s", key, e)

        if key_expired:
            raise KeyError(key)
        return result

    def __delitem__(self, key: str) -> None:
        with self._lock:
            # PERF-B / BUG-01: Only call _cancel_timer in TIMER mode;
            # in SCHEDULER/LAZY mode _timers/_async_tasks are always empty
            # so the call is pure overhead (mirrors the guard in __setitem__).
            if self._mode == ExpirationMode.TIMER:
                self._cancel_timer(key)
            if key in self._data:
                del self._data[key]
                del self._exptimes[key]

    def __iter__(self) -> Iterator[str]:
        # PERF-01: collect all expired keys in a single lock acquisition instead
        # of calling _check_expiry() (which re-acquires the lock) per key.
        now = time.time()
        expired_callbacks: list[tuple[str, Any]] = []
        with self._lock:
            live_keys: list[str] = []
            for key in list(self._data):
                if key in self._exptimes and self._exptimes[key] <= now:
                    value = self._data.pop(key, None)
                    self._exptimes.pop(key, None)
                    if self._on_expire:
                        expired_callbacks.append((key, value))
                else:
                    live_keys.append(key)
        # Fire callbacks outside the lock to prevent cross-lock deadlock.
        for key, value in expired_callbacks:
            try:
                self._on_expire(key, value)  # type: ignore[misc]
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in ExpiringDict on_expire callback for key '%s': %s", key, e)
        yield from live_keys

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
            # Use tuple() to create a copy of keys for safe iteration while modifying the original dict
            for key in tuple(self._timers):
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
                    logger.warning(
                        "ExpiringDict scheduler thread did not exit within timeout; it will continue as daemon."
                    )
        self._scheduler_thread = None
        # BUG-02 fix: restart the scheduler so future insertions are evicted.
        # Without this, clear() permanently kills the background thread and new
        # items added after clear() are never expired.
        if self._mode == ExpirationMode.SCHEDULER:
            self._stop_event.clear()
            self._start_scheduler()

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
