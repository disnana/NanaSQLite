# 保存状態・高負荷制御・分割読み取り

v1.6.1で追加されたAPIです。既存の設定は維持され、キャッシュ整合性と受付上限は明示的に有効化します。

## 保存状態を確認する

```python
from nanasqlite import NanaSQLite

with NanaSQLite("app.db", v2_mode=True, flush_mode="manual") as db:
    db["settings"] = {"theme": "dark"}
    print(db.get_status())
    db.flush(wait=True)
    if db.get_status()["failed_count"]:
        print(db.get_dlq_summary())  # 固定コードと時刻のみ
        # 障害原因を解消してから再投入する
        db.retry_dlq()
        db.flush(wait=True)
```

`get_status()` はメトリクスを有効にしなくても使用できます。`table()` の子では、共有エンジン全体の状態を返します。

| フィールド | 意味 |
| --- | --- |
| `mode` | `immediate` または `write_back` |
| `pending_kvs_count` | 保存待ちの異なるテーブル・キー組の数。同一キーの上書きは集約 |
| `flushing_kvs_count` | 処理中のKVSバッチに含まれるキー数 |
| `pending_sql_count` | キュー内のSQLタスク数。実行中タスクは含まない |
| `oldest_pending_age_seconds` | 待ちキュー内で最も古い項目の経過秒数。空なら `None`。再投入時にリセット |
| `flush_active` | フラッシュ処理が実行中か |
| `failed_count` | 現在の失敗キュー（DLQ）の件数 |
| `failure_count` | エンジン開始後の累積失敗件数 |
| `dropped_failure_count` | DLQ上限によって破棄した失敗項目の累積件数 |
| `last_failure_time` | 最終失敗のUNIX時刻、未発生なら `None` |
| `last_successful_flush_time` | 作業を含むフラッシュが新しい失敗なく終了したUNIX時刻 |

状態は複数のロックで順に採取する診断用の概況です。保存完了の同期バリアではありません。処理中の件数はバッチ全体を表し、一部コミット済みの行を含む場合があります。即時保存モードはキューを持たず、件数は0、時刻は `None` です。キャッシュ自動整合性と同様、状態APIは閉じたインスタンスでは例外になります。

`get_dlq_summary()` の `error` は `write_failed` という固定コードです。従来の内部エンジンAPIが返していた生の例外文も、値・キー・SQLを含む可能性があるため伏せます。詳細が必要な信頼できるコードでのみ既存の `get_dlq()` を利用してください。`clear_dlq()`・`retry_dlq()` は累積失敗・破棄件数をリセットしません。破棄済みの項目は再試行できません。同じテーブル・キーに新しいKVS書込みや削除を受け付けた場合、古い失敗項目は再試行時に除外し、新しい値を上書きしません。任意SQLの再試行にはこのキー単位の保護は適用されません。

非同期版は `await db.aget_status()`、`await db.aget_dlq_summary()` です。SQL待ち時間の集計は状態取得時だけキューを走査し、通常の読み書きには走査を追加しません。

## 非同期処理の受付上限

```python
from nanasqlite import AsyncNanaSQLite

async def save():
    async with AsyncNanaSQLite(
        "app.db", max_workers=5,
        max_pending_operations=100, admission_timeout=2.0,
    ) as db:
        await db.aset("settings", {"theme": "dark"})
```

- `max_pending_operations` はexecutorに投入済みの「実行中＋待機中」の合計上限です。既定の `None` は従来通り上限なしです。
- `admission_timeout` は受付枠の待機秒数です。超過すると `asyncio.TimeoutError` が発生し、その操作は投入されません。`None` は枠が空くまで待機します。
- `table()` の子は親と同じ受付枠を共有します。キャッシュだけで完了する読み取りはexecutor枠を使用しません。
- 投入後のキャンセルはSQLite処理を取り消しません。実際の処理が終了するまで枠を保持します。キャンセルされた書き込みを再試行する前に、結果を確認してください。
- 終了開始後は新規受付を拒否し、受付済みの処理を待ちます。`close()` の呼び出し元がキャンセルされても終了処理は続きます。再度 `await db.close()` で完了を待てます。これは受付上限なしの場合も同じです。未完了トランザクションのため終了に失敗した場合は、ロールバックまたはコミット後に終了を再試行できます。

この上限は利用側が作った待機コルーチンの数や、v2の保存待ちバッファのサイズを制限しません。大量投入するアプリ側でも入力を少量ずつ処理してください。タイムアウトはSQLの実行時間制限ではありません。

## 大量データの分割読み取り

```python
with NanaSQLite("app.db") as db:
    for key, value in db.iter_items(batch_size=256):
        process(key, value)

async def export():
    async with AsyncNanaSQLite("app.db") as db:
        async for key, value in db.aiter_items(batch_size=256):
            process(key, value)
```

`process` は利用側の処理関数です。APIはキー昇順でバッチを取得し、キャッシュに全件を読み込みません。メモリ量は件数だけでなく各値の大きさにも依存します。復号・`after_read` フックを適用し、各バッチのカーソルは返却前に閉じます。呼び出し元が値を受け取っている間、接続ロックを保持しません。

v2 / `memory_first` では開始時にフラッシュし、未解決のDLQがあれば例外になります。走査は全体を通したスナップショットではなく、後続バッチに更新が反映される場合があります。既に通過したキーより小さい位置への挿入は取得されません。一貫したエクスポートが必要なら `backup()` で作ったDBを走査してください。

## キャッシュの自動整合性

```python
with NanaSQLite("app.db", cache_consistency="auto") as db:
    print(db.get("settings"))
```

既定の `manual` は従来通り、必要に応じて `refresh()` を呼びます。`auto` はキャッシュ利用時に別接続のコミットと同一接続の変更を確認し、変更時に値・未存在キャッシュ・フックのインデックスを無効化します。子テーブルにも継承し、同期・非同期の両方で使えます。

確認とキャッシュ利用は共有ロック内で実行します。トランザクション中はロールバック後の古い値を残さないため、キャッシュを再利用しません。別接続の変更検知は [SQLiteの `PRAGMA data_version`](https://www.sqlite.org/pragma.html#pragma_data_version) を使用します。同一接続の更新確認は `total_changes()` とトランザクション状態を併用します。読み取り全体のスナップショット保証や、外部プロセスに対するフック制約の原子性を追加する機能ではありません。

`auto` は即時保存限定です。`v2_mode`・`memory_first`・永続化TTLとの組み合わせは、未保存データや期限管理との衝突を避けるため初期化時に拒否します。通常キャッシュTTL・LRU・暗号化は使用できます。確認処理のため読み取りコストが増え、同じ接続での自身の書き込み後にもキャッシュを無効化します。キャッシュ最速経路が必要なら既定設定を利用してください。
