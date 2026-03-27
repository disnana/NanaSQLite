"""
Compatibility layer for optional dependencies and internal shims.
(オプションの依存関係と内部シムのための互換性レイヤー)
"""

import logging
import re

logger = logging.getLogger(__name__)

# Optional validkit-py
try:
    import validkit  # noqa: F401
    HAS_VALIDKIT = True
    from validkit import validate as validkit_validate  # noqa: F401
except ImportError:
    HAS_VALIDKIT = False
    validkit_validate = None  # type: ignore

# Optional orjson
try:
    import orjson  # noqa: F401
    HAS_ORJSON = True
except ImportError:
    orjson = None  # type: ignore
    HAS_ORJSON = False

# Identifier pattern
IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_]\w*$")

# Sentinel for unset parameters
_UNSET = ...
