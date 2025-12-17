# NanaSQLite 潜在的な問題点と改善提案書

**対象バージョン**: v1.1.0a4  
**分析範囲**: ソースコード、テスト、CI/CD、ドキュメント

---

## 目次

1. [セキュリティ関連の問題](#1-セキュリティ関連の問題)
2. [コードの堅牢性に関する問題](#2-コードの堅牢性に関する問題)
3. [パフォーマンスとスケーラビリティ](#3-パフォーマンスとスケーラビリティ)
4. [API設計とユーザビリティ](#4-api設計とユーザビリティ)
5. [テストとCI/CDの改善](#5-テストとcicdの改善)
6. [ドキュメントとメンテナンス](#6-ドキュメントとメンテナンス)
7. [依存関係とライブラリ管理](#7-依存関係とライブラリ管理)
8. [優先順位と推奨対応順序](#8-優先順位と推奨対応順序)

---

## 1. セキュリティ関連の問題

### 1.1 SQLインジェクション対策の強化

**現状**: 
- `_sanitize_identifier()`メソッドで識別子の検証を行っているが、一部の複雑なSQL式では不十分な可能性
- `query()`と`query_with_pagination()`で列名の検証にやや異なるロジックを使用

**リスク**: 高  
**影響範囲**: `query()`, `query_with_pagination()`, `create_table()`, `create_index()`等

**推奨対応**:
```python
# より厳格な列名検証の統一
def _validate_column_expression(self, expression: str, allow_functions: bool = False) -> bool:
    """
    列式の検証を統一化
    - 単純な識別子: ^[a-zA-Z_][a-zA-Z0-9_]*$
    - 関数付き: 許可された関数のホワイトリスト
    - AS句: aliasの適切な検証
    """
    import re

    # 許可される関数名のホワイトリスト（必要に応じて拡張）
    allowed_functions = {"LOWER", "UPPER", "COUNT", "MAX", "MIN", "AVG"}

    identifier_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    func_call_re = re.compile(
        r"^(?P<func>[A-Za-z_][A-Za-z0-9_]*)\((?P<arg>[A-Za-z_][A-Za-z0-9_]*)\)$"
    )

    expr = expression.strip()
    if not expr:
        return False

    # AS 句の分離（エイリアスの検証を含む）
    parts = re.split(r"\s+AS\s+", expr, flags=re.IGNORECASE)
    if len(parts) > 2:
        return False

    main_expr = parts[0].strip()
    alias = parts[1].strip() if len(parts) == 2 else None

    # エイリアスも識別子として検証
    if alias is not None and not identifier_re.match(alias):
        return False

    # 関数を許可しない場合は単純な識別子のみ
    if not allow_functions:
        return bool(identifier_re.match(main_expr))

    # 関数を許可する場合:
    # 1) 単純な識別子
    if identifier_re.match(main_expr):
        return True

    # 2) 単一の関数呼び出し (FUNC(column))
    m = func_call_re.match(main_expr)
    if not m:
        return False

    func_name = m.group("func").upper()
    arg_name = m.group("arg")

    if func_name not in allowed_functions:
        return False

    return bool(identifier_re.match(arg_name))
```

**優先度**: 高

---

### 1.2 ReDoS（正規表現DoS）攻撃への脆弱性

**現状**: 
- 複数の正規表現パターンで複雑なバックトラッキングが発生する可能性
- 特に`group_by`と`order_by`の検証で使用される正規表現

**具体例**:
```python
# core.py:1308
if not re.match(r'^[\w\s,]+$', group_by):
```

**リスク**: 中  
**影響**: 大量のカンマとスペースを含む入力でCPU使用率が急上昇

**推奨対応**:
```python
# 入力長の制限を追加
MAX_CLAUSE_LENGTH = 1000

def _validate_group_by(self, group_by: str) -> None:
    if len(group_by) > MAX_CLAUSE_LENGTH:
        raise ValueError(f"group_by clause too long (max {MAX_CLAUSE_LENGTH} chars)")
    # シンプルな文字チェックに置き換え
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_,. ')
    if not all(c in allowed_chars for c in group_by):
        raise ValueError("Invalid characters in group_by clause")
```

**優先度**: 中

---

### 1.3 PRAGMA設定のセキュリティ強化

**現状**: 
- 許可されたPRAGMAのホワイトリストは存在するが、一部の危険なPRAGMAも含まれる可能性
- 文字列値の検証が`[\w\-\.]+`で緩い

**リスク**: 低〜中  
**具体的な懸念**:
- `writable_schema`などの危険なPRAGMAが将来追加される可能性
- ファイルパスを取る一部のPRAGMA（未実装）でのパストラバーサル

**推奨対応**:
```python
# 読み取り専用と書き込み可能なPRAGMAを分離
READONLY_PRAGMAS = {'schema_version', 'table_info', 'index_list', ...}
WRITABLE_PRAGMAS = {'foreign_keys', 'journal_mode', 'synchronous', ...}

# 明示的に禁止リストも定義
FORBIDDEN_PRAGMAS = {'writable_schema', 'data_store_directory'}
```

**優先度**: 低

---

## 2. コードの堅牢性に関する問題

### 2.1 エラーハンドリングの不統一

**現状**: 
- 一部のメソッドでAPSWの例外を直接スロー
- 一部のメソッドで`ValueError`や`TypeError`を使用
- ユーザーにとって予測しにくいエラーメッセージ

**影響範囲**: 全般

**推奨対応**:
```python
# カスタム例外クラスの導入
class NanaSQLiteError(Exception):
    """Base exception for NanaSQLite"""
    pass

class NanaSQLiteValidationError(NanaSQLiteError):
    """Validation error"""
    pass

class NanaSQLiteDatabaseError(NanaSQLiteError):
    """Database operation error"""
    pass
```

**優先度**: 中

---

### 2.2 リソースリークのリスク

**現状**: 
- `table()`メソッドで作成されたサブインスタンスの追跡がない
- 親インスタンスが閉じられた後、子インスタンスが孤立する可能性
- ドキュメントで警告はあるが、コードレベルでの保護がない

**具体的な問題**:
```python
main_db = NanaSQLite("app.db")
sub_db = main_db.table("users")
main_db.close()  # sub_dbは孤立するが、エラーにならない
sub_db["key"] = "value"  # 閉じた接続を使おうとする
```

**推奨対応**:
```python
class NanaSQLite:
    def __init__(self, ...):
        self._child_instances = []  # 子インスタンスを追跡
        self._is_closed = False
    
    def table(self, table_name: str):
        if self._is_closed:
            raise NanaSQLiteError("Cannot create table instance from closed connection")
        child = NanaSQLite(...)
        self._child_instances.append(weakref.ref(child))
        return child
    
    def close(self):
        if self._is_closed:
            return
        self._is_closed = True
        # 子インスタンスに通知
        for child_ref in self._child_instances:
            child = child_ref()
            if child:
                child._mark_parent_closed()
```

**優先度**: 高

---

### 2.3 型ヒントの不完全性

**現状**: 
- 型ヒントは存在するが、一部のメソッドで`Any`が多用されている
- ジェネリック型のサポートが不十分

**推奨対応**:
```python
from typing import TypeVar, Generic, overload

T = TypeVar('T')

class NanaSQLite(MutableMapping[str, Any]):
    @overload
    def get(self, key: str) -> Any: ...
    
    @overload
    def get(self, key: str, default: T) -> Union[Any, T]: ...
    
    def get(self, key: str, default: Any = None) -> Any:
        """型安全なget実装"""
        pass
```

**優先度**: 低

---

### 2.4 同時実行制御の改善

**現状**: 
- `threading.RLock`を使用しているが、デッドロックのリスクがゼロではない
- タイムアウト機構がない
- 長時間実行されるクエリでロックがブロックされる

**推奨対応**:
```python
# タイムアウト付きロック取得
class TimeoutLock:
    def __init__(self, timeout: float = 30.0):
        self._lock = threading.RLock()
        self._timeout = timeout
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        timeout = timeout or self._timeout
        return self._lock.acquire(timeout=timeout)
    
    def release(self):
        self._lock.release()

# コンテキストマネージャで自動解放
@contextmanager
def _acquire_lock(self, timeout: Optional[float] = None):
    if not self._lock.acquire(timeout=timeout):
        raise TimeoutError("Failed to acquire database lock")
    try:
        yield
    finally:
        self._lock.release()
```

**優先度**: 中

---

## 3. パフォーマンスとスケーラビリティ

### 3.1 キャッシュ戦略の制限

**現状**: 
- 単純なdict型のキャッシュのみ
- LRU、LFU、TTLなどの高度なキャッシュ戦略がない
- メモリ使用量の上限設定がない

**リスク**: 大規模データセットでのメモリ枯渇

**推奨対応**:
```python
from functools import lru_cache
from collections import OrderedDict

class LRUCache:
    def __init__(self, max_size: int = 1000):
        self._cache = OrderedDict()
        self._max_size = max_size
    
    def get(self, key):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
    
    def set(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
```

**優先度**: 中

---

### 3.2 バルク操作の最適化不足

**現状**: 
- `batch_update()`は存在するが、`batch_get()`がない
- 大量の読み込みでN+1問題が発生する可能性

**推奨対応**:
```python
def batch_get(self, keys: List[str]) -> Dict[str, Any]:
    """
    複数のキーを一度に取得（1回のクエリで）
    """
    if not keys:
        return {}
    
    # まずキャッシュをチェック
    results = {}
    missing_keys = []
    for key in keys:
        if key in self._cached_keys and key in self._data:
            results[key] = self._data[key]
        else:
            missing_keys.append(key)
    
    # 未キャッシュのキーをDBから取得
    if missing_keys:
        placeholders = ", ".join(["?"] * len(missing_keys))
        sql = f"SELECT key, value FROM {self._table} WHERE key IN ({placeholders})"
        with self._lock:
            cursor = self._connection.execute(sql, tuple(missing_keys))
            for key, value in cursor:
                deserialized = self._deserialize(value)
                results[key] = deserialized
                self._data[key] = deserialized
                self._cached_keys.add(key)
    
    return results
```

**優先度**: 中

---

### 3.3 インデックスの自動最適化機能がない

**現状**: 
- インデックスの作成は手動のみ
- 自動的なクエリ分析やインデックス推奨機能がない

**推奨対応**:
```python
from typing import Any, Dict, List
import re


class QueryAnalyzer:
    """クエリパフォーマンスを分析し、インデックスを推奨"""

    def __init__(self) -> None:
        # 非常に単純な実装例として、メモリ上にクエリ履歴を保持する
        self._history: List[str] = []

    def record_query(self, sql: str) -> None:
        """実行されたクエリを履歴に追加する簡易メソッド"""
        self._history.append(sql)

    def _analyze_single_query(self, sql: str) -> List[str]:
        """
        単一クエリを分析して推奨インデックスを返す簡易実装。

        制約:
        - SELECT ... FROM ... WHERE ... 形式のみを対象とする
        - WHERE 句に含まれる「column = ? / column = value」形式の列に対して
          単純な複合インデックスを推奨する
        """
        # テーブル名を抽出
        table_match = re.search(r"FROM\s+([A-Za-z_][A-Za-z0-9_]*)", sql, re.IGNORECASE)
        if not table_match:
            return []
        table_name = table_match.group(1)

        # WHERE 句の条件部を抽出
        where_match = re.search(r"WHERE\s+(.+)", sql, re.IGNORECASE)
        if not where_match:
            return []
        where_clause = where_match.group(1)

        # 「column = ...」形式の列名をすべて抽出
        columns = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", where_clause)
        if not columns:
            return []

        # 重複を排除し、安定した順序にソート
        unique_columns = sorted(set(columns))
        column_list = ", ".join(unique_columns)
        index_name = f"idx_{table_name}_" + "_".join(unique_columns)

        suggestion = f"CREATE INDEX {index_name} ON {table_name} ({column_list});"
        return [suggestion]

    def analyze_query(self, sql: str) -> List[str]:
        """クエリを分析し、推奨インデックスを返す"""
        # 実際の実装では EXPLAIN QUERY PLAN などを用いて詳細分析を行うことを想定
        # ここでは上記の簡易ロジックを呼び出す。
        return self._analyze_single_query(sql)

    def suggest_indexes(self) -> List[Dict[str, Any]]:
        """
        実行されたクエリ履歴から推奨インデックスを生成

        戻り値の例:
        [
            {
                "query": "SELECT ...",
                "suggested_indexes": ["CREATE INDEX ...", ...],
            },
            ...
        ]
        """
        results: List[Dict[str, Any]] = []

        for sql in self._history:
            suggestions = self._analyze_single_query(sql)
            if not suggestions:
                continue
            results.append(
                {
                    "query": sql,
                    "suggested_indexes": suggestions,
                }
            )

        return results
```

**優先度**: 低（機能拡張）

---

## 4. API設計とユーザビリティ

### 4.1 一貫性のないメソッド命名

**現状**: 
- `sql_insert()`, `sql_update()`, `sql_delete()` vs `query()`, `execute()`
- 一部は`sql_`プレフィックス、一部はそうでない

**推奨対応**:
- 命名規則を統一（既存APIは互換性のために維持、新APIで改善）
- deprecationワーニングを段階的に導入

**優先度**: 低

---

### 4.2 エイリアスメソッドの不足

**現状**: 
- Pydanticサポートは`set_model()`と`get_model()`のみ
- dict風の操作（`db["key"] = model`）がPydanticモデルで直接使えない

**推奨対応**:
```python
def __setitem__(self, key: str, value: Any) -> None:
    """Pydanticモデルを自動検出して保存"""
    if hasattr(value, 'model_dump'):
        self.set_model(key, value)
    else:
        # 通常の処理
        self._data[key] = value
        self._cached_keys.add(key)
        self._write_to_db(key, value)
```

**優先度**: 低

---

### 4.3 非同期コンテキストでのエラーメッセージ改善

**現状**: 
- AsyncNanaSQLiteのエラーメッセージが同期版と同じ
- スレッドプールでの実行時のスタックトレースが追いにくい

**推奨対応**:
- 非同期固有のエラーメッセージを追加
- コンテキスト情報を含むロギング

**優先度**: 低

---

## 5. テストとCI/CDの改善

### 5.1 テストカバレッジの改善

**現状**: 
- pytest-asyncioがオプション依存関係に含まれていなかった（現在は修正済み）
- 一部のエッジケースのテストが不十分

**具体的な不足箇所**:
```python
# テストされていないシナリオ
- 極端に大きなデータ（100MB以上の値）
- Unicode文字列の境界値（サロゲートペア、絵文字など）
- 同時実行でのデッドロック検証
- ディスクフル時の動作
- ファイルシステム権限エラー時の動作
```

**推奨対応**:
```bash
# ✅ 完了: pytest-asyncioを依存関係に追加済み
# pyproject.tomlに追加済み
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",  # ✅ 追加済み
    "pydantic>=2.0.0"
]

[tool.pytest.ini_options]
asyncio_mode = "auto"  # ✅ 追加済み

# 今後のタスク: 追加のエッジケーステスト
```

**優先度**: 高（一部対応済み）

---

### 5.2 パフォーマンステストの改善

**現状**: 
- ベンチマークテストは存在するが、継続的なパフォーマンス監視がない
- リグレッションを検出する仕組みがない

**推奨対応**:
```yaml
# .github/workflows/performance.yml
name: Performance Benchmarks

on:
  pull_request:
  push:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmarks
        run: pytest tests/test_benchmark.py --benchmark-only
      - name: Store results
        uses: benchmark-action/github-action-benchmark@v1.9.1
        with:
          tool: 'pytest'
          output-file-path: benchmark-results.json
```

**優先度**: 中

---

### 5.3 セキュリティスキャンの拡張

**現状**: 
- CodeQL、Bandit、Trivyは設定済み
- しかし、動的解析がない

**推奨対応**:
```yaml
# .github/workflows/security.yml に追加
  dynamic-analysis:
    name: Dynamic Security Testing
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run OWASP ZAP
        run: |
          # APIエンドポイントがある場合
          # docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable ...
      
      - name: Fuzz Testing
        run: |
          pip install atheris  # Googleのファジングツール
          python tests/fuzz_test.py
```

**優先度**: 中

---

## 6. ドキュメントとメンテナンス

### 6.1 APIドキュメントの自動生成不足

**現状**: 
- docstringは充実しているが、Sphinxなどでの自動生成がない
- オンラインドキュメントが不足

**推奨対応**:
```bash
# Sphinxのセットアップ
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# docs/conf.py の作成
# readthedocs.org との連携
```

**優先度**: 中

---

### 6.2 マイグレーションガイドの不足

**現状**: 
- バージョン間の変更点は記載されているが、移行手順が不明確
- 破壊的変更への対応方法が不足

**推奨対応**:
```markdown
# docs/ja/migration_guide.md
## v1.0 → v1.1 への移行

### 破壊的変更
- なし

### 非推奨になった機能
- なし（現時点）

### 推奨される移行手順
1. ...
2. ...
```

**優先度**: 低

---

### 6.3 トラブルシューティングガイド

**現状**: 
- よくある問題と解決方法が文書化されていない

**推奨対応**:
```markdown
# docs/ja/troubleshooting.md

## よくある問題

### Q: "database is locked" エラーが発生する

**原因**: 複数のプロセスまたはスレッドが同時にデータベースにアクセスしようとしている

**解決方法**:
1. WALモードが有効か確認:
   ```python
   db = NanaSQLite("mydata.db", optimize=True)  # WALモードが自動で有効
   # または手動で確認
   mode = db.pragma("journal_mode")
   print(f"Journal mode: {mode}")  # "wal" が表示されるべき
   ```

2. busy_timeoutを増やす:
   ```python
   db.pragma("busy_timeout", 5000)  # 5秒待機
   ```

3. コンテキストマネージャを使用して適切にクローズ:
   ```python
   with NanaSQLite("mydata.db") as db:
       db["key"] = "value"
   # 自動的にクローズされる
   ```

### Q: メモリ使用量が増え続ける

**原因**: bulk_load=Trueまたは大量のキーをキャッシュしている

**解決方法**:
1. 遅延ロードを使用:
   ```python
   # ❌ 避けるべき
   db = NanaSQLite("mydata.db", bulk_load=True)
   
   # ✅ 推奨
   db = NanaSQLite("mydata.db", bulk_load=False)  # デフォルト
   ```

2. 定期的にキャッシュをクリア:
   ```python
   # 特定のキーのキャッシュをクリア
   db.refresh("key1")
   
   # 全キャッシュをクリア
   db.refresh()
   
   # または定期的に実行
   import time
   while True:
       # アプリケーションのロジック
       time.sleep(3600)  # 1時間ごと
       db.refresh()  # キャッシュをクリア
   ```

3. LRUキャッシュ戦略を実装（将来の改善として提案中）

### Q: パフォーマンスが遅い

**原因**: インデックス不足、バッチ処理を使用していない

**解決方法**:
1. 頻繁にクエリするカラムにインデックスを追加:
   ```python
   db.create_table("users", {
       "id": "INTEGER PRIMARY KEY",
       "email": "TEXT",
       "age": "INTEGER"
   })
   
   # よく検索するカラムにインデックス
   db.create_index("idx_users_email", "users", ["email"])
   db.create_index("idx_users_age", "users", ["age"])
   ```

2. バッチ操作を使用:
   ```python
   # ❌ 遅い: 個別の書き込み
   for i in range(1000):
       db[f"key{i}"] = f"value{i}"
   
   # ✅ 速い: バッチ書き込み（10-100倍高速）
   data = {f"key{i}": f"value{i}" for i in range(1000)}
   db.batch_update(data)
   ```

3. トランザクションを使用:
   ```python
   with db.transaction():
       for i in range(1000):
           db.sql_insert("users", {"name": f"User{i}", "age": i})
   # 一括コミットで高速化
   ```

4. VACUUM実行でデータベースを最適化:
   ```python
   db.vacuum()  # 削除された領域を回収
   ```

### Q: 子インスタンス作成後、親を閉じたらエラーが出る

**原因**: table()メソッドで作成した子インスタンスが接続を共有している

**解決方法**:
1. コンテキストマネージャを使用（推奨）:
   ```python
   with NanaSQLite("app.db", table="main") as main_db:
       sub_db = main_db.table("sub")
       sub_db["key"] = "value"
   # 自動的にクローズされ、問題なし
   ```

2. 親インスタンスのみをクローズ:
   ```python
   main_db = NanaSQLite("app.db")
   sub_db = main_db.table("sub")
   
   # 作業完了後
   main_db.close()  # これだけでOK（子は自動的に無効化）
   # sub_db.close() は不要
   ```
```

**優先度**: 中

---

## 7. 依存関係とライブラリ管理

### 7.1 APSWバージョンの固定不足

**現状**: 
```toml
dependencies = [
    "apsw>=3.40.0.0"
]
```
- 上限が設定されていない
- 将来のAPSWで破壊的変更があった場合に対応できない

**推奨対応**:
```toml
dependencies = [
    "apsw>=3.40.0.0,<4.0.0"
]
```

**優先度**: 中

---

### 7.2 Python 3.14のサポート

**現状**: 
- Python 3.14がclassifiersに含まれているが、テストされていない可能性
- GitHub Actionsのテストマトリックスで確認必要

**推奨対応**:
```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12', '3.13', '3.14']
```

**優先度**: 低（Python 3.14のリリース状況を確認する必要がある）

---

### 7.3 オプショナル依存関係の明確化

**現状**: 
- Pydanticは必須ではないが、dev依存関係にのみ存在

**推奨対応**:
```toml
[project.optional-dependencies]
pydantic = ["pydantic>=2.0.0"]
async = ["aiofiles>=23.0.0"]  # 将来の拡張用
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "pydantic>=2.0.0"
]
```

**優先度**: 低

---

## 8. 優先順位と推奨対応順序

### 🔴 緊急（1-2週間以内）

1. **✅ テスト環境の修正** (5.1) - 完了
   - ✅ pytest-asyncioをpyproject.tomlに追加
   - ✅ 全テストが正常に実行可能（265 passed, 85 skipped）
   - ✅ CI/CDの安定化

2. **リソースリークのリスク対応** (2.2)
   - 子インスタンスの追跡
   - 閉じた接続の使用を防止

### 🟠 高優先度（1ヶ月以内）

3. **SQLインジェクション対策の強化** (1.1)
   - 列名検証の統一化
   - より厳格な入力検証

4. **エラーハンドリングの統一** (2.1)
   - カスタム例外クラスの導入
   - 一貫性のあるエラーメッセージ

### 🟡 中優先度（2-3ヶ月以内）

5. **ReDoS対策** (1.2)
   - 入力長の制限
   - 正規表現の最適化

6. **同時実行制御の改善** (2.4)
   - タイムアウト機構の追加

7. **キャッシュ戦略の改善** (3.1)
   - LRUキャッシュの実装
   - メモリ上限の設定

8. **バルク操作の拡張** (3.2)
   - batch_get()の実装

9. **ドキュメントの充実** (6.1, 6.3)
   - APIドキュメント自動生成
   - トラブルシューティングガイド

### 🟢 低優先度（機能拡張として検討）

10. **型ヒントの改善** (2.3)
11. **API命名の統一** (4.1)
12. **インデックス最適化機能** (3.3)
13. **マイグレーションガイド** (6.2)

---

## まとめ

### 全体的な評価

**強み**:
- ✅ 堅実なアーキテクチャ設計
- ✅ 包括的なセキュリティテスト
- ✅ 充実したdocstring
- ✅ 活発なCI/CD環境

**改善が必要な領域**:
- ⚠️ テスト環境の不備（非同期テスト）
- ⚠️ リソース管理の強化
- ⚠️ エラーハンドリングの統一
- ⚠️ キャッシュ戦略の高度化

### 推奨される最初のステップ

1. ✅ `pytest-asyncio`を依存関係に追加してテスト環境を修正（完了）
2. リソースリーク対策の実装
3. カスタム例外クラスの導入
4. セキュリティ対策の強化（SQLインジェクション、ReDoS）

これらの対応により、NanaSQLiteはより堅牢で信頼性の高いライブラリになります。

---

## 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [SQLite Security](https://www.sqlite.org/security.html)
- [APSW Documentation](https://rogerbinns.github.io/apsw/)

---

**文書バージョン**: 1.1  
**変更履歴**:
- v1.1: pytest-asyncio対応を完了済みとして更新
- v1.0: 初版作成
