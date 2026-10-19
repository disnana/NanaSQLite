"""Regressions for the September 2026 Codex Security findings."""

import re
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import BaseHook, UniqueHook


@pytest.mark.parametrize("mode", ["aes-gcm", "chacha20", "fernet"])
@pytest.mark.parametrize("backend", ["immediate", "v2", "memory"])
def test_child_and_grandchild_encryption_survives_reopen(tmp_path, mode, backend):
    path = str(tmp_path / "encrypted.db")
    key = Fernet.generate_key() if mode == "fernet" else AESGCM.generate_key(bit_length=256)
    options = {"v2_mode": backend == "v2", "memory_first": backend == "memory"}
    with NanaSQLite(path, encryption_key=key, encryption_mode=mode, **options) as parent:
        child = parent.table("child")
        grandchild = child.table("grandchild")
        child["k"] = {"secret": "child secret"}
        grandchild["k"] = "grandchild secret"
        grandchild.close()
        child.close()
    with sqlite3.connect(path) as conn:
        for table in ("child", "grandchild"):
            raw = conn.execute(f'SELECT value FROM "{table}"').fetchone()[0]
            assert isinstance(raw, bytes)
            assert b"secret" not in raw
    with NanaSQLite(path, encryption_key=key, encryption_mode=mode) as parent:
        assert parent.table("child")["k"] == {"secret": "child secret"}
        assert parent.table("grandchild")["k"] == "grandchild secret"


@pytest.mark.parametrize("mode", ["aes-gcm", "chacha20", "fernet"])
def test_legacy_child_plaintext_migration_preserves_parent_and_backup(tmp_path, mode):
    path = str(tmp_path / "legacy.db")
    backup = str(tmp_path / "backup.db")
    working = str(tmp_path / "working.db")
    key = Fernet.generate_key() if mode == "fernet" else AESGCM.generate_key(bit_length=256)
    expected = {"a": {"secret": "旧データ"}, "b": [1, None, True]}
    # Model the old layout: encrypted parent with an independently plaintext child.
    with NanaSQLite(path, encryption_key=key, encryption_mode=mode) as parent:
        parent["parent"] = "parent secret"
    with NanaSQLite(path, table="child") as child:
        child.batch_update(expected)
        child.backup(backup)
        child.backup(working)
    with NanaSQLite(working, table="child") as source:
        values = dict(source.iter_items(batch_size=1))
    with NanaSQLite(working, table="child", encryption_key=key, encryption_mode=mode) as target:
        target.batch_update(values)
    with NanaSQLite(working, encryption_key=key, encryption_mode=mode) as parent:
        assert parent["parent"] == "parent secret"
        assert dict(parent.table("child").iter_items(batch_size=1)) == expected
    with sqlite3.connect(working) as conn:
        rows = conn.execute('SELECT value FROM "child"').fetchall()
        assert len(rows) == len(expected)
        assert all(isinstance(row[0], bytes) for row in rows)
    with NanaSQLite(backup, table="child") as original:
        assert dict(original.iter_items()) == expected


@pytest.mark.parametrize("quote", ["{}", '"{}"', "[{}]", "`{}`"])
@pytest.mark.parametrize("function", ["randomblob", "length"])
def test_sql_function_policy_covers_sqlite_quote_forms(tmp_path, quote, function):
    with NanaSQLite(str(tmp_path / "policy.db"), forbidden_sql_functions=["LENGTH"]) as db:
        db["k"] = "normal"
        with pytest.raises(NanaSQLiteValidationError):
            db.query(columns=[f"{quote.format(function)}(8)"])
        assert db.query(columns=["'RANDOMBLOB(' AS literal"])[0]["literal"] == "RANDOMBLOB("
        assert db.query(columns=[f"{quote.format('abs')}(-8) AS result"])[0]["result"] == 8


def test_child_sql_policy_and_independent_sets(tmp_path):
    with NanaSQLite(
        str(tmp_path / "policy.db"),
        allowed_sql_functions=["CUSTOM"],
        forbidden_sql_functions=["LENGTH"],
        max_clause_length=40,
    ) as db:
        child = db.table("child")
        child["k"] = "value"
        with pytest.raises(NanaSQLiteValidationError):
            child.table("grandchild").query(columns=["length(value)"])
        child._validate_expression("CUSTOM(value)")
        with pytest.raises(NanaSQLiteValidationError):
            child._validate_expression("value = " + "1" * 41)
        child.allowed_sql_functions.add("OTHER")
        child.forbidden_sql_functions.add("ABS")
        assert "OTHER" not in db.allowed_sql_functions
        assert "ABS" not in db.forbidden_sql_functions
        db.strict_sql_validation = False
        permissive = db.table("permissive")
        with pytest.warns(UserWarning):
            permissive._validate_expression("UNKNOWN(value)")


async def test_async_child_inherits_concrete_encryption_and_policy(tmp_path):
    path = str(tmp_path / "async.db")
    key = AESGCM.generate_key(bit_length=256)
    async with AsyncNanaSQLite(path, encryption_key=key, forbidden_sql_functions=["LENGTH"]) as db:
        child = await db.table("child")
        await child.aset("k", "async secret")
        with pytest.raises(NanaSQLiteValidationError):
            await child.query(columns=["[length](value)"])
    with sqlite3.connect(path) as conn:
        raw = conn.execute('SELECT value FROM "child"').fetchone()[0]
        assert isinstance(raw, bytes)
        assert b"async secret" not in raw


@pytest.mark.parametrize(
    "pattern",
    [
        r"(a{1,})+$",
        r"(?:a+){20}$",
        r"(a)?(?(1)(b+)+|c)$",
        r"(a)?(?(1)b|(c{1,})+)$",
        r"(a+){2}$",
        r"(?:a{1,3}){2,}$",
        r"((a+))+$",
        r"(a|aa){1,}$",
        r"(?:a?)+$",
        r"(?x)( a{1,} )+$",
    ],
)
@pytest.mark.parametrize("compiled", [False, True])
def test_stdlib_regex_rejects_structural_repeat_bypasses(monkeypatch, pattern, compiled):
    monkeypatch.setattr("nanasqlite.hooks.HAS_RE2", False)
    with pytest.raises(NanaSQLiteValidationError, match="dangerous regex"):
        BaseHook(key_pattern=re.compile(pattern) if compiled else pattern)


def test_stdlib_regex_keeps_normal_filters_and_flags(monkeypatch):
    monkeypatch.setattr("nanasqlite.hooks.HAS_RE2", False)
    for pattern in (r"^user_\d+$", r"^(?:ab{2})+$", r"^[a-z(){}+]+$", r"(?x)^ user_ \d+ $"):
        assert BaseHook(key_pattern=pattern)._should_run("user_12") in (True, False)
    assert BaseHook(key_pattern=re.compile(r"^ USER_ \d+ $", re.VERBOSE | re.I))._should_run("user_12")


@pytest.mark.parametrize("consistency", ["manual", "auto"])
def test_partial_unique_validation_holds_lock_through_commit(tmp_path, consistency):
    checked = threading.Event()
    release = threading.Event()
    attempted = threading.Event()

    class PausingUnique(UniqueHook):
        def validate_batch_write(self, db, mapping):
            super().validate_batch_write(db, mapping)
            checked.set()
            assert release.wait(5)

    with (
        NanaSQLite(str(tmp_path / "unique.db"), hooks=[PausingUnique("email")], cache_consistency=consistency) as db,
        ThreadPoolExecutor(2) as pool,
    ):
        batch = pool.submit(db.batch_update_partial, {"a": {"email": "same"}})
        assert checked.wait(5)

        def competing_write():
            attempted.set()
            db["b"] = {"email": "same"}

        competitor = pool.submit(competing_write)
        try:
            assert attempted.wait(5)
            # The lock is owned by the checked batch until its commit.
            acquired = db._lock.acquire(blocking=False)
            if acquired:
                db._lock.release()
            assert not acquired
        finally:
            release.set()
        assert batch.result(5) == {}
        with pytest.raises(NanaSQLiteValidationError):
            competitor.result(5)
        assert db["a"] == {"email": "same"}
        assert "b" not in db
