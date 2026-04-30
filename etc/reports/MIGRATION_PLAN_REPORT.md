# NanaSQLite プレースホルダー移行計画レポート

**提出日**: 2026年4月28日

---

## **目的**
- SQLインジェクション（CWE-89）を防止し、セキュリティを強化する。
- プリペアドステートメントの活用により、クエリ実行のパフォーマンスを向上させる。
- コードの可読性と保守性を向上させる。

---

## **対象箇所**
以下の関数で動的SQL生成が確認されており、プレースホルダーを使用するよう移行する。

| ファイル | 関数名 | 問題点 |
|---|---|---|
| `src/nanasqlite/core.py` | `query()` | 動的にテーブル名やカラム名を埋め込んでいる |
| `src/nanasqlite/core.py` | `query_with_pagination()` | WHERE句やORDER BY句に値を直接埋め込んでいる |
| `src/nanasqlite/core.py` | `execute()` | 任意のSQL文を直接実行可能 |
| `src/nanasqlite/core.py` | `_shared_query_impl()` | 複数のクエリ生成箇所で値を直接埋め込んでいる |

---

## **修正方針**

### **1. プレースホルダーの導入**
- **値の埋め込み**:
  - 動的に埋め込まれる値はすべてプレースホルダーを使用。
  - SQLiteでは `?` を使用して値を安全にバインド。

- **識別子の検証**:
  - テーブル名やカラム名などの識別子は、ホワイトリストまたは正規表現で検証。
  - プレースホルダーは使用できないため、事前に安全性を確認。

### **2. テストケースの作成**
- **正常系テスト**:
  - クエリが正しく実行され、期待通りの結果が得られることを確認。
- **異常系テスト**:
  - SQLインジェクションを試みる入力に対して、クエリが失敗することを確認。

### **3. パフォーマンス検証**
- 修正前後でクエリ実行時間を比較。
- 大量データに対するクエリ性能を測定。

---

## **修正例**

### **修正前: 動的SQL生成**
```python
def query(table_name, column, value):
    sql = f"SELECT {column} FROM {table_name} WHERE id = {value}"
    cursor.execute(sql)
```

### **修正後: プレースホルダーの使用**
```python
ALLOWED_COLUMNS = {"id", "name", "created_at"}
ALLOWED_TABLES = {"users", "orders"}

def query(table_name, column, value):
    if table_name not in ALLOWED_TABLES or column not in ALLOWED_COLUMNS:
        raise ValueError("Invalid table or column name")
    sql = f"SELECT {column} FROM {table_name} WHERE id = ?"
    cursor.execute(sql, (value,))
```

---

## **移行スケジュール**

### **フェーズ1: 設計と準備（1週間）**
- 対象箇所の特定と修正方針の確定。
- コードレビューを実施。

### **フェーズ2: 実装（2週間）**
- 各関数の修正を実施。
- 修正後のユニットテストを作成。

### **フェーズ3: テストとデプロイ（1週間）**
- パフォーマンス検証を実施。
- 本番環境へのデプロイ。

---

## **期待される成果**
- **セキュリティ向上**:
  - SQLインジェクションのリスクを排除。
- **パフォーマンス向上**:
  - プリペアドステートメントの再利用により、クエリ実行時間を短縮。
- **コードの可読性向上**:
  - SQL文とデータの分離により、コードが明確になる。

---

**確認者**: AI Assistant (GitHub Copilot)  
**最終確認日**: 2026年4月28日  
**ステータス**: ✅ 計画完了 → 実装待機中