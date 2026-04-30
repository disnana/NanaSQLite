```markdown
### 🔍 発見サマリーテーブル

| ID | 関数 | カテゴリ | 深刻度 | CWE | BLINDカテゴリ |
|:---|:---|:---|:---:|:---|:---:|
| F-001 | `V2Engine.shutdown` | ロジックバグ・データ消失 | 🔴 CRITICAL | CWE-367 | B7 |
| F-002 | `UniqueHook.before_write` | 状態不整合（制約バイパス） | 🟠 HIGH | CWE-698 | B2 |
| F-003 | `NanaSQLite.query_with_pagination` | SQLインジェクション | 🟠 HIGH | CWE-89 | - |
| F-004 | `V2Engine.get_dlq` | 情報漏洩 | 🟡 MEDIUM | CWE-200 | B6 |
| F-005 | `ExpiringDict._evict` | スレッド競合・データ破損 | 🟡 MEDIUM | CWE-362 | B5 |

---

### 📋 発見詳細（上位5件）

#### FINDING-001

**関数**: `V2Engine.shutdown` (ChunkID: C313, **C310**)
**深刻度**: 🔴 CRITICAL
**カテゴリ**: ロジックバグ・状態不整合
**CWE**: CWE-367 (Time-of-check Time-of-use)

**根拠 (セクション参照)**:
[BLIND B7] `atexit` 登録によるシャットダウン順序の競合、および `V2Engine.retry_dlq` (C310) との相互作用。

**悪用シナリオ**:
```
Step 1: 攻撃者（あるいは高負荷状態）が大量の書き込み要求を発生させ、V2Engineのstagingバッファにデータが滞留する。
Step 2: プロセス終了がトリガーされ `atexit` 経由で `V2Engine.shutdown` が呼び出される。
Step 3: `shutdown` メソッド内で、スレッドプール (`_worker.shutdown`) が停止された後や、DB接続が閉じられた状態で `_perform_flush()` が呼び出され、書き込みエラーが多発する。
Step 4: エラーになったデータがDLQに送られるが、同時に別スレッドから `retry_dlq` (C310) が呼ばれると、シャットダウン中のキューに再投入される。
Step 5: 結果としてキューが処理されず、認証ログや監査ログなどの重要な永続化データがDBに書き込まれることなくメモリ上で完全に消失（セキュリティ要件のバイパス）する。
```

**修正骨格**:
```python
# 修正前（問題）
def shutdown(self):
    self._worker.shutdown()
    self._perform_flush() # DBクローズ後やワーカー停止後にフラッシュしている可能性

# 修正後
def shutdown(self):
    if getattr(self, '_is_shutting_down', False): return
    self._is_shutting_down = True
    # ワーカーを止める前にすべてのバッファを強制フラッシュ
    self._perform_flush()
    self._worker.shutdown(wait=True)
    atexit.unregister(self.shutdown)
```

**副作用リスク**: シャットダウン時のブロック時間が増加し、アプリケーションの停止が遅延する可能性がある。

---

#### FINDING-002

**関数**: `UniqueHook.before_write` (ChunkID: C264, **C310**)
**深刻度**: 🟠 HIGH
**カテゴリ**: 状態不整合（制約バイパス）
**CWE**: CWE-698 (Execution After Redirect / 副作用のロールバック不備)

**根拠 (セクション参照)**:
[BLIND B2] Hookチェーンにおける原子性の欠如。

**悪用シナリオ**:
```
Step 1: 攻撃者が、UniqueHook とその他のバリデーションHookが設定されたテーブルにデータを書き込む。
Step 2: `UniqueHook.before_write` は検証を通過し、メモリ上のインデックス辞書 `_value_to_key` を更新する。
Step 3: 次に実行されたHook（例: CheckHook）が例外を投げ、DB書き込み自体は中断される。
Step 4: DBには書き込まれていないにも関わらず、UniqueHook のメモリインデックスは更新されたまま残る。
Step 5: 攻撃者が正当なデータを再送信しようとすると、「重複」とみなされて拒否される（DoS状態）。逆にDBの実態と乖離したインデックスを悪用し、一意制約をすり抜ける事象が発生しうる。
```

**修正骨格**:
```python
# 修正前（問題）
for hook in self._hooks:
    hook.before_write(self, key, value) # 例外で中途半端な状態が残る

# 修正後
applied_hooks = []
try:
    for hook in self._hooks:
        hook.before_write(self, key, value)
        applied_hooks.append(hook)
except Exception:
    # ロールバックインターフェースをHook層に設ける
    for hook in reversed(applied_hooks):
        if hasattr(hook, 'rollback_write'):
            hook.rollback_write(self, key, value)
    raise
```

**副作用リスク**: Hookプロトコルのインターフェース変更が必要になり、サードパーティ製Hookとの後方互換性が損なわれる可能性がある。

---

#### FINDING-003

**関数**: `NanaSQLite.query_with_pagination` (ChunkID: C234, **C310**)
**深刻度**: 🟠 HIGH
**カテゴリ**: SQLインジェクション
**CWE**: CWE-89 (SQL Injection)

**根拠 (セクション参照)**:
[CALLCHAIN フロー②] `order_by` や `group_by` 句はプレースホルダ化できないため、文字列として直接結合される。

**悪用シナリオ**:
```
Step 1: 攻撃者が API のソートパラメータ (`order_by`) に `id; ATTACH DATABASE 'x.db' AS x;--` などのペイロードを入力する。
Step 2: `_validate_expression` をバイパスする文字列構成にするか、`override_allowed=True` の文脈を利用する。
Step 3: `query_with_pagination` 内部で `SELECT * FROM table ORDER BY {order_by}` と結合される。
Step 4: 任意のデータベース操作が実行され、情報漏洩やデータ改ざんに繋がる。
```

**修正骨格**:
```python
# 修正前（問題）
sql = f"SELECT {cols} FROM {table} ORDER BY {order_by}"

# 修正後
def query_with_pagination(self, ..., order_by=None):
    if order_by:
        # STRICTなホワイトリスト検証（英数字とアンダースコアのみ等）
        if not re.match(r'^[a-zA-Z0-9_., ASC]+$', order_by):
            raise ValueError("Invalid order_by format")
    # ...
```

**副作用リスク**: 開発者が複雑な動的式（例: `CASE WHEN...`）を `order_by` に使用できなくなる。

---

#### FINDING-004

**関数**: `V2Engine.get_dlq` (ChunkID: C309, **C310**)
**深刻度**: 🟡 MEDIUM
**カテゴリ**: 情報漏洩
**CWE**: CWE-200 (機密情報の暴露)

**根拠 (セクション参照)**:
[BLIND B6] `_add_to_dlq` が例外メッセージやDBの内部状態を含むオブジェクトをそのままリストに保持し、露出する。

**悪用シナリオ**:
```
Step 1: 攻撃者が故意に不正なデータ（長過ぎる文字列や型違反）を送信し、非同期バルク書き込みを失敗させる。
Step 2: 同一のチャンク（`_process_kvs_chunk`）に含まれていた「他のユーザの正常なデータ」も巻き込まれてDLQに送られる。
Step 3: 攻撃者がエラー監視APIや状態確認エンドポイント経由で `get_dlq()` の結果を読み取る。
Step 4: 他ユーザの機密データや、SQLiteの内部ファイルパス等を含んだスタックトレースが漏洩する。
```

**修正骨格**:
```python
# 修正前（問題）
def _add_to_dlq(self, error_msg, item):
    self.dlq.append(DLQEntry(error=error_msg, item=item))

# 修正後
def _add_to_dlq(self, error_msg, item):
    # 機密情報をマスク、ログには残すがDLQにはサマリーのみ
    sanitized_error = error_msg.split('\n')[0] 
    self.dlq.append(DLQEntry(error=sanitized_error, key=item.key)) # valueは露出しない
```

**副作用リスク**: 再処理時に元の Value が欠落するため、DLQ からの自動リカバリロジックが制限される。

---

#### FINDING-005

**関数**: `ExpiringDict._evict` (ChunkID: C281, **C310**)
**深刻度**: 🟡 MEDIUM
**カテゴリ**: 状態不整合（スレッド競合）
**CWE**: CWE-362 (Concurrent Execution using Shared Resource with Improper Synchronization)

**根拠 (セクション参照)**:
[BLIND B5] バックグラウンドのスレッド/タイマーとメインの書き込みスレッド間の競合。

**悪用シナリオ**:
```
Step 1: `ExpiringDict` のバックグラウンドタイマーが発火し、`_evict` が呼び出される。
Step 2: 同タイミングでメインスレッドが同じキーに対して新しいデータの更新（UPSERT）を完了させる。
Step 3: タイマー側のスレッドが遅れて `_on_expire`（`_delete_from_db_on_expire`）を実行し、DBからデータを物理削除する。
Step 4: 新しく書き込まれたばかりの有効なデータが直後に消失し、深刻なデータ不整合を招く。
```

**修正骨格**:
```python
# 修正前（問題）
def _evict(self, key):
    self._data.pop(key, None)
    self._on_expire(key)

# 修正後
def _evict(self, key):
    with self._lock: # 削除操作とDBアクセスをロックで保護
        if self._is_actually_expired(key):
            self._data.pop(key, None)
            self._on_expire(key)
```

**副作用リスク**: タイマーによるパージ時のロック獲得により、メインスレッドの読み書きが一時的にブロックされ、高並行環境で性能が低下する。

---

### 🕳️ BLINDカテゴリへのコメント

| カテゴリ | AIによる評価 | 深刻度 |
|:---|:---|:---:|
| B1: V2Engine×キャッシュ競合 | staging と DB の間に「データが見えない瞬間」が存在する。Read After Write の一貫性が破れるためアーキテクチャ上の欠陥といえる。 | HIGH |
| B2: Hookチェーンの原子性 | F-002にて立証。メモリ上のインデックスとDB実体との乖離はセキュリティ制約のバイパスを招く。 | HIGH |
| B3: WeakrefのGCハザード | インスタンスの破棄とバックグラウンドタスクの生存期間がズレることで、Null参照例外によるプロセスクラッシュ（DoS）のリスクあり。 | MEDIUM |
| B4: lru_cache汚染 | `_sanitize_identifier` はモジュールレベルでキャッシュされるため、1つのテナントが大量の不正キーでキャッシュを埋め尽くすとリソース枯渇を引き起こす。 | MEDIUM |
| B5: Thread×asyncio混在 | F-005にて立証。タイマーによる削除と書き込みの競合によるデータ破損。 | MEDIUM |
| B6: DLQ情報漏洩 | F-004にて立証。バルク操作の巻き添えによる他ユーザーのデータ露出リスク。 | MEDIUM |
| B7: atexit競合 | F-001にて立証。シャットダウン順序の制御不能による未コミットデータの消失とロジックバグ。 | CRITICAL |

---

### 📌 追加調査推奨箇所

```
AIが判断できなかった箇所（ソースコード確認が必要）:
  1. sql_utils.py の `sanitize_sql_for_function_scan` [C276]
     → 理由: 独自のサニタイズ処理を実装しているようだが、エッジケース（ネストされたコメント、不正なエンコーディング等）に対するインジェクション耐性がシグネチャからは判定不能。
  2. core.py の `NanaSQLite._deserialize` [C163]
     → 理由: 暗号化解除後に `orjson.loads` または `json.loads` を使用している。もし暗号鍵が外部から制御可能、または暗号化がOFFの場合、JSONパーサを通じたオブジェクトインジェクション（またはメモリ枯渇）が可能かソースコードの確認が必要。
```
```