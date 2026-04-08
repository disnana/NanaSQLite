#![no_main]
use libfuzzer_sys::fuzz_target;

// nanalib を fuzz ターゲットから使えるように fuzz/Cargo.toml に依存を追加してください。
// 例: fuzz/Cargo.toml の [dependencies] に nanalib = { path = "../src/nanalib" }

fuzz_target!(|data: &[u8]| {
    // まずは UTF-8 として解釈できる入力のみを sanitize に渡す（関数の前提を検証）
    if let Ok(s) = std::str::from_utf8(data) {
        let out = nanalib::sanitize_sql_for_function_scan(s);
        // 出力が常に有効 UTF-8 であることを確認（ここで panic が出れば問題）
        let _ = std::str::from_utf8(out.as_bytes()).unwrap();
        // fast_validate を呼んで落ちるか確認（任意）
        let _ = nanalib::fast_validate_sql_chars(s);
    }
});
