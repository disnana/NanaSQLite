# NanaSQLite セキュリティ修正コード例

**提出日**: 2026年4月28日

---

## 修正コード例
以下は、検出された脆弱性に対する簡易的な修正コード例です。

### 1. CWE-89: SQLインジェクション
#### 修正前:
```python
sql = f"PRAGMA {pragma_name} = {value}"
cursor.execute(sql)
```
#### 修正後:
```python
ALLOWED_PRAGMAS = {"journal_mode", "synchronous", "cache_size"}
if pragma_name not in ALLOWED_PRAGMAS:
    raise ValueError("Invalid pragma name")
sql = f"PRAGMA {pragma_name} = ?"
cursor.execute(sql, (value,))
```

---

### 2. CWE-693: 保護メカニズムの失敗
#### 修正前:
```python
def execute(sql, params):
    return self._connection.execute(sql, params)
```
#### 修正後:
```python
def execute(sql, params, *, trusted=False):
    if not trusted:
        raise PermissionError("Direct SQL execution is not allowed")
    return self._connection.execute(sql, params)
```

---

### 3. CWE-20: 不適切な入力検証
#### 修正前:
```python
if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name):
    raise ValueError("Invalid column name")
```
#### 修正後:
```python
ALLOWED_COLUMNS = {"id", "name", "created_at"}
if column_name not in ALLOWED_COLUMNS:
    raise ValueError("Invalid column name")
```

---

### 4. CWE-367: TOCTOU（競合状態）
#### 修正前:
```python
with self._lock:
    old_value = db._get_raw(key)
    db._update_raw(key, new_value)
```
#### 修正後:
```python
with self._lock:
    with db._acquire_lock():
        old_value = db._get_raw(key)
        db._update_raw(key, new_value)
```

---

### 5. CWE-918: SSRF
#### 修正前:
```python
def __init__(self, db_path):
    self._db_path = db_path
```
#### 修正後:
```python
ALLOWED_BASE_DIR = "/safe/base/dir"
def __init__(self, db_path):
    abs_path = os.path.realpath(db_path)
    if not abs_path.startswith(ALLOWED_BASE_DIR):
        raise ValueError("Path is outside the allowed directory")
    self._db_path = abs_path
```

---

## 提出内容
- **修正対象**: CWE-89, CWE-693, CWE-20, CWE-367, CWE-918
- **目的**: セキュリティ強化とパフォーマンス維持
- **次のステップ**: 各修正コードのテストケース作成と実装計画の詳細化

**確認者**: AI Assistant (GitHub Copilot)