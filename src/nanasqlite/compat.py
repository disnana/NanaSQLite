"""
Compatibility layer for optional dependencies and internal shims.
(オプションの依存関係と内部シムのための互換性レイヤー)
"""

from __future__ import annotations

import logging
import re
import sys
import types
from typing import Any, Optional

logger = logging.getLogger(__name__)

# EllipsisType compatibility (Python 3.10+)
if sys.version_info >= (3, 10):
    from types import EllipsisType
else:
    EllipsisType = Any  # type: ignore

# Optional validkit-py
try:
    import validkit  # noqa: F401

    HAS_VALIDKIT = True
    from validkit import validate as validkit_validate  # noqa: F401
except ImportError:
    HAS_VALIDKIT = False

    def validkit_validate(*args: Any, **kwargs: Any) -> None:  # type: ignore[misc]
        """Stub raised when validkit-py is not installed."""
        raise ImportError(
            "validkit-py is not installed. "
            "Install it with: pip install nanasqlite[validation]"
        )

# Optional orjson
try:
    import orjson  # noqa: F401

    HAS_ORJSON = True
except ImportError:
    orjson = None  # type: ignore
    HAS_ORJSON = False

# Optional google-re2 (linear-time regex engine, prevents ReDoS)
# Install with: pip install nanasqlite[re2]
# QUAL-01: try/except の前に宣言することで、どちらのブランチでも型が正しく追跡される。
re2_module: types.Optional[types.ModuleType] = None
try:
    import re2 as _re2_module  # type: ignore[import-untyped]

    HAS_RE2 = True
    re2_module = _re2_module
    logger.debug(
        "NanaSQLite: google-re2 is available. "
        "Regex operations in hooks will use the RE2 engine (linear-time complexity, ReDoS-safe)."
    )
except ImportError:
    HAS_RE2 = False

# Identifier pattern
IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_]\w*$")

# Sentinel for unset parameters
_UNSET = ...  # noqa: F401
