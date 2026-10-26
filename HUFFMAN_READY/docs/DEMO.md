# Kịch bản demo 5 phút

1. (30 giây) Giới thiệu: nén không mất mát bằng mã tiền tố, ứng dụng C–Python–React.
2. (60 giây) BANANA: giải thích tần suất; bấm từng bước, chỉ ra hai nút nhỏ nhất, tie-break, nhánh 0/1.
3. (45 giây) Bảng mã và chuỗi bit: A=0, B=10, N=11. Nhấn mạnh giải mã không cần dấu phân cách nhờ tính tiền tố.
4. (60 giây) Nén file repeated.txt và tải xuống, đọc số liệu gồm header. BANANA có thể tăng kích thước; dữ liệu lớn lệch tần suất có lợi hơn.
5. (60 giây) Chọn .huff vừa tải, giải nén, so hash với file gốc. Đóng/mở lại chương trình nếu cần chứng minh không giữ cây trong bộ nhớ.
6. (45 giây) Nêu giới hạn, UTF-8 nhiều byte, dữ liệu đã nén, CRC, bài học khi tích hợp C và Python.

Câu hỏi cần tự trả lời:
- Vì sao dùng heap? Vì sao chọn hai tần suất nhỏ nhất?
- Vì sao phải có tie-break khi lưu bảng tần suất?
- Byte khác chữ tiếng Việt như thế nào?
- Tại sao lưu văn bản '0101' không phải đóng gói bit?
- Bit đệm là gì và làm sao biết chỗ dừng?
- Vì sao bảng mã tối ưu mà file vẫn lớn hơn?
- CRC kiểm tra gì và không kiểm tra gì?

Phân công thuyết trình đề xuất: Kiệt trình bày lõi/cây; Tín trình bày luồng web, container, kiểm thử. Cả hai hiểu toàn bộ quy trình.
