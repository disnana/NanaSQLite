# QUAL-01 / BUG-04 検証と性能レビュー

日付: 2026-05-24

## 結論

### QUAL-01: 中核問題は修正済み。ただし元の説明は不正確

実際の問題は `AsyncNanaSQLite.table()` だけではなく、もう少し広い。

- 修正前の `AsyncNanaSQLite.__init__()` は任意の `**kwargs` を受け取るが、`lock_timeout` を読んでいなかった。
- 修正前の `_ensure_initialized()` は内部の `NanaSQLite(...)` を作るときに `lock_timeout` を渡していなかった。
- `AsyncNanaSQLite.table()` は `lock_timeout` 引数を公開していない。
- `NanaSQLite.table()` もサブテーブルごとの `lock_timeout` 上書き引数は公開していない。親の値を子へ継承するだけ。

したがって「`NanaSQLite.table()` はサブテーブルごとに `lock_timeout` を上書きできる」という説明は、現行ソースでは誤り。現行ソースが対応しているのは、同期サブテーブルへの親値継承だけ。

今回の修正で、`AsyncNanaSQLite(..., lock_timeout=...)` は内部の `NanaSQLite` に値を転送するようになった。`AsyncNanaSQLite.table()` の子インスタンスも親の `lock_timeout` を継承する。

関連箇所:

- `src/nanasqlite/async_core.py`: `AsyncNanaSQLite.__init__()` の kwargs 抽出。
- `src/nanasqlite/async_core.py`: `_ensure_initialized()` の内部 `NanaSQLite(...)` 呼び出し。
- `src/nanasqlite/async_core.py`: `AsyncNanaSQLite.table()` のシグネチャとラッパー生成。
- `src/nanasqlite/core.py`: `NanaSQLite.table()` のシグネチャと子インスタンス生成。

### BUG-04: 現行ソースでは false

`get_db_size()` は `":memory:"` と `""` に対して修正済みで、`os.path.getsize()` を呼ばずに `0` を返す。

関連箇所:

- `src/nanasqlite/core.py`: `NanaSQLite.get_db_size()`。
- `tests/test_audit_poc.py`: `TestV155Bug02MemoryDbSize`。

今から戻り値型を `int | None` に変えることは推奨しない。破壊的変更になる一方、現行の `int` 契約では「実ファイルを持たない DB は 0」という明確な扱いがすでにある。

## 再現・検証ファイル

- `scratch/verify_qual_bug04_static.py`: 実行時依存なし。`ast` でソースを解析する。
- `scratch/poc_async_lock_timeout.py`: async の `lock_timeout` 転送を確認する実行 PoC。
- `scratch/poc_get_db_size_memory.py`: インメモリ DB の `get_db_size()` 挙動を確認する実行 PoC。

## 推奨修正

### QUAL-01 の最小・非破壊修正

`AsyncNanaSQLite` でコンストラクタ指定の `lock_timeout` を有効化する。

1. `AsyncNanaSQLite.__init__()`:
   - `lock_timeout = kwargs.get("lock_timeout")` を読む
   - `self._lock_timeout = lock_timeout` として保持する

2. `_ensure_initialized()`:
   - 内部 `NanaSQLite(...)` に `lock_timeout=self._lock_timeout` を渡す

3. `AsyncNanaSQLite.table()` のラッパー生成:
   - 確認・デバッグ用の一貫性として `async_sub_db._lock_timeout = getattr(self, "_lock_timeout", None)` をコピーする
   - 実際に効く値は `sub_db._lock_timeout` 側から来る

これは実装済み。すでに `**kwargs` として受け取れていた設定を有効化するだけなので後方互換。

### 追加 API として検討する場合

サブテーブルごとの上書きまで必要なら、同期版と非同期版の両方に追加する。

- `NanaSQLite.table(..., lock_timeout: float | None | EllipsisType = _UNSET)`
- `AsyncNanaSQLite.table(..., lock_timeout: float | None | EllipsisType = _UNSET)`

解決ルールは `validator` / `coerce` と同じにする。

- 省略: 親の値を継承
- 明示的な `None`: そのサブテーブルではタイムアウトなし
- 数値: そのタイムアウト値を使用

これは公開 API の拡張なので、ドキュメント化が必要。

## 追加すべきテスト

### async コンストラクタの転送

```python
async def test_async_lock_timeout_is_forwarded(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    await db.aset("k", "v")
    assert db.sync_db._lock_timeout == 0.2
    await db.close()
```

### async サブテーブルの継承

```python
async def test_async_table_inherits_lock_timeout(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    child = await db.table("child")
    assert child.sync_db._lock_timeout == 0.2
    await db.close()
```

### サブテーブル上書き

これは同期版・非同期版の両方に公開 API を追加する場合だけ入れる。

```python
def test_sync_table_can_override_lock_timeout(tmp_path):
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    child = db.table("child", lock_timeout=None)
    assert child._lock_timeout is None
```

```python
async def test_async_table_can_override_lock_timeout(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    child = await db.table("child", lock_timeout=None)
    assert child.sync_db._lock_timeout is None
    await db.close()
```

## パフォーマンス・速度面の改善観点

### P1: キャッシュ済み async read の executor 往復を避ける

`AsyncNanaSQLite.aget()` は常に executor へ処理を投げる。内部の同期 DB が初期化済みで、対象キーがすでにメモリキャッシュ上にある場合、専用の async fast path で executor 往復を省ける可能性がある。設定値やセッション情報など、キャッシュ済みデータを何度も読む Web ハンドラでは効きやすい。

注意点: `after_read` フック、LRU の順序更新、v2 staging の可視性は `NanaSQLite.get()` と同じ意味を保つ必要がある。

### P2: `AsyncNanaSQLite.table()` の属性コピー重複を減らす

`AsyncNanaSQLite.table()` は `object.__new__` で作ったオブジェクトに多数の属性を手作業でコピーしている。極端なホットパスではないが、`lock_timeout` のように将来の属性漏れが起きやすい。`_from_sync_child(parent, table_name, sub_db)` のような小さな内部生成ヘルパーへ寄せると、保守性と欠落防止に効く。

### P3: async オプション検証を一度で済ませる

同期版 `NanaSQLite.__init__()` は `lock_timeout` を検証・正規化している。async 側が生値を保持して内部同期 DB の生成時に検証を任せる設計だと、無効値の失敗が初回利用時まで遅れる。互換性重視なら許容できるが、早期失敗を優先するなら検証処理を共通ヘルパー化するとよい。

### P4: `get_db_size()` の戻り値型は `int` のまま維持する

インメモリ DB で `0` を返す現行仕様なら、`int | None` への破壊的変更を避けられる。サイズ表示コードも単純なまま保てる。

```python
size_mb = db.get_db_size() / 1024 / 1024
```

### P5: async キャッシュ読み取りのベンチマークを追加する

同期版の `get_db_size()` や `lock_timeout` テストはあるが、キャッシュ済みキーに対する `AsyncNanaSQLite.aget()` のコストを測るベンチが見当たらない。以下を小さく測ると、async cached-read fast path を入れる価値を判断しやすい。

- 初期化済み async DB
- 対象キーはキャッシュ済み
- `aget()` を N 回繰り返す
- 直接 `sync_db.get()` を呼ぶ場合と比較する

この測定で、複雑さに見合う速度改善かどうかを判断できる。
