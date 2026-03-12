# V2 アーキテクチャ

NanaSQLite の V2 モードは、書き込みの多いワークロードに対して非ブロッキングの書き込みを実現するオプションのアーキテクチャです。

::: warning 制限事項
V2 モードはシングルプロセスでの利用を想定しています。Gunicorn のマルチワーカーなど、複数プロセスからの利用はサポートしていません。
:::

## 概要

V2 エンジンは **デュアルレーン** 設計を採用しています:

```
アプリケーション
  │
  ├─ KVS レーン ──────→ ステージングバッファ → コミット
  │   (dict操作)          (書き込み結合)
  │
  └─ Strict レーン ───→ 優先度キュー → 順序通り実行
      (SQL操作)           (FIFO)
```

- **KVS レーン**: `db["key"] = value` のような辞書操作を高速に処理。同じキーへの書き込みは結合（coalescing）される
- **Strict レーン**: `sql_insert()`、`sql_update()` などの SQL 操作を順序を保って実行

## 有効化

```python
from nanasqlite import NanaSQLite

db = NanaSQLite(
    "app.db",
    v2_mode=True,           # V2 エンジンを有効化
    flush_mode="immediate",  # フラッシュモード
)
```

## フラッシュモード

V2 エンジンはデータをバックグラウンドでデータベースに書き込みます。4 つのフラッシュモードから選択できます:

| モード | 説明 | データ安全性 | パフォーマンス |
|--------|------|-------------|--------------|
| `immediate` | 操作ごとに即座にフラッシュ | ★★★★★ | ★★★ |
| `count` | N 件蓄積後にフラッシュ | ★★★★ | ★★★★ |
| `time` | 一定時間間隔でフラッシュ | ★★★★ | ★★★★ |
| `manual` | 手動フラッシュのみ | ★★★ | ★★★★★ |

### immediate（デフォルト）

最も安全なモード。操作ごとにデータベースへの書き込みが保証されます:

```python
db = NanaSQLite("app.db", v2_mode=True, flush_mode="immediate")
db["key"] = "value"  # 即座にDB書き込み
```

### count

指定件数の操作が蓄積されたらフラッシュ:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    flush_mode="count",
    flush_count=100,  # 100 件ごとにフラッシュ
)
```

### time

指定間隔でフラッシュ:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    flush_mode="time",
    flush_interval=3.0,  # 3 秒ごとにフラッシュ
)
```

### manual

完全に手動制御:

```python
db = NanaSQLite("app.db", v2_mode=True, flush_mode="manual")

db["k1"] = "v1"
db["k2"] = "v2"
db["k3"] = "v3"

# 明示的にフラッシュ
db.flush()
```

::: danger manual モードの注意
`flush()` を呼ばずにプログラムが終了すると、バッファ内のデータが失われます。
:::

## チャンクサイズ

大量の書き込みがある場合、チャンクサイズを調整してトランザクションサイズを制御できます:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    v2_chunk_size=1000,  # 1000 件ずつトランザクション
)
```

## Dead Letter Queue (DLQ)

書き込みに失敗した操作は **Dead Letter Queue** に隔離されます。これにより、エラーが後続の操作をブロックしません。

### DLQ の確認

```python
# DLQ の内容を取得
dlq = db.get_dlq()
for item in dlq:
    print(f"失敗した操作: {item}")
```

### DLQ のリトライ

```python
# 失敗した操作を再試行
db.retry_dlq()
```

## StrictTask

Strict レーンにカスタムタスクをエンキューできます:

```python
from nanasqlite.v2_engine import StrictTask

# 優先度付きタスクをエンキュー
task = StrictTask(
    priority=1,
    sequence_id=0,
    task_type="sql",
    sql="INSERT INTO logs (message) VALUES (?)",
    parameters=["Important event"],
    on_success=lambda: print("成功"),
    on_error=lambda e: print(f"失敗: {e}"),
)
db._v2_engine.enqueue_strict_task(task)
```

## V2 コンストラクタパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|----------|------|
| `v2_mode` | `bool` | `False` | V2 エンジンの有効化 |
| `flush_mode` | `str` | `"immediate"` | フラッシュモード |
| `flush_interval` | `float` | `3.0` | time モードの間隔（秒） |
| `flush_count` | `int` | `100` | count モードの件数閾値 |
| `v2_chunk_size` | `int` | `1000` | トランザクションチャンクサイズ |

## 非同期での V2 利用

`AsyncNanaSQLite` でも V2 モードが使用できます:

```python
from nanasqlite import AsyncNanaSQLite

async def main():
    db = AsyncNanaSQLite(
        "app.db",
        v2_mode=True,
        flush_mode="time",
        flush_interval=5.0,
    )

    await db.aset("key", "value")
    await db.aflush()

    dlq = await db.aget_dlq()

    db.close()
```

## V1 vs V2 比較

| 項目 | V1（デフォルト） | V2 |
|------|----------------|-----|
| 書き込み | 同期・ブロッキング | 非ブロッキング（バッファ経由） |
| 読み取り | キャッシュ → DB | キャッシュ → バッファ → DB |
| データ安全性 | 即時保証 | フラッシュモードに依存 |
| 書き込み性能 | ベースライン | 高スループット |
| 複雑さ | シンプル | DLQ・フラッシュ管理が必要 |
| プロセス | マルチプロセス対応 | シングルプロセスのみ |

## いつ V2 を使うべきか

**V2 が適している場面:**
- 書き込みが頻繁なアプリケーション（ログ、センサーデータ、チャット）
- 書き込みレイテンシを最小化したい場合
- シングルプロセスアプリケーション

**V1 を使うべき場面:**
- データの即時永続化が必要
- マルチプロセス環境（Gunicorn ワーカーなど）
- シンプルな CRUD アプリケーション
