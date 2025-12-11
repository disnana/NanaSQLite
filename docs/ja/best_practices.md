# NanaSQLite ベストプラクティス

本番環境でNanaSQLiteを効果的に使用するための包括的なガイドです。

## 目次

- [パフォーマンス最適化](#パフォーマンス最適化)
- [セキュリティガイドライン](#セキュリティガイドライン)
- [エラーハンドリング](#エラーハンドリング)
- [リソース管理](#リソース管理)
- [デザインパターン](#デザインパターン)
- [テスト](#テスト)

---

## パフォーマンス最適化

### 適切なキャッシュ戦略の選択

**遅延ロード（デフォルト）**
```python
# 最適: 大規模データベース、まばらなアクセスパターン
db = NanaSQLite("large.db")
# アクセス時のみデータをロード
user = db["user_123"]  # 初回アクセス: DBからロード
user = db["user_123"]  # 2回目のアクセス: メモリから
```

**一括ロード**
```python
# 最適: 小規模データベース（<100MB）、ほとんどのキーへの頻繁なアクセス
db = NanaSQLite("small.db", bulk_load=True)
# 起動時に全データをロード
# 以降の読み込みはすべてメモリから（超高速）
```

**判断マトリクス:**

| データベースサイズ | アクセスパターン | 推奨 |
|--------------|----------------|----------------|
| < 10MB | 読み込み重視 | `bulk_load=True` |
| 10-100MB | ほとんどのキーにアクセス | `bulk_load=True` |
| 100MB-1GB | 一部のキーにアクセス | `bulk_load=False`（デフォルト）|
| > 1GB | 任意のパターン | `bulk_load=False`（デフォルト）|

### バッチ操作の使用

**❌ アンチパターン: 個別の書き込み**
```python
# 遅い: 1000個の別々のトランザクション
for i in range(1000):
    db[f"user_{i}"] = {"name": f"User{i}"}
```

**✅ ベストプラクティス: バッチ書き込み**
```python
# 速い: 単一トランザクション（10-100倍高速）
users = {f"user_{i}": {"name": f"User{i}"} for i in range(1000)}
db.batch_update(users)
```

**パフォーマンス比較:**

| 操作 | 個別 | バッチ | 高速化 |
|-----------|-----------|-------|---------|
| 100書き込み | ~200ms | ~2ms | 100倍 |
| 1000書き込み | ~2000ms | ~15ms | 133倍 |
| 10000書き込み | ~20000ms | ~150ms | 133倍 |

### SQLiteキャッシュサイズの最適化

`cache_size_mb`パラメータはSQLiteの内部ページキャッシュ（PRAGMA cache_size）を制御し、NanaSQLiteの辞書キャッシュではありません。これはSQLiteがメモリに保持するデータベースページ数に影響し、ディスクI/Oを高速化します。

```python
# デフォルト: 64MB SQLiteページキャッシュ（ほとんどの場合に適切）
db = NanaSQLite("data.db")

# 大規模データセット: SQLiteページキャッシュを増加
db = NanaSQLite("large.db", cache_size_mb=256)

# メモリ制約: SQLiteページキャッシュを削減
db = NanaSQLite("data.db", cache_size_mb=32)
```

**ガイドライン:**
- **小規模DB（<100MB）**: 32-64MB SQLiteキャッシュ
- **中規模DB（100MB-1GB）**: 128-256MB SQLiteキャッシュ
- **大規模DB（>1GB）**: 256-512MB SQLiteキャッシュ

**注意:** このパラメータはNanaSQLiteの内部辞書キャッシュ（`_data`）が使用するメモリには影響しません。辞書キャッシュはロードされた値をPythonメモリに保存します。これを制御するには、`bulk_load=False`（デフォルト）で遅延ロードを使用してください。

### 自動クリーンアップのためのコンテキストマネージャ

**✅ 常にコンテキストマネージャを使用**
```python
with NanaSQLite("data.db") as db:
    db["key"] = "value"
# 自動的にクローズされ、リソースが解放される
```

**❌ 手動管理を避ける**
```python
db = NanaSQLite("data.db")
db["key"] = "value"
db.close()  # 忘れやすい！
```

---

## セキュリティガイドライン

### SQLインジェクションの防止

**✅ パラメータバインディングを使用**
```python
# 安全: パラメータは適切にエスケープされる
results = db.query(
    table_name="users",
    where="name = ?",
    parameters=(user_input,)
)
```

**❌ ユーザー入力を連結しない**
```python
# 危険: SQLインジェクションの脆弱性
# 絶対にやらないでください！
db.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
```

### ファイルパスの検証

```python
import os

def safe_db_path(user_input: str) -> str:
    """ディレクトリトラバーサルを防ぐためにデータベースパスを検証"""
    # パス区切り文字と相対パスを削除
    if ".." in user_input or "/" in user_input or "\\" in user_input:
        raise ValueError("無効なデータベースパス")
    
    # 安全なディレクトリ内にあることを確認
    safe_dir = "/var/lib/myapp/databases"
    return os.path.join(safe_dir, f"{user_input}.db")

# 使用方法
db_path = safe_db_path(user_provided_name)
db = NanaSQLite(db_path)
```

### 機密データの保護

```python
# 平文でシークレットを保存しない
# ❌ 悪い例
db["config"] = {
    "api_key": "sk-1234567890abcdef",
    "password": "mypassword123"
}

# ✅ 良い例: 機密値を暗号化
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

encrypted_api_key = cipher.encrypt(b"sk-1234567890abcdef")
db["config"] = {
    "api_key": encrypted_api_key.decode(),
    "password_hash": hash_password("mypassword123")
}
```

### ファイルパーミッション

```python
import os
import stat

# 制限されたパーミッションでデータベースを作成
db = NanaSQLite("secure.db")
db.close()

# ファイルパーミッションを所有者のみの読み書きに設定
os.chmod("secure.db", stat.S_IRUSR | stat.S_IWUSR)
```

---

## エラーハンドリング

### 存在しないキーの適切な処理

**✅ デフォルト値付きでget()を使用**
```python
# 推奨: 例外処理が不要
value = db.get("key", default="デフォルト値")
```

**✅ 必須キーにはtry/exceptを使用**
```python
try:
    value = db["required_key"]
except KeyError:
    logger.error("必須設定が欠落しています")
    raise ConfigurationError("required_keyが欠落しています")
```

### データベースエラーの処理

```python
import apsw
import logging

logger = logging.getLogger(__name__)

try:
    with NanaSQLite("data.db") as db:
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT UNIQUE"
        })
        db.sql_insert("users", {"email": "test@example.com"})
except apsw.Error as e:
    logger.error(f"データベースエラー: {e}")
    # 適切に処理（再試行、フォールバック等）
```

### 挿入前のデータ検証

```python
def save_user(db: NanaSQLite, user_data: dict) -> bool:
    """検証付きでユーザーを保存"""
    # 必須フィールドの検証
    required = ["name", "email", "age"]
    if not all(field in user_data for field in required):
        raise ValueError(f"必須フィールドが欠落: {required}")
    
    # データ型の検証
    if not isinstance(user_data["age"], int):
        raise TypeError("年齢は整数である必要があります")
    
    if user_data["age"] < 0 or user_data["age"] > 150:
        raise ValueError("無効な年齢")
    
    # 保存
    db[f"user_{user_data['email']}"] = user_data
    return True
```

---

## リソース管理

### Webアプリケーション用の接続プーリング

**FastAPIの例**
```python
from fastapi import FastAPI, Depends
from nanasqlite import AsyncNanaSQLite
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動: データベース接続を作成
    app.state.db = AsyncNanaSQLite("app.db", max_workers=10)
    yield
    # シャットダウン: データベースをクローズ
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

async def get_db() -> AsyncNanaSQLite:
    """データベースの依存性注入"""
    return app.state.db

@app.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncNanaSQLite = Depends(get_db)):
    return await db.aget(f"user_{user_id}")
```

### メモリ管理

```python
# 長時間実行プロセスでは、定期的に未使用のキャッシュをクリア
class CachedDB:
    def __init__(self, db_path: str):
        self.db = NanaSQLite(db_path)
        self.access_count = 0
    
    def get(self, key: str):
        self.access_count += 1
        
        # 10000操作ごとにキャッシュを更新
        if self.access_count % 10000 == 0:
            self.db.refresh()  # キャッシュをクリア
            
        return self.db.get(key)
```

---

## デザインパターン

### 関心事の分離

```python
# 異なる関心事に異なるテーブルを使用
class AppDatabase:
    def __init__(self, db_path: str):
        self.users = NanaSQLite(db_path, table="users")
        self.sessions = NanaSQLite(db_path, table="sessions")
        self.cache = NanaSQLite(db_path, table="cache")
        self.config = NanaSQLite(db_path, table="config")
    
    def close_all(self):
        self.users.close()
        self.sessions.close()
        self.cache.close()
        self.config.close()

# 使用方法
app_db = AppDatabase("app.db")
app_db.users["alice"] = {"role": "admin"}
app_db.sessions["sess_123"] = {"user_id": "alice"}
app_db.close_all()
```

### リポジトリパターン

```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str
    age: int

class UserRepository:
    def __init__(self, db: NanaSQLite):
        self.db = db
    
    def save(self, user: User) -> None:
        self.db[f"user_{user.id}"] = {
            "name": user.name,
            "email": user.email,
            "age": user.age
        }
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        data = self.db.get(f"user_{user_id}")
        if data:
            return User(id=user_id, **data)
        return None
    
    def find_all(self) -> List[User]:
        users = []
        for key in self.db.keys():
            if key.startswith("user_"):
                user_id = key[5:]  # "user_"プレフィックスを削除
                data = self.db[key]
                users.append(User(id=user_id, **data))
        return users

# 使用方法
with NanaSQLite("app.db") as db:
    repo = UserRepository(db)
    
    user = User(id="1", name="Alice", email="alice@example.com", age=30)
    repo.save(user)
    
    found = repo.find_by_id("1")
    print(found.name)  # Alice
```

---

## テスト

### ユニットテスト

```python
import pytest
import tempfile
import os

@pytest.fixture
def temp_db():
    """テスト用の一時データベースを作成"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)

def test_basic_operations(temp_db):
    with NanaSQLite(temp_db) as db:
        # 書き込みのテスト
        db["test_key"] = {"value": 123}
        
        # 読み込みのテスト
        assert db["test_key"] == {"value": 123}
        
        # 削除のテスト
        del db["test_key"]
        assert "test_key" not in db

def test_batch_operations(temp_db):
    with NanaSQLite(temp_db) as db:
        # バッチ書き込みのテスト
        data = {f"key_{i}": i for i in range(100)}
        db.batch_update(data)
        
        assert len(db) == 100
        assert db["key_50"] == 50
```

### モック

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    mock_db = MagicMock(spec=NanaSQLite)
    mock_db.get.return_value = {"name": "テストユーザー"}
    
    # データベースを使用する関数
    def get_user_name(db, user_id):
        user = db.get(f"user_{user_id}")
        return user["name"] if user else None
    
    result = get_user_name(mock_db, "123")
    assert result == "テストユーザー"
    mock_db.get.assert_called_once_with("user_123")
```

---

## まとめ

**重要なポイント:**

1. ✅ 小規模で頻繁にアクセスされるデータベースには`bulk_load=True`を使用
2. ✅ 100以上の書き込みには常にバッチ操作を使用
3. ✅ 自動クリーンアップのためにコンテキストマネージャ（`with`文）を使用
4. ✅ SQLインジェクションを防ぐためにパラメータバインディングを使用
5. ✅ ユーザー入力、特にファイルパスを検証
6. ✅ `get()`とtry/exceptでエラーを適切に処理
7. ✅ 異なるテーブルで関心事を分離
8. ✅ 一時データベースでテスト
9. ✅ 長時間実行プロセスでメモリ使用量を監視
10. ✅ 非同期フレームワーク（FastAPI、aiohttp）には非同期版を使用

**避けるべき一般的な落とし穴:**

1. ❌ 大規模データベース（>1GB）で`bulk_load=True`を使用
2. ❌ バッチ操作の代わりに個別の書き込み
3. ❌ データベースのクローズを忘れる（`with`文を使用）
4. ❌ 文字列連結によるSQLインジェクション
5. ❌ 暗号化せずに機密データを保存
6. ❌ KeyError例外を無視
7. ❌ ユーザー入力を検証しない

詳細な例については以下を参照してください:
- [チュートリアル](tutorial.md) - 段階的な学習ガイド
- [APIリファレンス](reference.md) - 完全なメソッドドキュメント
- [非同期ガイド](async_guide.md) - async/awaitの使用方法
