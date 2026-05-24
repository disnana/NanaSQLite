# v1.5.6b1 監査メモ: AsyncNanaSQLite lock_timeout 転送漏れ

作成日: 2026-05-24

## 対象

- `src/nanasqlite/async_core.py`
- `tests/test_async.py`

## 結論

### QUAL-01 — `AsyncNanaSQLite` が `lock_timeout` を内部 DB に渡していない

**判定:** 修正済み

`AsyncNanaSQLite.__init__()` は `**kwargs` を受け取るにもかかわらず `lock_timeout` を読み取っていなかった。そのため、利用者が `AsyncNanaSQLite(path, lock_timeout=0.2)` と指定しても、内部で生成される `NanaSQLite` の `_lock_timeout` は `None` のままだった。

修正では以下を行った。

- `AsyncNanaSQLite.__init__()` で `lock_timeout` を読み取り、`self._lock_timeout` に保持。
- `_ensure_initialized()` の内部 `NanaSQLite(...)` 呼び出しへ `lock_timeout=self._lock_timeout` を追加。
- `AsyncNanaSQLite.table()` のラッパーにも `_lock_timeout` をコピーし、親設定の継承状態を確認しやすくした。
- 回帰防止として `tests/test_async.py` に async 親 DB と async サブテーブルの継承確認を追加。

### BUG-04 — `get_db_size()` が `:memory:` で例外を送出する

**判定:** 現行ソースでは既に修正済み

`NanaSQLite.get_db_size()` は `":memory:"` と空文字パスに対して `0` を返す guard を持つ。戻り値型を `int | None` に変更する必要はなく、むしろ既存の `int` 契約を壊すため非推奨。

## 検証

回帰テスト:

```powershell
python -m pytest tests\test_async.py::TestAsyncBasicOperations::test_async_lock_timeout_forwarded_to_sync_db tests\test_async.py::TestAsyncBasicOperations::test_async_table_inherits_lock_timeout -q
```

初期調査に使った `scratch/` 配下の一時 PoC は、回帰テストへ置き換え済みのため削除した。

## 性能面の補足

今回の修正はロック取得時のタイムアウト設定を転送するだけで、通常操作のホットパスに分岐や追加ロックを増やさない。性能改善の次候補としては、`AsyncNanaSQLite.aget()` のキャッシュ済み読み取りで executor 往復を避けられるかをベンチマークで確認する。
