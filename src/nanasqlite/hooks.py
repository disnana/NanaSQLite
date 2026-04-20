from __future__ import annotations

import logging
import re
import warnings
import weakref
from collections.abc import Hashable
from re import Pattern
from typing import Any, Callable

from .compat import HAS_RE2, HAS_VALIDKIT, re2_module
from .exceptions import NanaSQLiteValidationError

_logger = logging.getLogger(__name__)


class BaseHook:
    """Base class providing default pass-through implementations for NanaHook.
    Supports filtering by key_pattern (regex) or key_filter (callable).

    When google-re2 is installed (``pip install nanasqlite[re2]``), the RE2
    engine is used for all regex compilation and matching.  RE2 guarantees
    linear-time execution for any input, eliminating the risk of ReDoS attacks.
    A ``logging.debug`` message is emitted at module import time when RE2 is
    active (see ``nanasqlite.compat``).

    RE2 does not support some advanced regex features (backreferences such as
    ``(\\w)\\1``, and lookarounds such as ``(?=...)``).  When such a pattern is
    supplied and RE2 raises an error, the behaviour depends on *re_fallback*:

    - ``re_fallback=False`` (default): the ``re2.error`` propagates, failing
      fast and keeping full ReDoS protection.
    - ``re_fallback=True``: a :mod:`warnings` warning is emitted and the
      pattern is compiled with the standard ``re`` module instead.  ReDoS
      protection is disabled for that pattern.

    If *key_pattern* is a :class:`re.Pattern` compiled with flags that RE2
    cannot reproduce (e.g. ``re.VERBOSE``, ``re.LOCALE``, ``re.ASCII``), the
    behaviour is also controlled by *re_fallback*:

    - ``re_fallback=False`` (default): ``re.error`` is raised immediately.
    - ``re_fallback=True``: a warning is emitted and ``re.compile`` is used
      instead, preserving the original flags at the cost of ReDoS protection.
    """

    def __init__(
        self,
        key_pattern: str | Pattern | None = None,
        key_filter: Callable[[str], bool] | None = None,
        re_fallback: bool = False,
    ):
        # Validate regex patterns for ReDoS risk (skipped when RE2 is available
        # since RE2 guarantees linear-time complexity for all patterns).
        if HAS_RE2:
            # RE2 engine: linear time guaranteed, no ReDoS risk.
            if isinstance(key_pattern, str):
                self._key_regex = self._compile_re2(key_pattern, re_fallback)
            elif isinstance(key_pattern, Pattern):
                # Preserve the original flags (IGNORECASE, MULTILINE, etc.) when
                # re-compiling with RE2.  If RE2 does not support a given flag it
                # will raise re2.error, which is handled by the re_fallback logic.
                self._key_regex = self._compile_re2(
                    key_pattern.pattern, re_fallback, flags=key_pattern.flags
                )
            else:
                self._key_regex = key_pattern
        else:
            # 標準 re エンジン: ReDoS リスクを防ぐためパターンを検証する。
            if isinstance(key_pattern, str):
                self._validate_regex_pattern(key_pattern)
                self._key_regex = re.compile(key_pattern)
            elif isinstance(key_pattern, Pattern):
                # PERF-02: コンパイル済み Pattern を渡した場合、
                # 既コンパイル済みオブジェクトの再コンパイルは省略する。
                # ただし、コンパイル済み Pattern を経由して ReDoS ブラックリストを
                # バイパスできないよう、pattern.pattern（元のパターン文字列）に
                # 対しては必ずバリデーションを実行する（セキュリティ要件）。
                self._validate_regex_pattern(key_pattern.pattern)
                self._key_regex = key_pattern
            else:
                self._key_regex = key_pattern
        self._key_filter = key_filter

    def _compile_re2(self, pattern: str, re_fallback: bool, flags: int = 0) -> Any:
        """Compile *pattern* with RE2, falling back to ``re`` when *re_fallback* is True.

        RE2 rejects patterns that use features with super-linear worst-case
        complexity (e.g. backreferences, lookarounds).  When *re_fallback* is
        False (the default), the RE2 error propagates unchanged.  When True,
        a :mod:`warnings` warning is emitted and the pattern is compiled with
        the standard :mod:`re` engine instead.

        *flags* are translated to an ``re2.Options`` object so that modifiers
        such as ``re.IGNORECASE`` are preserved when re-compiling a
        ``re.Pattern`` with RE2.  In the fallback path ``re.compile`` receives
        the original *flags* integer unchanged.
        """
        # re2_module is guaranteed non-None here: _compile_re2 is only called
        # from within the `if HAS_RE2:` branch in __init__.

        # Build re2.Options from the flags only when non-trivial flags are
        # present. re.UNICODE (32) is Python-implicit and not meaningful for RE2.
        effective_flags = flags & ~re.UNICODE

        # Flags RE2 supports natively or matches by default:
        #   re.IGNORECASE → options.case_sensitive = False
        #   re.DOTALL     → options.dot_nl = True
        #   re.MULTILINE  → prepend (?m) to pattern; RE2 recognises this per-pattern
        #                   flag and makes ^ / $ match at line boundaries, which is
        #                   exactly Python's re.MULTILINE semantics.
        # Flags RE2 cannot reproduce (re.VERBOSE, re.LOCALE, re.ASCII, re.DEBUG, …)
        # would silently change matching semantics.  Detect them early and either
        # warn+fallback (re_fallback=True) or raise a clear error (re_fallback=False).
        _re2_compatible = re.IGNORECASE | re.DOTALL | re.MULTILINE
        unsupported = effective_flags & ~_re2_compatible
        if unsupported:
            unsupported_names = []
            for _name in ("VERBOSE", "LOCALE", "ASCII", "DEBUG", "TEMPLATE"):
                _val = getattr(re, _name, 0)
                if unsupported & _val:
                    unsupported_names.append(f"re.{_name}")
            unsupported_desc = (
                ", ".join(unsupported_names) if unsupported_names else hex(unsupported)
            )
            msg = (
                f"RE2 cannot preserve Python re flags ({unsupported_desc}) "
                f"for pattern {pattern!r}. "
                "Falling back to the standard re engine. "
                "ReDoS protection is disabled for this pattern."
            )
            if re_fallback:
                warnings.warn(msg, stacklevel=4)
                return re.compile(pattern, flags)
            raise re.error(
                f"RE2 does not support Python re flags ({unsupported_desc}) "
                f"for pattern {pattern!r}. "
                "Use re_fallback=True to fall back to the standard re engine "
                "(ReDoS protection will be disabled for this pattern)."
            )

        options: Any = None
        # Use a separate variable for the RE2 compile attempt so that the (?m)
        # prefix is never applied to ``pattern`` itself.  The original ``pattern``
        # is preserved for fallback re.compile() calls and warning/error messages.
        re2_pattern = pattern
        if effective_flags & _re2_compatible:
            # Translate MULTILINE to the per-pattern (?m) inline flag.
            # Apply only to the RE2-specific copy; do NOT mutate ``pattern``.
            if effective_flags & re.MULTILINE:
                re2_pattern = "(?m)" + pattern
            # Only instantiate Options when at least one Options-level flag is set.
            if effective_flags & (re.IGNORECASE | re.DOTALL):
                options = re2_module.Options()  # type: ignore[union-attr]
                if effective_flags & re.IGNORECASE:
                    options.case_sensitive = False
                if effective_flags & re.DOTALL:
                    options.dot_nl = True
            # re.MULTILINE: handled above via (?m) prefix; no Options attribute needed.

        try:
            return re2_module.compile(re2_pattern, options)  # type: ignore[union-attr]
        except re2_module.error as exc:  # type: ignore[union-attr]
            if re_fallback:
                warnings.warn(
                    f"RE2 cannot compile pattern {pattern!r}: {exc}. "
                    "Falling back to the standard re engine. "
                    "ReDoS protection is disabled for this pattern.",
                    # stacklevel 4: warnings.warn → _compile_re2 → __init__ → user code
                    stacklevel=4,
                )
                return re.compile(pattern, flags)
            raise

    def _validate_regex_pattern(self, pattern: str) -> None:
        """Validate regex patterns to prevent ReDoS attacks.

        This check is only performed when google-re2 is NOT available.
        When RE2 is active, all patterns are inherently safe (linear-time).
        """
        # Check for known dangerous patterns
        dangerous_patterns = [
            r'\([^)]*\+\)[*+]',     # (a+)+ or (a+)*
            r'\([^)]*\*\)[*+]',     # (a*)+ or (a*)*
            r'\([^|]*\|[^|]*\)\*',  # (a|b)*
            r'\([^|]*\|[^|]*\)\+',  # (a|b)+
        ]

        for dangerous in dangerous_patterns:
            if re.search(dangerous, pattern):
                raise NanaSQLiteValidationError(
                    f"Potentially dangerous regex pattern detected: {pattern}. "
                    "This pattern may cause ReDoS (Regular Expression Denial of Service) attacks. "
                    "Install google-re2 (pip install nanasqlite[re2]) for linear-time regex matching."
                )

    def _should_run(self, key: str) -> bool:
        """Determines if the hook should run for the given key."""
        if self._key_regex is not None and not self._key_regex.search(key):
            return False
        if self._key_filter is not None and not self._key_filter(key):
            return False
        return True

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        """Default passthrough for before_write.
        (書き込み前のデフォルトパススルー実装)
        """
        return value

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        """Default passthrough for after_read.
        (読み取り後のデフォルトパススルー実装)
        """
        return value

    def before_delete(self, db: Any, key: str) -> None:
        """Default implementation for before_delete. Does nothing.
        (削除前のデフォルト実装。何もしません)
        """
        pass


class CheckHook(BaseHook):
    """Simple check constraint."""

    def __init__(
        self,
        check_func: Callable[[str, Any], bool],
        error_msg: str = "Check constraint failed",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.check_func = check_func
        self.error_msg = error_msg

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        if not self.check_func(key, value):
            raise NanaSQLiteValidationError(self.error_msg)
        return value


class UniqueHook(BaseHook):
    """Ensures a specific field in a dictionary value is unique across the table.

    In non-v2 (synchronous) mode, the uniqueness check and the database write
    are executed inside the same RLock acquisition in NanaSQLite.__setitem__,
    eliminating the TOCTOU race condition (SEC-05 fix).

    In v2 (write-back cache) mode, the check is still performed before the
    asynchronous flush, so strict uniqueness is not guaranteed under high
    concurrency.  For production applications requiring strict uniqueness in v2
    mode, use SQLite UNIQUE constraints instead.

    This issue was tracked as SEC-03 in the v1.5.0 audit report and resolved
    as SEC-05 in v1.5.4.

    Performance note (PERF-01)
    --------------------------
    By default, each ``before_write`` call iterates over **all** existing rows
    via ``db.items()`` to check uniqueness — O(N) per write.  For large tables
    this becomes a significant bottleneck.

    Pass ``use_index=True`` to enable an opt-in inverse index that reduces
    uniqueness checks to **O(1)** after the first write:

    .. code-block:: python

        hook = UniqueHook("email", use_index=True)
        db.add_hook(hook)

    The index is built lazily on the first write (O(N) once) and kept
    up-to-date automatically through ``before_write`` and ``before_delete``
    callbacks.

    **Limitations of the inverse index:**

    * The index can become stale if the database is modified *outside* the hook
      lifecycle (e.g. via ``db.execute()``).  Call
      :meth:`invalidate_index` to force a rebuild after such changes.
    * The index is held in memory; very large tables will consume proportional
      memory (one entry per unique field value).
    * Callable ``field`` extractors are supported: the return value is used as
      the index key.
    """

    def __init__(self, field: str | Callable[[str, Any], Any], use_index: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.field = field
        self.use_index = use_index
        # 逆引きインデックス: {field_value → key_name}。use_index=True の場合のみ使用。
        # フィールド値をキーとするため、ハッシュ可能な値のみ格納可能。
        self._value_to_key: dict[Hashable, str] = {}
        # ライフサイクル外でのDB変更などで同一フィールド値を持つキーが複数存在する場合、
        # そのフィールド値を記録する。該当値については O(N) スキャンにフォールバックする。
        self._duplicate_field_values: set[Hashable] = set()
        self._index_built: bool = False
        # インデックスを構築した DB インスタンスへの弱参照。
        # 別の DB インスタンスで使用された場合に自動的に再構築するために使用する。
        self._bound_db_ref: weakref.ref[Any] | None = None

    def invalidate_index(self) -> None:
        """Force the inverse index to be rebuilt on the next write.

        Call this after modifying the database outside the hook lifecycle
        (e.g. via ``db.execute()``) to prevent stale index entries from
        hiding or falsely reporting duplicates.
        """
        self._index_built = False
        self._value_to_key.clear()
        self._duplicate_field_values.clear()
        self._bound_db_ref = None

    def _extract_field(self, key: str, value: Any) -> Any:
        """Return the uniqueness value for a (key, value) pair, or None."""
        if callable(self.field):
            return self.field(key, value)
        if isinstance(value, dict):
            return value.get(self.field)
        return None

    def _build_index(self, db: Any) -> None:
        """DB の全値から逆引きインデックスを構築する。初回のみ O(N)。

        フィールド値がアンハッシュ可能（dict/list など）の場合は
        そのエントリをインデックスに追加せずにスキップする。

        ライフサイクル外のDB変更などで重複が既に存在する場合は
        `_duplicate_field_values` に記録し、該当値の検証は O(N) スキャンに
        フォールバックする（インデックスの最初のキーのみ保持するより正確）。
        """
        self._value_to_key.clear()
        self._duplicate_field_values.clear()
        for k, v in db.items():
            val = self._extract_field(k, v)
            if val is None:
                continue
            try:
                if val in self._duplicate_field_values:
                    # すでに重複として記録済み - スキップ
                    pass
                elif val in self._value_to_key:
                    # 2つ目のキーが見つかった - 重複として記録しインデックスから除去
                    self._duplicate_field_values.add(val)
                    del self._value_to_key[val]
                else:
                    self._value_to_key[val] = k
            except TypeError:
                # アンハッシュ可能な値（dict, list など）はインデックス不可のためスキップ
                pass
        self._index_built = True
        # インデックスを構築した DB インスタンスへの弱参照を保存する。
        # 別の DB インスタンスで使用された場合に自動的に再構築するために使用する。
        self._bound_db_ref = weakref.ref(db)

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

        # 新しい値からユニーク性チェック用フィールド値を抽出する
        if callable(self.field):
            check_val = self.field(key, value)
        elif isinstance(value, dict) and self.field in value:
            check_val = value[self.field]
        else:
            check_val = None

        if self.use_index:
            # インデックスモード: O(N) の初回ビルド後は O(1) で検証
            # 別の DB インスタンスで使用された場合はインデックスを再構築する。
            if self._index_built and (
                self._bound_db_ref is None or self._bound_db_ref() is not db
            ):
                self.invalidate_index()
            if not self._index_built:
                self._build_index(db)

            # after_read フックをバイパスして生の旧値を取得する。
            # db.get() は after_read フックを適用するため、
            # PydanticHook 等が介在するとモデルオブジェクトが返り、
            # _extract_field() が None を返してインデックスエントリが残留する恐れがある。
            # 格納値としての None と「キーが存在しない」を区別するため sentinel を使用する。
            _missing = object()
            old_raw = db._get_raw(key, _missing)
            old_check_val = None
            old_check_val_hashable = False
            if old_raw is not _missing:
                old_check_val = self._extract_field(key, old_raw)
                try:
                    if old_check_val is not None:
                        hash(old_check_val)
                        old_check_val_hashable = True
                        # 旧インデックスの除去はまだ行わない。
                        # この後の重複チェックやバリデーションで例外が発生すると
                        # DB 書き込みは中止されるため、ここで _value_to_key を変更すると
                        # インデックスだけが壊れた状態になる。
                        # 実際の除去は、書き込み継続が確定した成功パスで行う。
                except TypeError:
                    # アンハッシュ可能な旧値はインデックスに存在しないためスキップ
                    pass

            if check_val is None:
                # 新しい値にユニーク性フィールドがない場合はインデックス登録をスキップ。
                # この分岐は成功パスでそのまま return するため、
                # ここで旧エントリを安全に除去できる。
                if old_check_val_hashable and old_check_val is not None:
                    _missing_index: object = object()
                    _removed_key = self._value_to_key.pop(old_check_val, _missing_index)
                    if _removed_key is not _missing_index and _removed_key != key:
                        self._value_to_key[old_check_val] = _removed_key  # type: ignore[index]
                    # _duplicate_field_values からは除去しない。
                    # 他のキーが同じ値を持っている可能性があるため、
                    # 重複の完全な解消は O(N) スキャン（is_known_duplicate パス）で確認する。
                return value

            # 重複チェック（同一キーの上書きは許可）
            # use_index=True で check_val がアンハッシュ可能な場合は設定エラーとして明示的に拒否する。
            # O(N) スキャンへのサイレントな縮退よりも、明確なエラーの方が望ましい。
            try:
                is_known_duplicate = check_val in self._duplicate_field_values
                existing_key = None if is_known_duplicate else self._value_to_key.get(check_val)
            except TypeError as exc:
                field_name = self.field.__name__ if callable(self.field) else str(self.field)
                raise NanaSQLiteValidationError(
                    f"UniqueHook: use_index=True requires hashable field values, "
                    f"but field '{field_name}' returned an unhashable value "
                    f"(type: {type(check_val).__name__}). "
                    f"Set use_index=False or use a field extractor that returns a hashable value."
                ) from exc

            # 既知の重複値に対しては O(N) スキャンにフォールバックして正確に検証
            if is_known_duplicate:
                for k, v in db.items():
                    if k == key:
                        continue
                    other_val = self._extract_field(k, v)
                    if other_val == check_val:
                        field_name = self.field.__name__ if callable(self.field) else str(self.field)
                        _logger.warning(
                            "Unique constraint violation for key '%s': field '%s' value already exists",
                            key,
                            field_name,
                        )
                        raise NanaSQLiteValidationError("Unique constraint violation: duplicate value detected")
                # 重複が解消された場合はインデックスに登録してセットから除去
                self._duplicate_field_values.discard(check_val)
                self._value_to_key[check_val] = key
                return value

            if existing_key is not None and existing_key != key:
                field_name = self.field.__name__ if callable(self.field) else str(self.field)
                _logger.warning(
                    "Unique constraint violation for key '%s': field '%s' value already exists",
                    key,
                    field_name,
                )
                raise NanaSQLiteValidationError("Unique constraint violation: duplicate value detected")

            # インデックスに新しいエントリを登録
            self._value_to_key[check_val] = key
        else:
            if check_val is None:
                return value
            # O(N) フルスキャン: use_index=False（デフォルト）時の元の動作
            for k, v in db.items():
                if k == key:
                    continue

                if callable(self.field):
                    other_val = self.field(k, v)
                elif isinstance(v, dict):
                    other_val = v.get(self.field)
                else:
                    other_val = None

                if other_val == check_val:
                    field_name = self.field.__name__ if callable(self.field) else str(self.field)
                    _logger.warning(
                        "Unique constraint violation for key '%s': field '%s' value already exists",
                        key,
                        field_name,
                    )
                    raise NanaSQLiteValidationError("Unique constraint violation: duplicate value detected")
        return value

    def before_delete(self, db: Any, key: str) -> None:
        """キー削除時に逆引きインデックスを最新状態に保つ。"""
        if not self.use_index or not self._index_built:
            return
        # 別の DB インスタンスで使用された場合はインデックスを無効化して早期リターン。
        # インデックスは次回の before_write で正しい DB から再構築される。
        if self._bound_db_ref is None or self._bound_db_ref() is not db:
            self.invalidate_index()
            return
        if not self._should_run(key):
            return
        # after_read フックをバイパスして生の格納値を取得する。
        # 格納値としての None と「キーが存在しない」を区別するため sentinel を使用する。
        _missing = object()
        value = db._get_raw(key, _missing)
        if value is not _missing:
            check_val = self._extract_field(key, value)
            try:
                if check_val is not None:
                    # 非アトミックな get()+del は v2 モードでフック呼び出しが
                    # インターリーブすると KeyError を引き起こす可能性がある。
                    # pop() で安全に除去し、このキーが所有していなかった場合は復元する。
                    _missing_index_del: object = object()
                    _removed_del = self._value_to_key.pop(check_val, _missing_index_del)
                    if _removed_del is not _missing_index_del and _removed_del != key:
                        self._value_to_key[check_val] = _removed_del  # type: ignore[index]
                    # _duplicate_field_values に含まれる値については除去しない。
                    # 他のキーがまだ同じ値を持っている可能性があるため、
                    # O(N) スキャンフォールバックの状態を維持する。
                    # 重複が本当に解消されたかどうかは次回の before_write で確認する。
            except TypeError:
                # アンハッシュ可能な値はインデックスに存在しないためスキップ
                pass


class ForeignKeyHook(BaseHook):
    """Ensures a specific field refers to an existing key in a target table.

    WARNING: This implementation has a known TOCTOU race condition where the
    referenced key can be deleted between the constraint check and write operation.

    For production applications requiring strict referential integrity:
    1. Use SQLite FOREIGN KEY constraints with PRAGMA foreign_keys=ON
    2. Use single-threaded access patterns
    3. Implement application-level locking around related operations

    This issue is tracked as SEC-04 in the v1.5.0 audit report.
    """

    def __init__(self, field: str | Callable[[str, Any], Any], target_db: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.field = field
        self.target_db = target_db

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

        if callable(self.field):
            ref_key = self.field(key, value)
        elif isinstance(value, dict) and self.field in value:
            ref_key = value[self.field]
        else:
            return value

        if ref_key is not None and ref_key not in self.target_db:
            field_name = self.field.__name__ if callable(self.field) else str(self.field)
            _logger.warning(
                "Foreign key constraint violation for key '%s': field '%s' references non-existent key",
                key,
                field_name,
            )
            raise NanaSQLiteValidationError("Foreign key constraint violation: referenced key not found")
        return value


class ValidkitHook(BaseHook):
    """Integration with validkit-py for schema validation."""

    _is_validkit_hook = True

    def __init__(self, schema: Any, coerce: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.schema = schema
        self.coerce = coerce

        if not HAS_VALIDKIT:
            raise ImportError(
                "The 'validkit-py' library is required for validation. "
                "Install it with: pip install nanasqlite[validation]"
            )
        from .compat import validkit_validate

        self._validate_func = validkit_validate

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        try:
            if self.coerce:
                return self._validate_func(value, self.schema)
            else:
                self._validate_func(value, self.schema)
                return value
        except Exception as exc:
            if isinstance(exc, (MemoryError, OSError)):
                raise
            _logger.error("Schema validation failed for key '%s': %s", key, exc)
            raise NanaSQLiteValidationError("Schema validation failed") from exc


class PydanticHook(BaseHook):
    """Automatic cast to/from a Pydantic model for seamless integration."""

    def __init__(self, model_class: type, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = model_class

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

        if isinstance(value, self.model_class):
            if hasattr(value, "model_dump"):
                return value.model_dump()
            elif hasattr(value, "dict"):
                return value.dict()

        try:
            if hasattr(self.model_class, "model_validate"):
                model = self.model_class.model_validate(value)
                return model.model_dump()
            elif hasattr(self.model_class, "parse_obj"):
                model = self.model_class.parse_obj(value)
                return model.dict()
            return value
        except (ValueError, TypeError, AttributeError) as exc:
            _logger.error("Pydantic validation failed for key '%s': %s", key, exc)
            raise NanaSQLiteValidationError("Model validation failed") from exc

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        try:
            if hasattr(self.model_class, "model_validate"):
                return self.model_class.model_validate(value)
            elif hasattr(self.model_class, "parse_obj"):
                return self.model_class.parse_obj(value)
        except (ValueError, TypeError, AttributeError) as e:
            # Only suppress Pydantic validation errors, not system errors
            _logger.debug("Pydantic model validation failed for key '%s': %s", key, e)
        # Don't suppress ConnectionError, MemoryError, OSError, etc.
        return value
