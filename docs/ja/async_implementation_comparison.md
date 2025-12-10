# 非同期実装の比較: aiosqlite vs APSW vs 両方

## 現状の実装

現在のNanaSQLiteは**APSW (Another Python SQLite Wrapper)**を使用しています。
- バージョン: APSW 3.51.1.0
- 同期実装: `NanaSQLite`クラス（APSW使用）
- 非同期実装: `AsyncNanaSQLite`クラス（APSWをスレッドプールでラップ）

## オプション1: aiosqlite（純粋非同期）

### 概要
`aiosqlite`は、標準ライブラリの`sqlite3`をasyncioでラップしたライブラリです。

### メリット
1. **真の非同期**: I/O操作が非同期で実行される
2. **asyncio ネイティブ**: Pythonのasyncioエコシステムと自然に統合
3. **広く使用**: FastAPI、aiohttp等で標準的に使用される
4. **シンプル**: 標準ライブラリのsqlite3ベース

### デメリット
1. **2つの依存関係**: APSWとaiosqliteの両方が必要
2. **コード重複**: 同期版（APSW）と非同期版（aiosqlite）で別実装が必要
3. **機能差異**: APSWとsqlite3で微妙に異なる機能/API
4. **メンテナンス負担**: 2つの実装を維持する必要がある
5. **パフォーマンス**: 実際には内部でスレッドプールを使用（完全非同期ではない）

### コード例
```python
import aiosqlite

async with aiosqlite.connect("db.db") as db:
    await db.execute("CREATE TABLE IF NOT EXISTS data (key TEXT, value TEXT)")
    await db.execute("INSERT INTO data VALUES (?, ?)", ("key", "value"))
    await db.commit()
```

## オプション2: APSW + asyncio.to_thread()（現在の実装）

### 概要
現在の実装: APSWをスレッドプールでラップして非同期化

### メリット
1. **単一依存関係**: APSWのみで完結
2. **コード統一**: 同期版と非同期版で同じAPSW APIを使用
3. **機能完全性**: APSWの全機能をそのまま利用可能
4. **メンテナンス容易**: 同期版の変更が非同期版にも自動的に反映
5. **実装済み**: すでに44個のテストが合格している
6. **高性能**: APSWは最適化されており、sqlite3より高速

### デメリット
1. **疑似非同期**: スレッドプールでブロッキング操作を実行
2. **真の並列性なし**: GILの制限を受ける（ただしI/O待機時は問題なし）

### 現在の実装
```python
# async_core.py
async def aget(self, key: str, default: Any = None) -> Any:
    await self._ensure_initialized()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        self._executor,
        self._db.get,
        key,
        default
    )
```

## オプション3: 両方サポート

### 概要
APSWベースの実装とaiosqliteベースの実装を両方提供

### メリット
1. **柔軟性**: ユーザーが好みの実装を選択可能
2. **最適化**: 各実装が最適化された形で提供

### デメリット
1. **複雑性**: コードベースが2倍に
2. **メンテナンス**: 2つの実装を維持する必要
3. **テスト**: テストも2倍必要
4. **依存関係**: 両方のライブラリが必要
5. **混乱**: ユーザーがどちらを使うべきか迷う

## 技術的考察

### aiosqliteの「非同期」の実態
実は、aiosqliteも内部ではスレッドプールを使用しています：
```python
# aiosqlite内部の実装
async def execute(self, sql, parameters=None):
    return await self._execute(self._conn.execute, sql, parameters)

async def _execute(self, fn, *args, **kwargs):
    return await self._loop.run_in_executor(None, fn, *args, **kwargs)
```

つまり、**aiosqliteも現在の実装と同じくスレッドプールを使用**しています！

### パフォーマンス比較

| 実装 | 読み込み速度 | 書き込み速度 | 真の非同期 | 実装の複雑さ |
|------|-------------|-------------|-----------|-------------|
| APSW + thread pool | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ (シンプル) |
| aiosqlite | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ (内部でthread pool) | ⭐⭐⭐⭐ |
| 両方 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ (複雑) |

注: SQLiteは本質的にC言語の同期ライブラリなので、「真の非同期」は不可能

## 推奨: オプション2（現在の実装を継続）

### 理由

1. **技術的優位性なし**: aiosqliteも内部でスレッドプールを使用しているため、パフォーマンス面で現在の実装と同等

2. **APSWの優位性**:
   - より高速（Cレベルで最適化）
   - より多機能（APSW固有の機能）
   - 現在の同期版と完全互換

3. **コード品質**:
   - すでに44個のテストが合格
   - 単一の依存関係
   - メンテナンスが容易

4. **実用性**:
   - FastAPI、aiohttp等で問題なく動作
   - イベントループをブロックしない
   - 並行処理が可能

5. **SQLiteの性質**:
   - SQLite自体が単一ライターモデル
   - 並列書き込みは不可能
   - したがって「真の非同期」のメリットは限定的

## 改善提案

現在の実装（APSW + thread pool）を維持しつつ、以下の改善を提案：

### 1. ドキュメントの明確化
```markdown
## 非同期実装について

AsyncNanaSQLiteは、APSWをスレッドプールでラップして非同期化しています。
これは以下の理由から最適な選択です：

1. SQLiteはC言語の同期ライブラリであり、真の非同期I/Oは不可能
2. aiosqliteも内部でスレッドプールを使用（同じアプローチ）
3. APSWは高速で機能豊富
4. 同期版との完全互換性

イベントループをブロックせず、FastAPI等の非同期フレームワークで安全に使用できます。
```

### 2. パフォーマンスベンチマーク追加
```python
# tests/test_async_benchmark.py
@pytest.mark.asyncio
async def test_concurrent_performance():
    """並行処理のパフォーマンステスト"""
    async with AsyncNanaSQLite(":memory:") as db:
        # 100個の並行読み込みをベンチマーク
        start = time.time()
        await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
        elapsed = time.time() - start
        assert elapsed < 1.0  # 1秒以内
```

### 3. 接続プールの最適化（オプション）
より高度な使用ケース向けに接続プールを提供：
```python
class AsyncNanaSQLite:
    def __init__(self, db_path, max_connections=5):
        self._pool = ThreadPoolExecutor(max_workers=max_connections)
```

## 結論

**推奨: 現在の実装（APSW + asyncio.to_thread()）を継続**

理由:
- ✅ 技術的に健全（aiosqliteと同じアプローチ）
- ✅ 高性能（APSWの最適化を活用）
- ✅ シンプル（単一依存関係）
- ✅ メンテナンス容易
- ✅ すでに動作確認済み（44テスト合格）

aiosqliteへの移行や両方のサポートは、追加の複雑性をもたらすだけで、
パフォーマンスや機能面での明確なメリットがありません。

---

作成日: 2025-12-10
結論: APSW + asyncio.to_thread()を継続推奨
