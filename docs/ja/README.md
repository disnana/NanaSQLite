# NanaSQLite ドキュメント

dict風インターフェースでSQLite永続化を実現するライブラリ。

## 目次

- [コンセプト](#コンセプト)
- [インストール](#インストール)
- [クイックスタート](#クイックスタート)
- [ガイド](#ガイド)
  - [チュートリアル](guide/tutorial.md)
  - [非同期サポート](guide/async.md)
  - [トランザクション](guide/transactions.md)
  - [エラーハンドリング](guide/error_handling.md)
  - [パフォーマンス](guide/performance.md)
  - [ベストプラクティス](guide/best_practices.md)
- [APIリファレンス](#apiリファレンス)
  - [NanaSQLite (Sync)](api/nanasqlite.md)
  - [AsyncNanaSQLite (Async)](api/async_nanasqlite.md)

---

## コンセプト

### 課題

Pythonのdictは高速で便利ですが、揮発性です。プログラムが終了すると全てのデータが失われます。従来のデータベースソリューションはSQLの学習、接続管理、シリアライズの手動処理が必要です。

### 解決策

**NanaSQLite**は標準のPython dictを透過的なSQLite永続化でラップし、このギャップを埋めます：

```
┌─────────────────────────────────────────────────────┐
│                  Pythonコード                        │
│                                                      │
│    db["user"] = {"name": "Nana", "age": 20}         │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   NanaSQLite                         │
│  ┌───────────────┐     ┌───────────────────────┐    │
│  │ メモリキャッシュ │ ←→  │ APSW SQLite バックエンド │    │
│  │ (Python dict) │     │ (永続ストレージ)         │    │
│  └───────────────┘     └───────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 設計原則

1. **即時書き込み**: すべての書き込み操作は即座にSQLiteに永続化
2. **スマートリード**: データはオンデマンド（遅延）または一括でロード
3. **メモリ優先**: 一度ロードしたデータはメモリから高速に提供
4. **設定不要**: パフォーマンス最適化された合理的なデフォルト

### パフォーマンス最適化

NanaSQLiteはデフォルトで以下のSQLite最適化を適用します：

| 設定 | 効果 |
|------|------|
| **WALモード** | 書き込み速度: 30ms+ → 1ms以下 |
| **synchronous=NORMAL** | 安全 + 高速 |
| **mmap (256MB)** | メモリマップドI/Oで読み込み高速化 |
| **cache_size (64MB)** | SQLiteページキャッシュ拡大 |
| **temp_store=MEMORY** | 一時テーブルをRAMに |

---

## インストール

```bash
pip install nanasqlite
```

**必要条件:**
- Python 3.9以上
- APSW（自動でインストール）

---

## クイックスタート

### 基本的な使い方

```python
from nanasqlite import NanaSQLite

# データベースを作成または開く
db = NanaSQLite("mydata.db")

# データを保存（即座に永続化）
db["config"] = {"theme": "dark", "language": "ja"}
db["users"] = ["Alice", "Bob", "Charlie"]
db["count"] = 42

# データを取得
print(db["config"]["theme"])  # 'dark'
print(db["users"][0])          # 'Alice'
print(db["count"])             # 42

# 存在確認
if "config" in db:
    print("設定が存在します！")

# データを削除
del db["count"]

# 終了時にクローズ
db.close()
```

### コンテキストマネージャ

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # 終了時に自動的にクローズ
```

### 一括ロードで高速化

```python
# 起動時に全データをメモリにロード
db = NanaSQLite("mydata.db", bulk_load=True)

# 以降の読み込みはすべてメモリから（超高速）
for key in db.keys():
    print(db[key])  # データベースクエリなし！
```

---

## ガイド

詳細な情報は以下のガイドを参照してください：

- **[チュートリアル](guide/tutorial.md)**: 複数テーブルや高度な機能を含む詳細な例。
- **[非同期サポート](guide/async.md)**: `AsyncNanaSQLite` の使用方法。
- **[トランザクション](guide/transactions.md)**: データの整合性と一括書き込みの最適化。
- **[エラーハンドリング](guide/error_handling.md)**: 例外処理とトラブルシューティング。
- **[パフォーマンス](guide/performance.md)**: NanaSQLiteの速度チューニング。
- **[ベストプラクティス](guide/best_practices.md)**: 本番環境での推奨パターン。

---

## APIリファレンス

全クラス・メソッドの完全なドキュメント。

- **[NanaSQLite (Sync)](api/nanasqlite.md)**
- **[AsyncNanaSQLite (Async)](api/async_nanasqlite.md)**
