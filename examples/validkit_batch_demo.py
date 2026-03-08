#!/usr/bin/env python3
"""
Validkit Integration with Batch Operations Example

This example demonstrates how to use validkit-py validation with
batch_update() and batch_update_partial() for different use cases.
"""

import os
import sys
import tempfile


class _MissingValidationError(Exception):
    """Fallback exception type used only when validation extras are unavailable."""

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if os.path.isdir(os.path.join(SRC_DIR, "nanasqlite")) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from validkit import v

    from nanasqlite import NanaSQLite, NanaSQLiteValidationError
    HAS_VALIDKIT = True
except ImportError:
    v = None  # type: ignore[assignment]
    NanaSQLite = None  # type: ignore[assignment]
    NanaSQLiteValidationError = _MissingValidationError  # type: ignore[assignment]
    HAS_VALIDKIT = False
    print("⚠️  validkit-py not installed. Install with: pip install nanasqlite[validation]")
    sys.exit(1)


def _db_path(tmpdir: str, name: str) -> str:
    return os.path.join(tmpdir, name)


def demo_batch_update_atomic(tmpdir: str):
    """
    batch_update() はアトミック動作：全件成功か全件失敗のどちらか
    """
    print("\n=== Demo 1: batch_update() - Atomic Behavior ===")

    schema = {
        "name": v.str(),
        "age": v.int(),
    }

    db = NanaSQLite(  # pylint: disable=unexpected-keyword-arg
        _db_path(tmpdir, "validkit_demo_atomic.db"),
        validator=schema,
    )

    try:
        # すべて正常なデータ
        print("\n1. All valid data:")
        db.batch_update({
            "user1": {"name": "Alice", "age": 25},
            "user2": {"name": "Bob", "age": 30},
            "user3": {"name": "Charlie", "age": 35},
        })
        print(f"✓ Successfully saved {len(db)} users")
        for key in ["user1", "user2", "user3"]:
            print(f"  - {key}: {db[key]}")

        # 1件でも不正なデータが含まれる場合
        print("\n2. One invalid entry (全件が拒否されます):")
        try:
            db.batch_update({
                "user4": {"name": "David", "age": 40},
                "user5": {"name": "Eve", "age": "bad"},  # 不正な年齢
                "user6": {"name": "Frank", "age": 45},
            })
            print("✓ Successfully saved all users")
        except NanaSQLiteValidationError as e:
            print(f"✗ Validation failed: {e}")
            print(f"  Database still has {len(db)} users (user4, user5, user6 were NOT added)")
    finally:
        db.close()


def demo_batch_update_partial(tmpdir: str):
    """
    batch_update_partial() は部分成功モード：正常なものだけ保存
    """
    print("\n=== Demo 2: batch_update_partial() - Partial Success Mode ===")

    schema = {
        "name": v.str(),
        "age": v.int(),
    }

    db = NanaSQLite(  # pylint: disable=unexpected-keyword-arg
        _db_path(tmpdir, "validkit_demo_partial.db"),
        validator=schema,
    )

    try:
        print("\nMixed valid and invalid data:")
        batch_update_partial = getattr(db, "batch_update_partial")
        failed = batch_update_partial(
            {
                "user1": {"name": "Alice", "age": 25},     # OK
                "user2": {"name": "Bob", "age": "bad"},  # 不正な年齢
                "user3": {"name": "Carol", "age": 22},     # OK
            }
        )

        print(f"\n✓ Successfully saved {len(db)} users")
        print(f"✗ Failed to save {len(failed)} users\n")

        print("Saved users:")
        for key in sorted(db.keys()):
            print(f"  - {key}: {db[key]}")

        print("\nFailed users:")
        for key, error_msg in failed.items():
            print(f"  - {key}: {error_msg}")
    finally:
        db.close()


def demo_use_cases():
    """
    どちらを使うべきかのガイド
    """
    print("\n=== When to Use Each Method ===")
    print("""
batch_update():
  ✓ トランザクション的な整合性が必要な場合
  ✓ 全件成功が保証されないと困る場合
  ✓ 例: 財務データ、クリティカルな設定

batch_update_partial():
  ✓ ベストエフォートでデータを取り込みたい場合
  ✓ 一部の不正データがあっても他は保存したい場合
  ✓ 例: ログのインポート、外部APIからのデータ取得
    """)


def demo_coerce_mode(tmpdir: str):
    """
    coerce モードのデモ
    """
    print("\n=== Demo 3: Coerce Mode ===")

    schema = {
        "name": v.str(),
        "age": v.int().coerce(),
        "score": v.float().coerce(),
    }

    db = NanaSQLite(  # pylint: disable=unexpected-keyword-arg
        _db_path(tmpdir, "validkit_demo_coerce.db"),
        validator=schema,
        coerce=True,
    )

    try:
        print("\nData with type coercion:")
        batch_update_partial = getattr(db, "batch_update_partial")
        failed = batch_update_partial(
            {
                "user1": {"name": "Alice", "age": "25", "score": "98.5"},
                "user2": {"name": "Bob", "age": "30", "score": "87.0"},
                "user3": {"name": "Charlie", "age": "invalid", "score": "91.2"},
            }
        )

        print(f"\n✓ Successfully saved {len(db)} users with coercion")
        for key in sorted(db.keys()):
            data = db[key]
            age_type = type(data['age']).__name__
            score_type = type(data['score']).__name__
            print(f"  - {key}: {data} (age type: {age_type}, score type: {score_type})")

        print(f"\n✗ Failed: {len(failed)} users")
        for key, error_msg in failed.items():
            print(f"  - {key}: {error_msg}")
    finally:
        db.close()


def main():
    """Run all demos"""
    print("=" * 60)
    print("Validkit Batch Operations Demo")
    print("=" * 60)

    if not HAS_VALIDKIT:
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        demo_batch_update_atomic(tmpdir)
        demo_batch_update_partial(tmpdir)
        demo_coerce_mode(tmpdir)
        demo_use_cases()

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
