"""Focused executable specifications for deterministic v1.6 behavior.

This module is loaded only by the dedicated ``pytest --niltest`` CI job.
Production modules never import niltest.
"""

from typing import Any

from niltest import case, docs, scenario

from nanasqlite.core import _apply_increment_value, _apply_shallow_patch, _integrity_check_ok


@scenario("SQLite integrity result")
@docs(
    case("single ok row", given={"messages": ["ok"]}, returns=True),
    case("reported corruption", given={"messages": ["page 2 is corrupt"]}, returns=False),
    case("empty result is not success", given={"messages": []}, returns=False),
)
def integrity_result(messages: list[str]) -> bool:
    return _integrity_check_ok([(message,) for message in messages])


@scenario("Atomic scalar increment calculation")
@docs(
    case("positive increment", given={"current": 2, "amount": 3}, returns=5),
    case("negative increment", given={"current": 2, "amount": -1}, returns=1),
    case("bool is rejected", given={"current": True, "amount": 1}, raises=Exception),
)
def scalar_increment(current: Any, amount: int) -> int:
    return _apply_increment_value(current, amount, field=None, default=None)


@scenario("Shallow patch calculation")
@docs(
    case(
        "new top-level keys are merged",
        given={"current": {"name": "Nana"}, "changes": {"active": True}},
        returns={"name": "Nana", "active": True},
    ),
    case(
        "nested values are replaced, not recursively merged",
        given={"current": {"nested": {"a": 1}}, "changes": {"nested": {"b": 2}}},
        returns={"nested": {"b": 2}},
    ),
)
def shallow_patch(current: dict, changes: dict) -> dict:
    return _apply_shallow_patch(current, changes, create=False)
