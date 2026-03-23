# v2 アーキテクチャ ガイド

> [!IMPORTANT]
> v2 アーキテクチャは **v1.4.0dev1** で導入されたオプション機能です。シングルプロセス環境専用です。マルチプロセス環境（Gunicorn マルチワーカー等）での利用は **データ破損** の原因となります。

---

## 概要

v2 アーキテクチャは、SQLite への書き込みを **バックグラウンドスレッドで非同期に実行** することで、メインスレッド（アプリケーションロジック）の I/O ブロックを完全にゼロにする設計です。

### どのような問題を解決するか？

標準の v1 モードでは、`db["key"] = value` を呼び出すたびにメインスレッドがディスク I/O を待機します。例えばHTTPリクエストハンドラ内で頻繁にKVSへ書き込む場合、この I/O 待機がレイテンシの主要因になります。

v2 モードでは書き込みをメモリバッファに積み、バックグラウンドで SQLite へフラッシュするため、書き込みのレイテンシが事実上ゼロになります。

---

## アーキテクチャの内部構造

```
メインスレッド
    │
    ├── KVS 書き込み (db["key"] = val)
    │       └──→ [Lane 1: KVS Staging Buffer]  ← dict + lock で保護
    │
    └── SQL 実行 (db.execute(...))
            └──→ [Lane 2: Strict SQL Queue]    ← シーケンスIDで順序保証
                                ↓
                    ┌ バックグラウンドスレッド ┐
                    │     (定期フラッシュ)     │
                    │   BEGIN TRANSACTION      │
                    │   Lane1 KVS を書き込み   │
                    │   Lane2 SQL を実行       │
                    │   COMMIT                 │
                    └──────────────────────────┘
                         失敗時 → [DLQ] に隔離
```

### 2レーンハイブリッド設計

| レーン | 用途 | 特徴 |
|--------|------|------|
| **Lane 1** - KVS Staging Buffer | `db["key"] = val` / `del db["key"]` | 同一キーへの書き込みをマージ（コアレッシング）して効率化 |
| **Lane 2** - Strict SQL Queue   | `db.execute(sql, params)` 等       | 単調増加シーケンスIDで厳格な順序を保証 |

---

## 基本的な使い方

### 有効化

```python
from nanasqlite import NanaSQLite

# v2 モードを有効化（デフォルトは immediate フラッシュ）
db = NanaSQLite("mydb.db", v2_mode=True)

# 書き込みはメインスレッドをブロックしない
db["user:1"] = {"name": "Alice", "score": 100}
db["user:2"] = {"name": "Bob",   "score": 200}

# 読み込みはメモリキャッシュから即座に返る（ゼロレイテンシ）
user = db["user:1"]

db.close()  # シャットダウン時に残っているバッファを SQLite へフラッシュ
```

### 非同期 (AsyncNanaSQLite)

```python
from nanasqlite import AsyncNanaSQLite

async with AsyncNanaSQLite("mydb.db", v2_mode=True) as db:
    await db.aset("key", "value")
    # バックグラウンドで非同期フラッシュが行われる
    await db.aflush()  # 手動で即時フラッシュも可能
```

---

## フラッシュモードの選択

`flush_mode` パラメータで SQLite への書き込みタイミングを制御します。

| モード | 動作 | 主な用途 |
|--------|------|----------|
| `immediate` (デフォルト) | 書き込みの都度すぐにフラッシュ | データ消失リスクを最小化したい場合 |
| `count` | N 件以上たまったらフラッシュ | スループット優先のバッチ処理 |
| `time` | 一定時間ごとにフラッシュ | 定期バッチ処理 |
| `manual` | `db.flush()` を呼んだときのみ | 完全な手動制御 |

```python
# 100件ごとにフラッシュ（スループット重視）
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="count", flush_count=100)

# 500ms ごとにフラッシュ
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="time", flush_interval=0.5)

# 手動フラッシュ
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="manual")
db["key"] = "value"
db.flush()  # ここで初めてディスクに書き込まれる
```

---

## デッドレターキュー (DLQ)

バックグラウンドでの SQL 実行が失敗した場合（型違反、SQL構文エラー等）、failed タスクは **DLQ（Dead Letter Queue）** に隔離されます。これにより、エラーが一件あっても他のデータ永続化が継続されます。

以前は内部エンジンを直接操作する必要がありましたが、現在は公開 API として利用可能です。

```python
# DLQ の内容を確認する
dlq_items = db.get_dlq()  # 非同期版は await db.aget_dlq()
for item in dlq_items:
    print(f"Task: {item['task']}, Error: {item['error']}")

# 問題を修正してから再試行する場合
db.retry_dlq()  # 非同期版は await db.aretry_dlq()

# DLQ を空にする場合
db.clear_dlq()  # 非同期版は await db.aclear_dlq()
```

---

## メトリクス収集 (モニタリング)

エンジンの稼働状況（フラッシュの頻度、処理時間、エラー発生数など）を詳細に把握したい場合、メトリクス収集機能を有効にできます。

### 有効化
`v2_enable_metrics=True` を指定してインスタンスを作成します。この設定は `table()` メソッドで作成した子インスタンスにも自動的に引き継がれます。

```python
db = NanaSQLite("mydb.db", v2_mode=True, v2_enable_metrics=True)
```

### 統計情報の取得
`get_v2_metrics()` メソッドで現在の統計データを取得できます。

```python
stats = db.get_v2_metrics()  # 非同期版は await db.aget_v2_metrics()

print(f"総フラッシュ回数: {stats['flush_count']}")
print(f"総書き込みアイテム数: {stats['kvs_items_flushed']}")
print(f"総フラッシュ処理時間: {stats['total_flush_time']:.4f}s")
print(f"直近のフラッシュ時間: {stats['last_flush_time']:.4f}s")
print(f"DLQ エラー発生数: {stats['dlq_errors']}")
```

---

## チャンクフラッシュ

一度に大量のデータをフラッシュする場合、SQLite のロックを長時間占有しないよう、自動的にバッチを分割（チャンク）して書き込みます。

```python
# チャンクサイズを調整（デフォルト: 1000件）
db = NanaSQLite("mydb.db", v2_mode=True, v2_chunk_size=500)
```

---

## 注意点と制限事項

> [!CAUTION]
> v2 アーキテクチャは **シングルプロセス専用** です。以下の環境では使用してはいけません。
>
> - `gunicorn --workers=N` (N > 1) の FastAPI/Flask
> - `multiprocessing` を使ったワーカー
> - `fork` を使うデーモン

### データ整合性に関する注意

- `manual` または `count` モードの場合、アプリが強制終了すると **バッファ内のデータが失われます**。
- シャットダウン時に `db.close()` を必ず呼ぶことで、残りのバッファが SQLite へフラッシュされます。
- `atexit` ハンドラにより、プロセス正常終了時は自動的にシャットダウンが実行されます。

### 読み取りの整合性

v2 モードは **Write-Back Cache** 構造です。書き込み直後にメモリキャッシュから即座に読み取れますが、SQLite ファイルにはまだ反映されていない場合があります。

別プロセスから同じ SQLite ファイルを読み取る場合、フラッシュがまだ完了していないと古い値が見える場合があります。

---

## チェックリスト

- [ ] v2 モードはシングルプロセスのみで使用しているか？
- [ ] `manual` / `count` モードではデータ消失リスクを理解しているか？
- [ ] 本番環境では `db.close()` か `atexit` が確実に呼ばれるか？
- [ ] 大量バッチ処理時に `v2_chunk_size` を調整しているか？
