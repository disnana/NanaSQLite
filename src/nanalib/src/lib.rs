use pyo3::prelude::*;

/// UTF-8コードポイント単位でスペースを出力する。
/// 継続バイト(0x80..=0xBF)はスキップし、先頭バイト or ASCII 1バイトにつきスペース1個。
/// これにより Python の len() と文字数が一致する。
#[inline(always)]
fn push_spaces_per_char(result: &mut Vec<u8>, bytes: &[u8]) {
    for &b in bytes {
        if b < 0x80 || b >= 0xC0 {
            result.push(b' ');
        }
    }
}

/// コンパイル時生成の安全文字ルックアップテーブル（256要素 → O(1)参照・分岐なし）
static SAFE_CHARS: [bool; 256] = {
    let mut t = [false; 256];
    let safe = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\
                 0123456789_ ,.()\'=<>!+-*/\"|?:@$";
    let mut i = 0;
    while i < safe.len() {
        t[safe[i] as usize] = true;
        i += 1;
    }
    t
};

/// 内部的な状態を管理するための型
#[repr(u8)]
enum State {
    Normal,
    InSingle,
    InDouble,
    InLineComment,
    InBlockComment,
}

/// SQL文をスキャンして、インジェクションに悪用されやすい文字列リテラルや
/// コメント部分を「 」（スペース）で埋める関数。
///
/// # 安全性（unsafe ブロックについて）
/// - 入力 `sql: &str` は Rust が有効な UTF-8 であることを保証済み。
/// - スペース埋めは ASCII 0x20 のみ。ASCII バイトは UTF-8 多バイトシーケンスの
///   継続バイト(0x80-0xBF)と衝突しないため、出力も有効な UTF-8 となる。
/// - InDouble は入力バイトをそのままコピーするため問題なし。
/// - よって `from_utf8_unchecked` の前提条件は常に成立する。
#[pyfunction]
fn sanitize_sql_for_function_scan(sql: &str) -> String {
    let bytes = sql.as_bytes();
    let len = bytes.len();
    if len == 0 {
        return String::new();
    }

    let mut result: Vec<u8> = Vec::with_capacity(len);
    let mut i = 0;
    let mut state = State::Normal;

    while i < len {
        match state {
            // ── Normal ─────────────────────────────────────────────────────
            State::Normal => {
                // 特殊文字が来るまで一括 memcpy（最大の速度改善点）
                let start = i;
                while i < len {
                    match bytes[i] {
                        b'\'' | b'"' | b'-' | b'/' => break,
                        _ => i += 1,
                    }
                }
                result.extend_from_slice(&bytes[start..i]);
                if i >= len { break; }

                let ch = bytes[i];
                if ch == b'-' && i + 1 < len && bytes[i + 1] == b'-' {
                    state = State::InLineComment;
                    result.extend_from_slice(b"  ");
                    i += 2;
                } else if ch == b'/' && i + 1 < len && bytes[i + 1] == b'*' {
                    state = State::InBlockComment;
                    result.extend_from_slice(b"  ");
                    i += 2;
                } else if ch == b'\'' {
                    state = State::InSingle;
                    result.push(b' ');
                    i += 1;
                } else if ch == b'"' {
                    state = State::InDouble;
                    result.push(b' ');
                    i += 1;
                } else {
                    // `-` や `/` 単体（コメント開始でない）はそのままコピー
                    result.push(ch);
                    i += 1;
                }
            }

            // ── InLineComment ───────────────────────────────────────────────
            State::InLineComment => {
                let start = i;
                while i < len && bytes[i] != b'\n' { i += 1; }
                // Unicode 対応: コードポイント単位でスペース埋め
                push_spaces_per_char(&mut result, &bytes[start..i]);
                if i < len {
                    state = State::Normal;
                    result.push(b'\n');
                    i += 1;
                }
            }

            // ── InBlockComment ──────────────────────────────────────────────
            State::InBlockComment => {
                let start = i;
                loop {
                    if i >= len {
                        push_spaces_per_char(&mut result, &bytes[start..i]);
                        break;
                    }
                    if bytes[i] == b'*' && i + 1 < len && bytes[i + 1] == b'/' {
                        push_spaces_per_char(&mut result, &bytes[start..i]);
                        result.extend_from_slice(b"  ");
                        i += 2;
                        state = State::Normal;
                        break;
                    }
                    i += 1;
                }
            }

            // ── InSingle ────────────────────────────────────────────────────
            State::InSingle => {
                let start = i;
                while i < len && bytes[i] != b'\'' { i += 1; }
                // Unicode 対応: コードポイント単位でスペース埋め
                push_spaces_per_char(&mut result, &bytes[start..i]);
                if i < len {
                    if i + 1 < len && bytes[i + 1] == b'\'' {
                        // '' エスケープ: 2文字 → スペース2個、InSingle 継続
                        result.extend_from_slice(b"  ");
                        i += 2;
                    } else {
                        // 閉じクォート: InSingle 終了
                        state = State::Normal;
                        result.push(b' ');
                        i += 1;
                    }
                }
            }

            // ── InDouble ────────────────────────────────────────────────────
            // 識別子（テーブル名等）なので中身は保持する
            State::InDouble => {
                let start = i;
                while i < len && bytes[i] != b'"' { i += 1; }
                // 識別子内容はそのままコピー（入力が有効 UTF-8 なので安全）
                result.extend_from_slice(&bytes[start..i]);
                if i < len {
                    if i + 1 < len && bytes[i + 1] == b'"' {
                        // "" エスケープ: 2文字 → スペース2個、InDouble 継続
                        result.extend_from_slice(b"  ");
                        i += 2;
                    } else {
                        // 閉じクォート: InDouble 終了
                        state = State::Normal;
                        result.push(b' ');
                        i += 1;
                    }
                }
            }
        }
    }

    // SAFETY: 上記コメント参照。入力が有効 UTF-8 かつ ASCII のみ置換するため安全。
    unsafe { String::from_utf8_unchecked(result) }
}

/// SQL式に使われる文字が「安全な文字セット」に含まれているか一括チェックする関数。
/// コンパイル時テーブルによる O(1) ルックアップで分岐予測ミスを排除。
#[pyfunction]
fn fast_validate_sql_chars(expr: &str) -> bool {
    expr.as_bytes().iter().all(|&b| SAFE_CHARS[b as usize])
}

/// Python モジュールとして登録
#[pymodule]
fn nanalib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sanitize_sql_for_function_scan, m)?)?;
    m.add_function(wrap_pyfunction!(fast_validate_sql_chars, m)?)?;
    Ok(())
}

// ─── ユニットテスト ────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    // ── sanitize_sql_for_function_scan ────────────────────────────────────

    #[test]
    fn test_empty_input() {
        assert_eq!(sanitize_sql_for_function_scan(""), "");
    }

    #[test]
    fn test_no_special_chars() {
        let s = "SELECT col FROM tbl WHERE id = 1";
        assert_eq!(sanitize_sql_for_function_scan(s), s);
    }

    #[test]
    fn test_single_quote_masked() {
        let out = sanitize_sql_for_function_scan("SELECT 'secret' FROM t");
        assert!(!out.contains("secret"));
        assert!(out.contains("SELECT"));
        assert!(out.contains("FROM t"));
    }

    #[test]
    fn test_escaped_single_quote() {
        let out = sanitize_sql_for_function_scan("WHERE x = 'it''s ok'");
        assert!(!out.contains("it''s"));
    }

    #[test]
    fn test_line_comment_masked() {
        let out = sanitize_sql_for_function_scan("SELECT col --comment\nFROM t");
        assert!(!out.contains("comment"));
        assert!(out.contains("\nFROM t"));
    }

    #[test]
    fn test_block_comment_masked() {
        let out = sanitize_sql_for_function_scan("SELECT /* secret */ col FROM t");
        assert!(!out.contains("secret"));
        assert!(out.contains("col FROM t"));
    }

    #[test]
    fn test_double_quote_preserved() {
        let out = sanitize_sql_for_function_scan(r#"SELECT "col_name" FROM t"#);
        assert!(out.contains("col_name"), "識別子の中身は保持されるべき");
    }

    #[test]
    fn test_standalone_slash_preserved() {
        let s = "SELECT 10/2 FROM t";
        assert_eq!(sanitize_sql_for_function_scan(s), s);
    }

    #[test]
    fn test_standalone_dash_preserved() {
        let s = "SELECT -1 FROM t";
        assert_eq!(sanitize_sql_for_function_scan(s), s);
    }

    /// Unicode 文字を含む場合、出力の char 数（コードポイント数）が
    /// 入力と一致しなければならない（Python の len() と対応）
    #[test]
    fn test_unicode_char_length_preserved() {
        let sql = "SELECT '日本語テスト' FROM table";
        let out = sanitize_sql_for_function_scan(sql);
        assert_eq!(
            out.chars().count(),
            sql.chars().count(),
            "コードポイント数が一致しなければならない: got {:?}", out
        );
    }

    #[test]
    fn test_unicode_in_block_comment() {
        let sql = "SELECT /* 日本語コメント */ col FROM t";
        let out = sanitize_sql_for_function_scan(sql);
        assert_eq!(out.chars().count(), sql.chars().count());
        assert!(!out.contains("日本語"));
    }

    #[test]
    fn test_unicode_in_line_comment() {
        let sql = "SELECT col -- 日本語コメント\nFROM t";
        let out = sanitize_sql_for_function_scan(sql);
        assert_eq!(out.chars().count(), sql.chars().count());
        assert!(!out.contains("日本語"));
        assert!(out.contains("\nFROM t"));
    }

    #[test]
    fn test_unclosed_single_quote() {
        // 未閉じクォートでもパニックしないこと
        let sql = "SELECT 'unclosed";
        let out = sanitize_sql_for_function_scan(sql);
        assert_eq!(out.chars().count(), sql.chars().count());
    }

    #[test]
    fn test_unclosed_block_comment() {
        let sql = "SELECT /* unclosed";
        let out = sanitize_sql_for_function_scan(sql);
        assert_eq!(out.chars().count(), sql.chars().count());
    }

    // ── fast_validate_sql_chars ──────────────────────────────────────────

    #[test]
    fn test_validate_empty() {
        assert!(fast_validate_sql_chars(""));
    }

    #[test]
    fn test_validate_safe() {
        assert!(fast_validate_sql_chars("SELECT a FROM b WHERE id = 1"));
    }

    #[test]
    fn test_validate_unicode_rejected() {
        assert!(!fast_validate_sql_chars("SELECT ☺ FROM b"));
        assert!(!fast_validate_sql_chars("SELECT '日本語' FROM b"));
    }

    #[test]
    fn test_validate_semicolon_rejected() {
        assert!(!fast_validate_sql_chars("SELECT a; DROP TABLE b"));
    }

    #[test]
    fn test_validate_allowed_special_chars() {
        assert!(fast_validate_sql_chars("a_b, (c.d) = 'x' < > ! + - * / | ? : @ $"));
    }
}
