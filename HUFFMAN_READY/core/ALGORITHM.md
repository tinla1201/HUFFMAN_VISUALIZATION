# Thuật toán và giới hạn phân tích

## Dữ liệu
Mỗi byte 0..255 là một ký hiệu. Đếm N byte để có k tần suất dương, k<=256. Lá có ID=byte; nút nội bộ ID tăng từ 256. Heap so sánh (tần suất, ID) nên hai lần dựng với cùng bảng tạo cùng cây.

## Dựng cây
Đưa k lá vào Min-Heap. Khi còn ít nhất hai gốc, lấy hai gốc nhỏ nhất x,y; tạo cha có trọng số x.freq+y.freq, trái=x, phải=y; đưa cha vào heap. Lặp đến khi còn một gốc. Mỗi lần gộp giảm số gốc đi 1 nên có k-1 bước (k>0).

## Mã và giải mã
Duyệt trái ghi 0, phải ghi 1. Mã lá là đường từ gốc đến lá. Không lá nào là tổ tiên của lá khác nên không mã nào là tiền tố mã khác. Khi giải mã, đọc bit để đi trái/phải; đến lá xuất byte rồi trở lại gốc. Với một ký hiệu duy nhất, quy ước mã 0; với dữ liệu rỗng, không có cây.

## Ý tưởng chứng minh tối ưu
Trong một cây mã tiền tố nhị phân tối ưu có thể chọn hai ký hiệu tần suất nhỏ nhất làm hai lá anh em ở độ sâu lớn nhất: đổi các ký hiệu nhỏ xuống vị trí sâu không làm tăng tổng chi phí có trọng số. Gộp hai lá thành ký hiệu có tần suất tổng; chi phí cây ban đầu bằng chi phí cây rút gọn cộng tổng hai tần suất. Nếu cây rút gọn chưa tối ưu thì thay bằng cây tốt hơn sẽ cải thiện cây ban đầu, mâu thuẫn. Quy nạp theo số ký hiệu chứng minh lựa chọn tham lam. Tính tối ưu chỉ xét mã tiền tố nhị phân cho tần suất đã cho, không có nghĩa file .huff luôn nhỏ nhất trong mọi định dạng nén.

## Độ phức tạp của đúng mã nguồn này
- Đếm: O(N).
- Dựng cây bằng heap, không tính lịch sử: O(k log k).
- Bản Kiệt ghi queue_after bằng sao chép và qsort heap ở mỗi bước: tổng O(k² log k), bộ nhớ lịch sử O(k²). Phải ghi rõ chi phí mô phỏng này trong báo cáo.
- Sinh mã hiện tìm node theo ID bằng quét tuyến tính tại mỗi lần thăm: O(k²), cộng chi phí sao chép các chuỗi mã. Bộ nhớ mã O(k * Lmax), Lmax<=255.
- Mã hóa Python: đọc các byte và ghi B bit đầu ra; phụ thuộc độ dài mã. Không tạo một chuỗi '0'/'1' cho toàn file; dùng bộ đệm bit và bytearray.
- Giải mã Python: O(B), bộ nhớ đầu ra O(N).
- Vẽ cây: duyệt các node đang hiển thị; không vẽ hàng triệu pixel dữ liệu đầu vào.

## Ví dụ BANANA
A:3, B:1, N:2. Gộp B+N=3. A có ID65 nhỏ hơn ID256 nên A làm trái ở lần gộp cuối. A=0, B=10, N=11. BANANA -> 100110110, 9 bit, trung bình 1.5 bit/byte gốc. Mã cố định trên ba ký hiệu dùng 2 bit/ký hiệu: 12 bit, tiết kiệm 25% phần mã. File ASCII gốc thực tế 6 byte; .huff V1 thực tế 56 byte vì 27+9*3+2. Không đánh đồng các tỷ lệ.
