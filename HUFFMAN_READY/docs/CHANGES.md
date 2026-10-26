# Bàn giao và sửa lỗi bộ lõi Kiệt

Đầu vào: `huffman_core_v1.zip` do người dùng cung cấp, gồm main.c/huffman.c/huffman.h, README, banana.json và 5 bài kiểm thử. Bản ZIP gốc không bị thay đổi.

Giữ lại thuật toán, cấu trúc dữ liệu, Min-Heap, cách dựng cây, sinh mã và JSON của Kiệt. Không dùng lõi C thay thế đã dựng trước khi nhận ZIP.

Sửa trong core/huffman.c:
1. Thay ký tự NUL thực nằm trong literal bằng biểu diễn văn bản `'\0'` để tránh cảnh báo trình biên dịch.
2. Comparator trả 0 khi so sánh cùng ID, đúng hợp đồng của qsort.
3. Thay parser fscanf cho bảng tần suất bằng parser kiểm tra từng chữ số. Từ chối thiếu/thừa số, dấu +/-, ký tự lạ, uint64 overflow và tổng vượt 16 MiB trước khi cộng.
4. Kiểm tra lỗi fread/fclose và lỗi stdout.

Bằng chứng trước sửa: 5 test gốc pass nhưng các bảng 257 số, `+0` và `18446744073709551615 1 ...` đều bị chấp nhận (exit code 0). Sau sửa, regression tests xác nhận từ chối.

CLI/JSON, quy tắc (freq,id), schema_version=1 và định dạng HUF1 không đổi. `core/examples/banana.json` được sinh lại từ binary thực tế.

Phần Tín: backend/codec.py, backend/app.py, frontend React, scripts Windows, tests tích hợp, docs và mẫu. Thêm API vẫn giữ hai endpoint preview đã làm trước đó.

Ngày bàn giao: 23/10/2026. Gói này là bản dự án riêng để tránh ghi đè các file đang sửa trên máy Tín.
