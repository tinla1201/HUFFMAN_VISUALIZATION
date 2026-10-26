# Kết quả thực nghiệm

Đo thực tế trong môi trường Linux của phiên làm việc, Python 3.12.14. Thời gian gồm gọi tiến trình C, xử lý tệp tạm và codec Python; một lần đo cho mỗi mẫu, không phải benchmark chuẩn. Máy Windows có thể khác.

| Dữ liệu | Gốc (byte) | .huff (byte) | Tiết kiệm | Nén (ms) | Giải nén (ms) | Đối chiếu |
|---|---:|---:|---:|---:|---:|---|
| BANANA | 6 | 56 | -833.33% | 1.61 | 1.40 | Đúng từng byte |
| Lặp lệch tần suất | 110000 | 17554 | 84.04% | 15.26 | 34.61 | Đúng từng byte |
| Tiếng Việt UTF-8 | 5900 | 3749 | 36.46% | 2.61 | 6.17 | Đúng từng byte |
| Đủ 256 byte × 100 | 25600 | 27931 | -9.11% | 11.34 | 45.37 | Đúng từng byte |
| Giả ngẫu nhiên 100000 byte | 100000 | 102331 | -2.33% | 25.25 | 155.72 | Đúng từng byte |

Giá trị âm nghĩa là tăng dung lượng. BANANA: 9 bit mã so với 12 bit mã cố định cho bảng chữ cái 3 ký hiệu tiết kiệm 25%; file gốc ASCII là 48 bit và container .huff là 56 byte. Ba phép so sánh có mẫu số khác nhau.
