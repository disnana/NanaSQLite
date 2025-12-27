# 導入ガイド

NanaSQLiteは、Pythonの `dict` のような使い勝手と、SQLiteによる堅牢な永続化、そして高速なメモリキャッシュを組み合わせたライブラリです。

---

## ⚡ クイックスタート

インストールは簡単です：

```bash
pip install nanasqlite
```

基本的な使い方は以下の通りです：

```python
from nanasqlite import NanaSQLite

# データベースを開く（存在しない場合は作成）
db = NanaSQLite("mydata.db")

# dictのようにデータを保存
db["user_1"] = {"name": "Nana", "age": 20}

# データの取得
user = db["user_1"]
print(user["name"]) # Nana

# プログラムを終了しても、次回起動時にデータは保持されています
```

---

## 🌟 主な機能

::: info キャッシュとパフォーマンス
NanaSQLiteは起動時に全データを読み込む「一括ロード」と、アクセス時に読み込む「遅延ロード」を選択できます。また、WALモードにより書き込み中も読み込みをブロックしません。
:::

### 1. ネストされた構造
複雑な辞書やリストをそのまま保存でき、30階層以上の深いネストもサポートしています。

### 2. 強力なセキュリティ (v1.2.0+)
SQLインジェクション対策としての厳格なバリデーションや、ReDoS（正規表現DoS）攻撃を防ぐための長さ制限・文字セット検証が組み込まれています。

### 3. 非同期 (async/await) 対応
`AsyncNanaSQLite` クラスを使用して、FastAPIやDiscord.pyなどの非同期フレームワークで最高のパフォーマンスを発揮します。

```python
async with AsyncNanaSQLite("async.db") as db:
    await db.aset("key", "value")
```

---

## 🛠️ 次のステップ

- [パフォーマンスの最適化](./performance_tuning)
- [エラーハンドリングとトラブルシューティング](./error_handling)
- [APIリファレンス (同期)](./api_sync)
- [APIリファレンス (非同期)](./api_async)
