# Lõi C của Kiệt — bản tích hợp V1

Xem README.md tại thư mục gốc để cài GCC và chạy build_core.py. Không thay đổi CLI/JSON; xem docs/CHANGES.md để biết các bản sửa kiểm tra đầu vào.

Từ thư mục gốc:

    python build_core.py
    core\huffman_core.exe analyze samples\banana.txt
    python core\tests\test_core.py

Linux: binary là core/huffman_core. Kết quả JSON chỉ in trên stdout, lỗi in stderr. `tree` nhận đúng 256 số nguyên không âm ASCII, không nhận JSON. Bộ nhớ global chỉ phục vụ một lệnh mỗi tiến trình; backend tạo tiến trình độc lập cho mỗi lần gọi.

Không khẳng định mọi toolchain MinGW tạo binary không phụ thuộc DLL; script build Windows dùng -static. Việc chạy trên Windows cần kiểm tra thực tế tại máy người dùng.
