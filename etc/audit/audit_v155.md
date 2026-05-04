# NanaSQLite v1.5.5 セキュリティ・品質監査レポート

| 項目 | 内容 |
|---|---|
| **対象バージョン** | v1.5.5 |
| **監査日** | 2026-04-30 |
| **対象ファイル** | `src/nanasqlite/core.py`, `src/nanasqlite/utils.py`, `src/nanasqlite/v2_engine.py` |
| **前回監査** | v1.5.4 |

---

## 概要

本レポートは NanaSQLite v1.5.5 に対して実施したセキュリティ・品質監査の結果をまとめたものである。
v1.5.5 では ORDER BY / GROUP BY に対するバリデーション強化（変更履歴「F-003」）が導入されたが、
実装上の不備により依然としてサブクエリインジェクションが可能な状態であった。
その他、`ExpiringDict` の実装上の非一貫性および `get_db_size()` の `:memory:` 未対応についても修正を適用した。

---

## 検出項目 サマリー

| ID | 分類 | 深刻度 | タイトル | 対処 |
|---|---|---|---|---|
| SEC-01 | セキュリティ | 🔴 High | ORDER BY / GROUP BY サブクエリインジェクション | 修正済み |
| BUG-01 | バグ | 🟡 Medium | `ExpiringDict.__delitem__` が非 TIMER モードでも `_cancel_timer()` を呼ぶ | 修正済み |
| BUG-02 | バグ | 🟢 Low | `get_db_size()` が `:memory:` DB で `FileNotFoundError` を送出 | 修正済み |
| PERF-01 | パフォーマンス | 🟢 Low | `ExpiringDict.__iter__` がキーごとに RLock を取得 | 修正済み |
| QUAL-01 | コード品質 | 🟢 Low | `_check_auto_flush` の TOCTOU (軽微) | ドキュメント化のみ |

---

## 各検出項目の詳細

---

### SEC-01 — ORDER BY / GROUP BY サブクエリインジェクション

| 項目 | 内容 |
|---|---|
| **深刻度** | 🔴 High |
| **該当ファイル** | `src/nanasqlite/core.py` |
| **該当行** | L736–L743（パッチ前）、`_validate_expression` メソッド |

#### 概要

v1.5.5 では ORDER BY / GROUP BY 節に対して文字ホワイトリスト検証（F-003）が追加された。
しかし、許可文字セット `[a-zA-Z0-9_.,\s\(\)\"\'\`\[\]]` は英数字・アンダースコア・括弧を含んでおり、
これらの組み合わせにより以下のようなサブクエリペイロードの構築が可能であった。

```sql
ORDER BY (SELECT CASE WHEN 1=1 THEN name ELSE age END)
```

モジュールレベルの `_DANGEROUS_SQL_RE` は DDL キーワード（DROP, DELETE, …）のみを対象としており、
`SELECT` / `FROM` / `JOIN` 等のリード専用クエリキーワードを検出しない。
`strict_sql_validation=False`（デフォルト）の場合、上記ペイロードはすべてのバリデーションを通過して
SQLite へそのまま渡されるため、**ブールベースのブラインド SQL インジェクションによる情報漏洩**が可能となる。

#### 修正内容

`src/nanasqlite/core.py` に以下の変更を加えた。

1. **モジュールレベル定数の追加**（L91 直後）

```python
_ORDERBY_SUBQUERY_KEYWORDS_RE = re.compile(
    r"\b(?:SELECT|FROM|JOIN|UNION|WHERE|HAVING|LIMIT|OFFSET|EXCEPT|INTERSECT)\b",
    re.IGNORECASE,
)
```

2. **`_validate_expression` 内の追加チェック**（`order_by` / `group_by` コンテキスト限定）

文字ホワイトリスト検証の直後に上記正規表現によるサブクエリキーワード検出を実施する。
キーワードが検出された場合は `strict` フラグに応じて `ValueError` または `UserWarning` を発生させる。

> **設計上の注意:** このチェックは `order_by` / `group_by` コンテキストにのみ適用する。
> `WHERE` 節では相関サブクエリが正当なユースケースとして存在するため除外している。

#### テスト

`tests/test_audit_poc.py` クラス `TestV155Sec01OrderBySubqueryInjection`

---

### BUG-01 — `ExpiringDict.__delitem__` が非 TIMER モードでも `_cancel_timer()` を呼ぶ

| 項目 | 内容 |
|---|---|
| **深刻度** | 🟡 Medium |
| **該当ファイル** | `src/nanasqlite/utils.py` |
| **該当行** | L259–L264（パッチ前） |

#### 概要

`__delitem__` は `_cancel_timer()` を無条件で呼び出していた。
SCHEDULER / LAZY モードでは `_timers` と `_async_tasks` は常に空の辞書であるため、
`_cancel_timer()` の呼び出しは毎回 2 回の無駄な辞書ルックアップを発生させる。

`__setitem__` では既に `if self._mode == ExpirationMode.TIMER:` ガードが存在しており、
`__delitem__` との実装上の非一貫性となっていた。

#### 修正内容

```python
def __delitem__(self, key: str) -> None:
    with self._lock:
        if self._mode == ExpirationMode.TIMER:
            self._cancel_timer(key)
        if key in self._data:
            del self._data[key]
            del self._exptimes[key]
```

#### テスト

`tests/test_audit_poc.py` クラス `TestV155Bug01ExpiringDictDelitemTimerGuard`

---

### BUG-02 — `get_db_size()` が `:memory:` データベースで `FileNotFoundError` を送出

| 項目 | 内容 |
|---|---|
| **深刻度** | 🟢 Low |
| **該当ファイル** | `src/nanasqlite/core.py` |
| **該当行** | L3321（パッチ前） |

#### 概要

`get_db_size()` は `os.path.getsize(self._db_path)` を直接呼び出していた。
`_db_path` が `":memory:"` の場合、実ファイルが存在しないため
`os.path.getsize(":memory:")` が `FileNotFoundError` を送出する。

インメモリデータベースは SQLite の正当なユースケースであり、
`NanaSQLite(":memory:")` を使用するコードでは予期せぬ例外が発生し得た。

#### 修正内容

```python
def get_db_size(self) -> int:
    if self._db_path in (":memory:", ""):
        return 0
    return os.path.getsize(self._db_path)
```

#### テスト

`tests/test_audit_poc.py` クラス `TestV155Bug02MemoryDbSize`

---

### PERF-01 — `ExpiringDict.__iter__` がキーごとに RLock を取得

| 項目 | 内容 |
|---|---|
| **深刻度** | 🟢 Low |
| **該当ファイル** | `src/nanasqlite/utils.py` |
| **該当行** | L266–L271（パッチ前） |

#### 概要

旧実装はキーごとに `_check_expiry()` を呼び出していた。
`_check_expiry()` は内部で `RLock` を取得するため、N 個のキーに対して O(N) 回のロック取得が発生する。
特に多数のキーを持つ辞書に対して `for key in expiring_dict:` を実行した場合、
ロック取得のオーバーヘッドが無視できなくなる。

#### 修正内容

単一のロック取得内でバッチ処理を行い、期限切れコールバックはロック外で実行する。

```python
def __iter__(self) -> Iterator[str]:
    now = time.time()
    expired_callbacks: list[tuple[str, Any]] = []
    with self._lock:
        live_keys: list[str] = []
        for key in list(self._data):
            if key in self._exptimes and self._exptimes[key] <= now:
                value = self._data.pop(key, None)
                self._exptimes.pop(key, None)
                if value is not None and self._on_expire:
                    expired_callbacks.append((key, value))
            else:
                live_keys.append(key)
    for key, value in expired_callbacks:
        try:
            self._on_expire(key, value)
        except Exception as e:
            logger.error("Error in ExpiringDict on_expire callback for key '%s': %s", key, e)
    yield from live_keys
```

コールバックをロック外で実行することで、クロスロックデッドロックのリスクも低減される。

#### テスト

`tests/test_audit_poc.py` クラス `TestV155Perf01ExpiringDictIterBatch`

---

### QUAL-01 — `_check_auto_flush` の TOCTOU（軽微）

| 項目 | 内容 |
|---|---|
| **深刻度** | 🟢 Low |
| **該当ファイル** | `src/nanasqlite/v2_engine.py` |
| **該当行** | L232–L240 |

#### 概要

`_check_auto_flush` では `_staging_lock` を解放した後に `flush()` を呼び出す。
この間に別スレッドがアイテムを追加した場合、フラッシュのトリガー判定が 1 件ずれる可能性がある（TOCTOU）。
`count` モードでは 1 件の超過または不足で flush が誤動作する可能性があるが、
過剰フラッシュ（余裕を持った早期実行）方向にずれるため実害は軽微である。

#### 対処

修正は適用しない。この挙動は許容可能なトレードオフとして文書化する。
`_staging_lock` を保持したまま `flush()` を呼ぶと他のロックとのデッドロックリスクが生じるため、
現在の設計は意図的なものである。

---

## 結論

v1.5.5 では計 5 件の問題を検出した。うち 4 件（SEC-01, BUG-01, BUG-02, PERF-01）はコード修正を適用済みである。
残る 1 件（QUAL-01）は許容可能なトレードオフとして文書化のみ行った。

最も重大な問題は **SEC-01**（ORDER BY サブクエリインジェクション）であり、
これは v1.5.5 で新たに導入されたバリデーション機能（F-003）の不完全な実装に起因する。
パッチ適用後は `_ORDERBY_SUBQUERY_KEYWORDS_RE` によってサブクエリキーワードを確実にブロックする。

既存のテスト（959 件以上）はすべてパッチ適用後も合格している。

---

*本レポートは NanaSQLite セキュリティ監査シリーズ（v1.4.0, v1.5.1〜v1.5.5）の一部である。*
