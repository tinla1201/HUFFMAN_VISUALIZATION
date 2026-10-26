# Kiểm thử thực tế — 23/10/2026

Môi trường: Linux x86_64, Python 3.12.14.

- 21 test tích hợp: pass.
- 5 test gốc Kiệt: pass.
- GCC -std=c11 -O2 -Wall -Wextra -Wpedantic: build thành công, không cảnh báo sau sửa.
- React/Vite 8.3.5 production build: thành công.
- Chưa chạy executable trên Windows. setup.cmd chạy kiểm thử lại tại máy người dùng.
- Chưa xác nhận UI bằng trình duyệt: môi trường preview không có runtime Python/Flask tương thích. Các route HTTP đã kiểm tra bằng Flask test_client, bao gồm multipart và tải file.
- Chưa kiểm tra giao diện trên điện thoại hay thao tác upload/download bằng trình duyệt thật.

```text
test_errors_are_json (__main__.ApiTests.test_errors_are_json) ... ok
test_health_and_static (__main__.ApiTests.test_health_and_static) ... ok
test_http_roundtrip (__main__.ApiTests.test_http_roundtrip) ... ok
test_json_and_file_analyze (__main__.ApiTests.test_json_and_file_analyze) ... ok
test_missing_core (__main__.ApiTests.test_missing_core) ... ok
test_preview_utf8 (__main__.ApiTests.test_preview_utf8) ... ok
test_corruption (__main__.CodecTests.test_corruption) ... ok
test_duplicate_symbol_and_large_size (__main__.CodecTests.test_duplicate_symbol_and_large_size) ... ok
test_fresh_process (__main__.CodecTests.test_fresh_process) ... ok
test_reference_bytes (__main__.CodecTests.test_reference_bytes) ... ok
test_roundtrip (__main__.CodecTests.test_roundtrip) ... ok
test_single_nonzero_bits (__main__.CodecTests.test_single_nonzero_bits) ... ok
test_truncated_extra_bad_magic (__main__.CodecTests.test_truncated_extra_bad_magic) ... ok
test_all_bytes (__main__.CoreTests.test_all_bytes) ... ok
test_banana_exact (__main__.CoreTests.test_banana_exact) ... ok
test_cli_errors (__main__.CoreTests.test_cli_errors) ... ok
test_empty_single (__main__.CoreTests.test_empty_single) ... ok
test_invalid_frequency_tables (__main__.CoreTests.test_invalid_frequency_tables) ... ok
test_limit (__main__.CoreTests.test_limit) ... ok
test_long_codes (__main__.CoreTests.test_long_codes) ... ok
test_ties_prefix_weights (__main__.CoreTests.test_ties_prefix_weights) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.391s

OK

.....
----------------------------------------------------------------------
Ran 5 tests in 0.006s

OK

```
