# 追加便利機能の提案 / Proposals for Additional Convenient Features

## 提案の背景 (Background)

NanaSQLiteは現在、Pydantic互換性、直接SQL実行、そして包括的なSQLiteラッパー関数を提供しています。さらなる利便性向上のため、以下の機能を提案します。

---

## 提案1: ORM風のモデル定義 (ORM-style Model Definition)

### 概要
Pydanticだけでなく、独自の軽量なモデルクラスを提供し、より直感的なデータ操作を可能にします。

### 実装例
```python
from nanasqlite import NanaSQLite, Model, Field

class User(Model):
    __table__ = "users"
    
    id: int = Field(primary_key=True, autoincrement=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True)
    age: int = Field(default=0)
    created_at: str = Field(auto_now_add=True)

db = NanaSQLite("app.db")

# テーブル自動作成
User.create_table(db)

# レコード作成
user = User(name="Alice", email="alice@example.com", age=25)
user.save(db)

# クエリ
users = User.query(db).filter(age__gte=18).order_by("name").all()
user = User.query(db).get(id=1)

# 更新
user.age = 26
user.save(db)

# 削除
user.delete(db)
```

### メリット
- Pydanticなしでも型安全なモデル定義
- テーブル自動生成
- クエリビルダーによる直感的なデータ操作
- バリデーション機能

---

## 提案2: マイグレーション機能 (Migration Support)

### 概要
データベーススキーマの変更を管理・追跡する機能。

### 実装例
```python
from nanasqlite import NanaSQLite, Migration

db = NanaSQLite("app.db")

# マイグレーション定義
class AddPhoneToUsers(Migration):
    version = "001"
    
    def up(self, db):
        db.alter_table_add_column("users", "phone", "TEXT")
        db.create_index("idx_users_phone", "users", ["phone"])
    
    def down(self, db):
        # SQLiteはカラム削除非対応なので、テーブル再作成が必要
        pass

# マイグレーション実行
db.run_migration(AddPhoneToUsers)

# マイグレーション履歴
history = db.get_migration_history()
```

### メリット
- スキーマ変更の追跡
- チーム開発での一貫性
- ロールバック対応

---

## 提案3: クエリビルダー (Query Builder)

### 概要
SQLを書かずに複雑なクエリを構築できる流暢なインターフェース。

### 実装例
```python
from nanasqlite import NanaSQLite, QueryBuilder

db = NanaSQLite("app.db")

# 基本クエリ
results = (QueryBuilder(db, "users")
    .select("name", "email", "age")
    .where("age", ">", 18)
    .where("status", "=", "active")
    .order_by("name", "ASC")
    .limit(10)
    .get())

# JOIN操作
results = (QueryBuilder(db, "orders")
    .select("orders.id", "users.name", "orders.total")
    .join("users", "orders.user_id", "=", "users.id")
    .where("orders.status", "=", "completed")
    .get())

# 集計
stats = (QueryBuilder(db, "orders")
    .select("user_id", "COUNT(*) as count", "SUM(total) as sum")
    .group_by("user_id")
    .having("count", ">", 5)
    .get())

# サブクエリ
active_users = (QueryBuilder(db, "users")
    .select("id")
    .where("status", "=", "active"))

orders = (QueryBuilder(db, "orders")
    .where_in("user_id", active_users)
    .get())
```

### メリット
- SQL知識不要で複雑なクエリを構築
- 型安全性
- 読みやすいコード

---

## 提案4: リレーションシップ管理 (Relationship Management)

### 概要
テーブル間の関係を定義し、自動的にJOINやデータ取得を行う。

### 実装例
```python
from nanasqlite import NanaSQLite, Model, Relationship

class User(Model):
    __table__ = "users"
    id: int
    name: str
    
    # リレーションシップ定義
    posts = Relationship("Post", foreign_key="user_id")
    profile = Relationship("Profile", foreign_key="user_id", one_to_one=True)

class Post(Model):
    __table__ = "posts"
    id: int
    user_id: int
    title: str
    
    user = Relationship("User", back_populates="posts")

db = NanaSQLite("app.db")

# 関連データの取得
user = User.query(db).get(id=1)
posts = user.posts.all()  # ユーザーの全投稿を自動取得
profile = user.profile.get()  # 1対1の関係

# 逆参照
post = Post.query(db).get(id=1)
author = post.user.get()  # 投稿の著者を自動取得
```

### メリット
- 関連データの取得が簡単
- N+1問題の自動最適化
- リレーションの整合性維持

---

## 提案5: キャッシュ戦略の拡張 (Extended Cache Strategies)

### 概要
より高度なキャッシュ戦略を提供し、パフォーマンスをさらに向上。

### 実装例
```python
from nanasqlite import NanaSQLite, CacheStrategy

# LRUキャッシュ
db = NanaSQLite("app.db", cache_strategy=CacheStrategy.LRU, cache_max_size=1000)

# TTL（有効期限）付きキャッシュ
db = NanaSQLite("app.db", cache_strategy=CacheStrategy.TTL, cache_ttl=300)  # 5分

# カスタムキャッシュ戦略
class CustomCache(CacheStrategy):
    def should_cache(self, key, value):
        # 大きなオブジェクトはキャッシュしない
        return len(str(value)) < 10000
    
    def should_evict(self, key, value, last_access):
        # 1時間アクセスされていないものは削除
        return time.time() - last_access > 3600

db = NanaSQLite("app.db", cache_strategy=CustomCache())

# キャッシュ統計
stats = db.cache_stats()
print(f"Hit rate: {stats.hit_rate}%")
print(f"Size: {stats.size} / {stats.max_size}")
```

### メリット
- メモリ使用量の最適化
- アクセスパターンに応じた柔軟なキャッシュ
- パフォーマンス監視

---

## 提案6: バリデーション機能 (Validation Features)

### 概要
データ挿入・更新時の自動バリデーション。

### 実装例
```python
from nanasqlite import NanaSQLite, Validator

class EmailValidator(Validator):
    def validate(self, value):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValueError(f"Invalid email: {value}")

class AgeValidator(Validator):
    def validate(self, value):
        if not (0 <= value <= 150):
            raise ValueError(f"Invalid age: {value}")

db = NanaSQLite("app.db")

# バリデーション設定
db.add_validator("users", "email", EmailValidator())
db.add_validator("users", "age", AgeValidator())

# バリデーション実行
try:
    db.sql_insert("users", {
        "name": "Alice",
        "email": "invalid-email",  # エラー発生
        "age": 25
    })
except ValueError as e:
    print(e)
```

### メリット
- データ整合性の保証
- アプリケーション層でのバリデーション
- 再利用可能なバリデーター

---

## 提案7: JSONフィールドのクエリサポート (JSON Field Query Support)

### 概要
JSON型カラムに対する高度なクエリ機能。

### 実装例
```python
from nanasqlite import NanaSQLite

db = NanaSQLite("app.db")

# JSONカラムのクエリ
results = db.query_json("users", 
    json_column="metadata",
    json_path="$.address.city",
    condition="= 'Tokyo'"
)

# JSONフィールドでのフィルタリング
users = (QueryBuilder(db, "users")
    .where_json("metadata", "$.age", ">", 25)
    .where_json("metadata", "$.tags", "contains", "premium")
    .get())

# JSON集計
stats = db.execute("""
    SELECT 
        json_extract(metadata, '$.country') as country,
        COUNT(*) as count
    FROM users
    GROUP BY country
""")
```

### メリット
- 柔軟なデータ構造のクエリ
- NoSQL的な使い方
- スキーマレスデータの活用

---

## 提案8: 全文検索機能 (Full-Text Search)

### 概要
SQLiteのFTS5を活用した高速な全文検索。

### 実装例
```python
from nanasqlite import NanaSQLite, FullTextSearch

db = NanaSQLite("app.db")

# FTSテーブル作成
fts = FullTextSearch(db)
fts.create_index("articles_fts", ["title", "content"], source_table="articles")

# 全文検索
results = fts.search("articles_fts", "python AND database")

# ハイライト付き結果
results = fts.search("articles_fts", "SQLite", highlight=True)
for r in results:
    print(r['highlighted_content'])

# ランキング
results = fts.search("articles_fts", "tutorial", order_by_rank=True, limit=10)
```

### メリット
- 高速な全文検索
- 多言語対応
- ランキング機能

---

## 提案9: バックアップ・リストア機能 (Backup & Restore)

### 概要
データベースの簡単なバックアップとリストア。

### 実装例
```python
from nanasqlite import NanaSQLite

db = NanaSQLite("app.db")

# バックアップ
db.backup("backup_20250109.db")

# 増分バックアップ
db.incremental_backup("backup_dir/")

# リストア
db.restore("backup_20250109.db")

# 自動バックアップ設定
db.enable_auto_backup(interval=3600, keep_last=10)  # 1時間ごと、最新10個保持

# クラウドバックアップ
db.backup_to_cloud("s3://mybucket/backup.db")
```

### メリット
- データ損失防止
- 簡単な復旧
- 自動化可能

---

## 提案10: 監視・ロギング機能 (Monitoring & Logging)

### 概要
データベース操作の監視とパフォーマンス分析。

### 実装例
```python
from nanasqlite import NanaSQLite, Monitor

db = NanaSQLite("app.db")

# モニタリング有効化
monitor = Monitor(db)
monitor.enable()

# クエリログ
monitor.log_query("SELECT * FROM users WHERE age > ?", (18,))

# パフォーマンス統計
stats = monitor.get_stats()
print(f"Total queries: {stats.total_queries}")
print(f"Slow queries: {stats.slow_queries}")
print(f"Average query time: {stats.avg_query_time}ms")

# スロークエリ通知
monitor.set_slow_query_threshold(100)  # 100ms以上
monitor.on_slow_query(lambda q: print(f"Slow query: {q}"))

# プロファイリング
with monitor.profile("complex_operation"):
    # 複雑な操作
    pass

report = monitor.generate_report()
```

### メリット
- パフォーマンスボトルネックの特定
- クエリ最適化のヒント
- 運用監視

---

## 優先順位の提案 (Priority Recommendations)

### 高優先度
1. **クエリビルダー** - 最も頻繁に使用され、コード品質向上に直結
2. **バリデーション機能** - データ整合性は重要
3. **バックアップ・リストア** - データ保護は必須

### 中優先度
4. **ORM風モデル定義** - 大規模アプリケーションで有用
5. **キャッシュ戦略拡張** - パフォーマンス重視の場合
6. **監視・ロギング** - 運用環境で重要

### 低優先度（特殊用途）
7. **マイグレーション機能** - チーム開発で有用だが複雑
8. **リレーションシップ管理** - ORM的な使い方をする場合
9. **全文検索** - 特定のユースケース向け
10. **JSONクエリサポート** - NoSQL的な使い方をする場合

---

## まとめ (Summary)

これらの機能を段階的に実装することで、NanaSQLiteは：
- シンプルなkey-valueストレージから
- 本格的なORM、クエリビルダーまで

幅広いニーズに対応できる、柔軟で強力なライブラリになります。

各機能は独立して実装可能で、必要に応じて選択的に追加できます。
