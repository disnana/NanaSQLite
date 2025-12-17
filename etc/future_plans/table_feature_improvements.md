# table()機能の将来的な改善案

**作成日**: 2025年12月17日  
**ステータス**: 検討中（ユーザーフィードバック待ち）

---

## 📋 概要

table()機能に関する軽微な問題に対する将来的な改善提案です。
提案Aのドキュメント改善は即座に実施されましたが、以下の提案は将来的な実装として保留されています。

---

## 🔍 問題1: 同一テーブルへの複数インスタンスでキャッシュ不整合

### 提案B: 重複インスタンス検出警告

**ステータス**: 検討推奨（オプション）

#### 実装内容

同じテーブルへの複数インスタンス作成時に警告を表示する機能。

```python
import weakref
import warnings

class NanaSQLite(MutableMapping):
    _table_registry = {}  # {(db_path, table_name): weakref(instance)}
    
    def table(self, table_name: str):
        """
        サブテーブル用のNanaSQLiteインスタンスを取得
        
        注意: 同じテーブルに対して複数のインスタンスを作成すると警告が表示されます。
        各インスタンスは独立したキャッシュを持つため、キャッシュレベルでの
        整合性が保証されません。
        
        Args:
            table_name: テーブル名
        
        Returns:
            NanaSQLite: 新しいテーブルインスタンス
        
        Raises:
            UserWarning: 同じテーブルに対して既にインスタンスが存在する場合
        
        Example:
            >>> main_db = NanaSQLite("app.db")
            >>> users_db = main_db.table("users")
            >>> # 同じテーブルに再度インスタンスを作成すると警告
            >>> users_db2 = main_db.table("users")  # UserWarning発生
        """
        key = (self._db_path, table_name)
        
        # 既存インスタンスがあれば警告
        if key in self._table_registry:
            existing = self._table_registry[key]()
            if existing is not None:
                warnings.warn(
                    f"Table '{table_name}' already has an active instance. "
                    f"Multiple instances for the same table may cause cache inconsistency. "
                    f"Consider reusing the existing instance instead of creating a new one.\n"
                    f"Recommended: Store and reuse the first instance.",
                    UserWarning,
                    stacklevel=2
                )
        
        new_instance = NanaSQLite(
            self._db_path,
            table=table_name,
            _shared_connection=self._connection,
            _shared_lock=self._lock
        )
        
        # weakrefで登録（ガベージコレクション対応）
        self._table_registry[key] = weakref.ref(new_instance)
        return new_instance
```

#### 評価

| 項目 | 評価 |
|------|------|
| 優先度 | 🟡 中 |
| 推奨度 | ⭐⭐⭐⭐☆ |
| パフォーマンス影響 | 🟢 微小（weakrefチェックのみ、10ns程度） |
| 実装難易度 | ⭐⭐☆☆☆（簡単） |
| 実装工数 | 2-3時間 |
| コード追加量 | 約50行 |

#### メリット

1. **開発時の問題早期発見**
   - 誤用を開発段階で検出できる
   - ユニットテスト実行時に警告が表示される

2. **ユーザー教育**
   - 警告メッセージで正しい使い方を学べる
   - ベストプラクティスへの誘導

3. **パフォーマンス向上**
   - 不要なインスタンス作成を防ぐ
   - メモリ使用量の削減

#### デメリット

1. **若干のオーバーヘッド**
   - weakref管理のコスト（微小）
   - レジストリ検索のコスト（微小）

2. **テストコードの増加**
   - 警告の抑制が必要な場合がある
   - テストケースの追加が必要

3. **既存コードへの影響**
   - 警告が表示される既存コードがあるかもしれない
   - ユーザーが混乱する可能性

#### 実装時の注意点

1. **weakrefの適切な管理**
   ```python
   # インスタンスがGCされた場合の対応
   if key in self._table_registry:
       existing = self._table_registry[key]()
       if existing is None:
           # 既にGCされている場合は削除
           del self._table_registry[key]
   ```

2. **スレッドセーフ性**
   ```python
   # レジストリへのアクセスをロックで保護
   _registry_lock = threading.Lock()
   
   with self._registry_lock:
       # レジストリ操作
   ```

3. **警告の抑制方法をドキュメント化**
   ```python
   # 意図的に複数インスタンスを作る場合
   import warnings
   with warnings.catch_warnings():
       warnings.simplefilter("ignore", UserWarning)
       inst2 = main_db.table("users")
   ```

#### テストケース

```python
def test_duplicate_table_instance_warning():
    """同一テーブルへの複数インスタンス作成で警告"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        inst1 = main_db.table("users")
        
        # 2つ目のインスタンス作成で警告が発生
        with pytest.warns(UserWarning, match="already has an active instance"):
            inst2 = main_db.table("users")
        
        # GC後は警告が出ない
        del inst1
        import gc
        gc.collect()
        
        inst3 = main_db.table("users")  # 警告なし
        
        main_db.close()
    finally:
        os.unlink(db_path)
```

#### 実装スケジュール

**フェーズ**: 2  
**期間**: 1-2日  
**依存**: ドキュメント改善（提案A）完了後

---

### 提案C: 共有キャッシュ機構

**ステータス**: 保留（現時点では不要）

#### 実装内容

テーブルごとに共有キャッシュを使用し、同じテーブルの複数インスタンスで
キャッシュを同期する機構。

```python
import threading
from typing import Dict, Tuple

class SharedCacheManager:
    """
    テーブルごとの共有キャッシュ管理
    
    同じ(db_path, table_name)の組み合わせに対して、
    共有されたキャッシュディクショナリを提供します。
    """
    
    def __init__(self):
        self._caches: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._locks: Dict[Tuple[str, str], threading.RLock] = {}
        self._manager_lock = threading.Lock()
    
    def get_cache(self, db_path: str, table_name: str) -> Tuple[Dict, threading.RLock]:
        """
        指定されたテーブルの共有キャッシュとロックを取得
        
        Args:
            db_path: データベースファイルパス
            table_name: テーブル名
        
        Returns:
            (shared_cache, cache_lock) のタプル
        """
        key = (db_path, table_name)
        
        with self._manager_lock:
            if key not in self._caches:
                self._caches[key] = {}
                self._locks[key] = threading.RLock()
            
            return self._caches[key], self._locks[key]
    
    def clear_cache(self, db_path: str, table_name: str) -> None:
        """特定のテーブルのキャッシュをクリア"""
        key = (db_path, table_name)
        with self._manager_lock:
            if key in self._caches:
                with self._locks[key]:
                    self._caches[key].clear()

# グローバルインスタンス
_shared_cache_manager = SharedCacheManager()


class NanaSQLite(MutableMapping):
    def __init__(self, db_path: str, table: str = "data", ...):
        self._db_path = db_path
        self._table = table
        
        # 共有キャッシュを使用
        self._data, self._cache_lock = _shared_cache_manager.get_cache(
            db_path, table
        )
        
        # 既存の初期化処理...
```

#### 評価

| 項目 | 評価 |
|------|------|
| 優先度 | 🟢 低 |
| 推奨度 | ⭐⭐☆☆☆ |
| パフォーマンス影響 | 🟡 小（キャッシュ管理の複雑化） |
| 実装難易度 | ⭐⭐⭐⭐☆（難しい） |
| 実装工数 | 1-2週間 |
| コード変更量 | 大規模（200-300行） |

#### メリット

1. **完全なキャッシュ整合性**
   - 複数インスタンスでもキャッシュが同期される
   - ユーザーが意識せずに安全に使える

2. **柔軟性の向上**
   - 同じテーブルへの複数インスタンスが安全に使える
   - より自由な設計が可能

#### デメリット

1. **実装が非常に複雑**
   - グローバルステートの管理
   - スレッドセーフ性の確保が困難
   - デバッグが難しい

2. **パフォーマンスへの影響**
   - グローバルロックの競合
   - キャッシュ管理のオーバーヘッド

3. **設計の大幅な変更**
   - 既存のキャッシュ機構を全面的に変更
   - 後方互換性の維持が困難
   - 既存テストの大幅な修正が必要

4. **メモリ管理の複雑化**
   - キャッシュのライフサイクル管理
   - メモリリークのリスク増加

#### 実装しない理由

1. **現状で十分**
   - 提案A（ドキュメント改善）で誤用を防げる
   - 提案B（警告）で問題を検出できる

2. **コストが高すぎる**
   - 実装工数が大きい
   - リスクが高い（バグの混入、パフォーマンス低下）

3. **需要が不明**
   - ユーザーから要望がない
   - 実際に必要とされるかわからない

4. **代替案が十分**
   - ドキュメント改善で解決可能
   - ベストプラクティスの啓蒙が効果的

#### 再検討の条件

以下の条件が満たされた場合、再検討を行う：

1. **ユーザーからの強い要望**
   - 複数のユーザーから同様の要望がある
   - 具体的なユースケースが提示される

2. **代替案の効果が限定的**
   - ドキュメント改善だけでは不十分
   - 誤用が頻繁に発生する

3. **技術的な解決策が見つかる**
   - よりシンプルな実装方法が発見される
   - パフォーマンス問題を回避できる

---

## 🔍 問題2: close後のサブインスタンスアクセス

### 提案B: 接続状態チェックの追加

**ステータス**: 検討推奨

#### 実装内容

すべての操作前に接続状態を確認する機能。

```python
import weakref
from typing import Optional

class NanaSQLite(MutableMapping):
    def __init__(self, db_path: str, table: str = "data", ...,
                 _shared_connection=None, _shared_lock=None, _parent=None):
        # 既存の初期化処理...
        
        self._closed = False  # 接続状態フラグ
        self._parent: Optional[weakref.ref] = _parent  # 親インスタンスへの参照
    
    def _check_connection(self):
        """
        接続が有効か確認
        
        Raises:
            RuntimeError: 接続が閉じられている場合
        """
        # 接続の所有者の場合
        if self._is_connection_owner:
            if self._closed:
                raise RuntimeError(
                    "Database connection is closed. "
                    "Cannot perform operations on a closed database.\n"
                    "Tip: Use context manager (with statement) to ensure proper cleanup."
                )
        # 子インスタンスの場合、親の状態を確認
        else:
            parent = self._parent() if self._parent else None
            if parent is None:
                # 親インスタンスがGCされた場合
                # これは通常起こらないが、念のためチェック
                pass
            elif hasattr(parent, '_closed') and parent._closed:
                raise RuntimeError(
                    "Parent database connection is closed. "
                    "Cannot perform operations when parent is closed.\n"
                    "Tip: Keep parent instance alive or use context manager."
                )
    
    def close(self) -> None:
        """
        データベース接続を閉じる

        注意: table()メソッドで作成されたインスタンスは接続を共有しているため、
        接続の所有者（最初に作成されたインスタンス）のみが接続を閉じます。
        接続が閉じられた後、このインスタンスおよび子インスタンスは使用できなくなります。
        """
        if self._is_connection_owner and not self._closed:
            self._connection.close()
            self._closed = True
    
    # すべての操作メソッドに_check_connection()を追加
    
    def __getitem__(self, key: str) -> Any:
        """dict[key] - 遅延ロード後、メモリから取得"""
        self._check_connection()
        if self._ensure_cached(key):
            return self._data[key]
        raise KeyError(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """dict[key] = value - 即時書き込み + メモリ更新"""
        self._check_connection()
        self._data[key] = value
        self._cached_keys.add(key)
        self._write_to_db(key, value)
    
    def __delitem__(self, key: str) -> None:
        """del dict[key] - 即時削除"""
        self._check_connection()
        if not self._ensure_cached(key):
            raise KeyError(key)
        del self._data[key]
        self._cached_keys.add(key)
        self._delete_from_db(key)
    
    def __contains__(self, key: str) -> bool:
        """key in dict - キーの存在確認"""
        self._check_connection()
        # 既存の処理...
    
    def __len__(self) -> int:
        """len(dict) - 全件数を返す"""
        self._check_connection()
        # 既存の処理...
    
    def __iter__(self):
        """for key in dict - 全キーをイテレート"""
        self._check_connection()
        # 既存の処理...
    
    def keys(self):
        """dict.keys() - 全キーを返す"""
        self._check_connection()
        # 既存の処理...
    
    def values(self):
        """dict.values() - 全値を返す"""
        self._check_connection()
        # 既存の処理...
    
    def items(self):
        """dict.items() - 全アイテムを返す"""
        self._check_connection()
        # 既存の処理...
    
    def get(self, key: str, default=None):
        """dict.get() - デフォルト値付きで取得"""
        self._check_connection()
        # 既存の処理...
    
    def pop(self, key: str, *args):
        """dict.pop() - キーを削除して値を返す"""
        self._check_connection()
        # 既存の処理...
    
    def clear(self) -> None:
        """dict.clear() - 全データを削除"""
        self._check_connection()
        # 既存の処理...
    
    def update(self, mapping=None, **kwargs) -> None:
        """dict.update() - 複数のキーを更新"""
        self._check_connection()
        # 既存の処理...
    
    def setdefault(self, key: str, default=None):
        """dict.setdefault() - キーがなければ設定"""
        self._check_connection()
        # 既存の処理...
    
    # その他のメソッドにも同様に追加...
    
    def table(self, table_name: str):
        """
        サブテーブル用のNanaSQLiteインスタンスを取得

        新しいインスタンスを作成しますが、SQLite接続とロックは共有します。
        これにより、複数のテーブルインスタンスが同じ接続を使用して
        スレッドセーフに動作します。

        :param table_name: テーブル名
        :return NanaSQLite: 新しいテーブルインスタンス
        """
        self._check_connection()  # 親が閉じられていないか確認
        
        return NanaSQLite(
            self._db_path,
            table=table_name,
            _shared_connection=self._connection,
            _shared_lock=self._lock,
            _parent=weakref.ref(self)  # 親への参照を渡す
        )
```

#### 非同期版の実装

```python
class AsyncNanaSQLite:
    async def _check_connection(self):
        """非同期版の接続チェック"""
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        # 同期版DBの接続状態をチェック
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db._check_connection
        )
    
    async def aget(self, key: str, default: Any = None) -> Any:
        await self._check_connection()
        # 既存の処理...
    
    async def aset(self, key: str, value: Any) -> None:
        await self._check_connection()
        # 既存の処理...
    
    # その他のメソッドにも同様に追加...
```

#### 評価

| 項目 | 評価 |
|------|------|
| 優先度 | 🟡 中 |
| 推奨度 | ⭐⭐⭐⭐☆ |
| パフォーマンス影響 | 🟢 微小（フラグチェックのみ、数ns） |
| 実装難易度 | ⭐⭐⭐☆☆（中程度） |
| 実装工数 | 4-6時間 |
| コード変更量 | 約100-150行 |

#### メリット

1. **より安全な実装**
   - close後のアクセスを完全に防げる
   - エラーメッセージが明確

2. **デバッグの容易化**
   - 問題の原因が明確になる
   - スタックトレースで特定しやすい

3. **ベストプラクティスの強制**
   - コンテキストマネージャーの使用を促進
   - より堅牢なコード

#### デメリット

1. **各操作でのオーバーヘッド**
   - 1操作あたり10-20ns程度
   - 100万回操作で10-20ms程度の影響

2. **コード変更の影響範囲が広い**
   - 全操作メソッドに追加が必要
   - テストケースの更新が必要

3. **後方互換性への影響**
   - close後のキャッシュアクセスが不可に
   - 既存コードでエラーが発生する可能性

#### パフォーマンス測定

```python
import time

# ベンチマーク
def benchmark_check_overhead():
    db = NanaSQLite("test.db")
    
    # チェックなし
    start = time.perf_counter()
    for i in range(1000000):
        _ = db._closed  # 単純なフラグアクセス
    elapsed1 = time.perf_counter() - start
    
    # チェックあり
    start = time.perf_counter()
    for i in range(1000000):
        db._check_connection()
    elapsed2 = time.perf_counter() - start
    
    overhead = (elapsed2 - elapsed1) * 1000  # ms
    print(f"100万回のチェック: {overhead:.2f}ms")
    print(f"1回あたり: {overhead/1000:.2f}ns")
    
    db.close()

# 予想結果: 10-20ms程度（無視できるレベル）
```

#### テストケース

```python
def test_access_after_close():
    """close後のアクセスでエラー"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        sub_db = main_db.table("sub")
        
        # データ書き込み
        sub_db["key"] = "value"
        
        # メインをclose
        main_db.close()
        
        # 読み取りでエラー（キャッシュヒットでも）
        with pytest.raises(RuntimeError, match="connection is closed"):
            _ = sub_db["key"]
        
        # 書き込みでエラー
        with pytest.raises(RuntimeError, match="connection is closed"):
            sub_db["key2"] = "value2"
    finally:
        os.unlink(db_path)


async def test_async_access_after_close():
    """非同期版：close後のアクセスでエラー"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = AsyncNanaSQLite(db_path, table="main")
        await main_db._ensure_initialized()
        
        sub_db = await main_db.table("sub")
        await sub_db.aset("key", "value")
        
        await main_db.close()
        
        with pytest.raises(RuntimeError, match="connection is closed"):
            await sub_db.aget("key")
    finally:
        os.unlink(db_path)
```

#### 実装スケジュール

**フェーズ**: 2  
**期間**: 2-3日  
**依存**: ドキュメント改善（提案A）完了後  
**並行実装**: 提案B（重複検出警告）と同時実装可能

---

## 📊 実装判断基準

### 提案Bを実装する条件

以下のいずれかが該当する場合、実装を検討：

1. **ユーザーからの要望**
   - 重複インスタンスの問題が報告される
   - より厳格なエラーチェックが求められる

2. **プロジェクトの方針**
   - より安全な実装を優先する方針
   - エンタープライズ向けに堅牢性を重視

3. **コミュニティの反応**
   - ドキュメント改善後のフィードバック
   - 実際の誤用事例の報告

### 提案Cを実装しない理由

- 実装コストが高すぎる
- 現状で十分な品質が確保されている
- ユーザーからの要望がない
- 代替案（提案A, B）で十分

---

## 🎯 推奨アクション

### 即座に実施（完了）

✅ **提案A: ドキュメント改善**
- README.mdの更新
- docstringの改善
- ベストプラクティスの記載

### 短期的に検討（1-2週間）

**実施判断**: ユーザーフィードバック収集後

- **提案B（問題1）**: 重複インスタンス検出警告
  - 推奨度: ⭐⭐⭐⭐☆
  - 実装コスト: 低
  
- **提案B（問題2）**: 接続状態チェック
  - 推奨度: ⭐⭐⭐⭐☆
  - 実装コスト: 中

### 長期的に保留

**実施判断**: 具体的な要望があった場合のみ

- **提案C**: 共有キャッシュ機構
  - 推奨度: ⭐⭐☆☆☆
  - 実装コスト: 高

---

## 📝 更新履歴

- 2025-12-17: 初版作成
  - 提案B, Cの詳細を記載
  - 実装判断基準を明記

