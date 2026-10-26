# PROMPT CHO CHATGPT CỦA KIỆT — HUFFMAN V1
Ngày chốt: 23/10/2026. Đây là đặc tả chung đã được Tín giao quyền chốt, không phải danh sách lựa chọn. Hãy đọc toàn bộ và bắt đầu triển khai phần của Kiệt, không hỏi lại công nghệ hoặc giao thức.

## 1. Bối cảnh và mục tiêu
Tôi là Hoàng Dương Tuấn Kiệt, cùng La Hữu Tín làm đề tài Toán rời rạc: “Thiết kế và phân tích hệ thống nén dữ liệu không mất mát sử dụng mã Huffman”. Hạn nộp 25/10/2026; cần ưu tiên bản chạy được trong hôm nay.
Sản phẩm là web chạy trên máy cá nhân: nhập văn bản/chọn tập tin; xem tần suất, cây, bảng mã và từng bước gộp; nén thành .huff; mở lại và giải nén chính xác; thống kê kích thước thật.
Công nghệ đã chốt: C11 cho lõi, Python Flask cho backend, React cho giao diện. Dùng GCC (Windows dùng MinGW-w64; Linux dùng GCC). Không cần triển khai server công khai.
Bản đầu chỉ tiếng Việt. Không làm LZ77, DEFLATE, JPEG, tài khoản, cơ sở dữ liệu hay demo pixel ảnh. Tập tin ảnh vẫn được nén như tập tin byte bất kỳ, không hứa nhỏ hơn.

## 2. Phân công cố định
Kiệt: lõi C gồm đếm tần suất, Min-Heap, dựng cây xác định, sinh mã, lịch sử gộp, CLI xuất JSON, kiểm thử lõi; phần báo cáo thuật toán.
Tín: Python gọi CLI C; mã hóa và đóng gói bit; đọc/ghi .huff; giải mã bằng cây từ C; kiểm tra CRC; React và SVG vẽ cây; thống kê; kiểm thử toàn hệ thống; phần báo cáo phần mềm.
Không tự viết backend/React hoặc thêm một bản Huffman Python chính thức. Python có thể làm test cho C.
Hai bên chưa được coi là đã viết xong code; chỉ đặc tả này đã chốt.

## 3. Dữ liệu và thuật toán xác định
- Đơn vị nén là byte 0..255. Văn bản được Python chuyển UTF-8; C chỉ đọc byte, không giải mã Unicode.
- V1 giới hạn dữ liệu gốc tối đa 16 MiB = 16777216 byte. C kiểm tra cả khi đọc tập tin và khi nhận tần suất. Python kiểm tra trước nén và trước cấp phát dữ liệu giải nén.
- Tần suất và tổng bit dùng uint64_t; đọc byte bằng unsigned char. In số bằng PRIu64.
- Lá: id = giá trị byte, symbol = byte, freq = số lần xuất hiện. Không tạo lá có freq=0.
- Nút nội bộ: ID bắt đầu từ 256, tăng 1 cho mỗi lần gộp; symbol=null.
- Min-Heap so sánh tăng dần theo (freq, id), bao gồm cả lá và nút nội bộ.
- Mỗi bước pop hai nút: nút pop trước là left (nhánh 0), pop sau là right (nhánh 1).
- Nút cha có freq = tổng hai con. Root là nút cuối.
- Tối đa 511 nút; độ dài mã tối đa 255 bit. Chuỗi mã cần vùng nhớ ít nhất 256 char tính cả ký tự kết thúc; không lưu mã vào một số nguyên 64-bit.
- Một byte khác nhau: giữ root là lá, mã của lá là "0", encoded_bits = original_size; không tạo nút cha giả.
- Dữ liệu rỗng: root=null, nodes=[], codes=[], steps=[], encoded_bits=0.
- encoded_bits = tổng freq[symbol] * độ dài mã.

## 4. Giao thức gọi C — chỉ hai lệnh
Tên binary: huffman_core.exe trên Windows, huffman_core trên Linux.

Lệnh 1:
    huffman_core analyze INPUT_PATH
Đọc INPUT_PATH ở chế độ rb, đếm tần suất rồi trả JSON.

Lệnh 2:
    huffman_core tree FREQ_PATH
FREQ_PATH là tập tin ASCII: đúng 256 số nguyên thập phân không âm, lần lượt freq[0]..freq[255], cách nhau bằng khoảng trắng hoặc xuống dòng. Cho phép khoảng trắng cuối; không cho dấu +/-, số thập phân, thiếu/thừa số, ký tự lạ hoặc tràn số. Tổng <= 16777216.
Lệnh này dùng khi giải nén: Python đọc header .huff, ghi bảng 256 số ra tập tin tạm rồi gọi C dựng cây.
KHÔNG yêu cầu C đọc JSON hoặc đọc .huff. Kết quả hai lệnh có cùng schema.

Thành công: exit code 0; stdout đúng một JSON object hợp lệ, có thể thêm newline cuối; không log/debug trên stdout.
Thất bại: exit code 1 (đọc/ghi, cấp phát, dữ liệu lỗi) hoặc 2 (sai cú pháp CLI); stderr có thông báo; stdout rỗng. Hoàn thành kiểm tra dữ liệu trước khi bắt đầu in JSON.
Không sử dụng trạng thái giữa các lần gọi, không tạo tập tin tạm tên cố định.

Python gọi bằng danh sách tham số, shell=False, check=True, capture_output=True, text=True, encoding="utf-8", timeout=30. Mỗi request có thư mục tạm riêng. Ví dụ:
    result = subprocess.run(
        [str(core_path), "analyze", str(input_path)],
        check=True, capture_output=True, text=True,
        encoding="utf-8", timeout=30
    )
    data = json.loads(result.stdout)
Đây là cách tích hợp; Tín phụ trách code Python thực tế.

## 5. Schema JSON version 1 — giữ nguyên tên trường
Các số JSON là số nguyên, không phải chuỗi. Giới hạn V1 bảo đảm số an toàn cho JavaScript.
Các trường luôn có mặt:
- schema_version: 1
- original_size: tổng tần suất, đơn vị byte
- encoded_bits: số bit thật, chưa đệm
- frequencies: array đúng 256 số, theo thứ tự byte 0..255
- root: ID hoặc null
- nodes: array sắp tăng theo id. Mỗi phần tử có đúng:
  {"id":65,"symbol":65,"freq":3,"left":null,"right":null}
  Nút nội bộ có symbol=null và left/right là ID số nguyên.
- codes: array sắp tăng theo symbol, chỉ các byte xuất hiện:
  {"symbol":65,"bits":"0"}
- steps: array theo thứ tự gộp:
  {"step":1,"left":66,"right":78,"parent":256,"queue_after":[65,256]}
  step bắt đầu từ 1. queue_after là ID các gốc cây còn trong heap sau khi đưa parent vào, SẮP THEO (freq,id); không xuất thứ tự nội bộ của mảng heap.
  Python/React lấy hàng đợi ban đầu từ các lá rồi sắp theo (freq,id).
  Node parent đã có trong nodes. Không cần nhân bản toàn bộ cây cho mỗi bước.
Không xuất tên ký tự, chuỗi đầu vào hay chuỗi bit mã hóa đầy đủ; frontend tự định dạng byte thành hex hoặc ASCII. Điều này tránh lỗi escape JSON và dữ liệu quá lớn.
Trường hợp rỗng/một byte: steps=[].
Có thể tự in JSON bằng fprintf/printf vì chỉ xuất số, null, chuỗi bit và khóa cố định; không cần thư viện JSON ngoài.

## 6. Ví dụ nghiệm thu bắt buộc: BANANA
Đầu vào đúng 6 byte ASCII, KHÔNG có newline:
frequencies[65]=3; frequencies[66]=1; frequencies[78]=2; tất cả còn lại bằng 0.
original_size=6; encoded_bits=9; root=257.
nodes:
[
 {"id":65,"symbol":65,"freq":3,"left":null,"right":null},
 {"id":66,"symbol":66,"freq":1,"left":null,"right":null},
 {"id":78,"symbol":78,"freq":2,"left":null,"right":null},
 {"id":256,"symbol":null,"freq":3,"left":66,"right":78},
 {"id":257,"symbol":null,"freq":6,"left":65,"right":256}
]
codes:
[
 {"symbol":65,"bits":"0"},
 {"symbol":66,"bits":"10"},
 {"symbol":78,"bits":"11"}
]
steps:
[
 {"step":1,"left":66,"right":78,"parent":256,"queue_after":[65,256]},
 {"step":2,"left":65,"right":256,"parent":257,"queue_after":[257]}
]
Mã hóa BANANA: 100110110. Phần payload đóng gói: 0x9B 0x00 (7 bit đệm).
Ví dụ trên mô tả các trường; JSON thật phải có đầy đủ frequencies gồm 256 số.

## 7. Định dạng .huff V1 — Tín triển khai, Kiệt cần hiểu
Tất cả số nhiều byte đều unsigned LITTLE-ENDIAN. Không ghi trực tiếp struct C vì có padding.
Header cố định 27 byte:
| Offset | Độ dài | Nội dung |
|---|---:|---|
| 0 | 4 | Magic ASCII HUF1 |
| 4 | 1 | Version = 1 |
| 5 | 8 | original_size |
| 13 | 8 | encoded_bits |
| 21 | 4 | CRC-32 của dữ liệu gốc: Python zlib.crc32(raw) & 0xffffffff |
| 25 | 2 | k: số byte khác nhau, 0..256 |

Tiếp theo là k entry sắp tăng theo symbol. Mỗi entry 9 byte: symbol (1 byte), freq (uint64 little-endian, 8 byte). Chỉ lưu freq>0, không lặp symbol.
Sau bảng là payload dài ceil(encoded_bits/8) byte. Bit đầu tiên đặt ở bit 7 (MSB) của byte đầu; đi dần đến bit 0. Byte cuối đệm số 0 ở bên phải. Không cho byte dư sau payload.
Không lưu tên file gốc; khi giải nén người dùng chọn tên/đuôi cần lưu. Header đủ để khôi phục nội dung byte.
Tổng kích thước = 27 + 9*k + ceil(encoded_bits/8).
Ví dụ BANANA: k=3, 9 bit, payload 2 byte => .huff có 56 byte, lớn hơn file gốc 6 byte. Không nhầm với tiết kiệm 25% khi so 9 bit với mã cố định 2 bit/ký hiệu.
File rỗng: k=0, original_size=0, encoded_bits=0, CRC=0; kích thước 27 byte.
Một byte lặp N lần: k=1, encoded_bits=N, payload toàn bit 0.

Khi giải nén, Python bắt buộc kiểm tra magic/version, k, độ dài header/payload, entries có thứ tự và freq>0, tổng freq=original_size, giới hạn 16 MiB, encoded_bits khớp bảng mã do C dựng, bit đệm bằng 0, giải mã hết đúng số bit và đúng số byte; không kết thúc giữa một mã; tần suất khôi phục khớp header và CRC khớp.
Một ký hiệu: kiểm tra toàn bộ bit thật đều 0, rồi khôi phục N byte.
CRC nhằm phát hiện hỏng ngẫu nhiên, không dùng để xác thực bảo mật.
Không trả file khôi phục khi kiểm tra thất bại.

## 8. Những file Kiệt phải bàn giao
- core/huffman.h: cấu trúc và API nội bộ C.
- core/huffman.c: heap, đếm tần suất, dựng cây, sinh mã, lịch sử.
- core/main.c: CLI, đọc bảng tần suất, xuất JSON.
- core/README.md: cách biên dịch Windows/Linux, hai lệnh, schema, lỗi và test.
- core/tests/test_core.py: dùng Python standard library, subprocess và unittest; không viết lại thuật toán Huffman.
- core/examples/banana.json: JSON thật sinh từ chương trình, không phải dữ liệu giả.
- core/ALGORITHM.md: thuật toán, tính tiền tố, lập luận tham lam/tính tối ưu, độ phức tạp; giải thích ở mức bảo vệ môn học.

Tên API nội bộ C do Kiệt quyết định và tài liệu hóa; giao diện liên nhóm chính thức là CLI/JSON trên, không phải ABI/shared library.

Lệnh build từ thư mục gốc dự án:
    gcc -std=c11 -O2 -Wall -Wextra -Wpedantic core/main.c core/huffman.c -o core/huffman_core.exe
Linux đổi đích thành core/huffman_core.
Không dùng system(), thư viện ngoài hoặc hàm chỉ có trên Linux; có kiểm tra malloc và giải phóng bộ nhớ.
Nếu chưa có GCC, hướng dẫn cài ngắn gọn theo môi trường thực tế; không dành cả buổi chỉnh IDE.

## 9. Kiểm thử cần có
1. BANANA khớp toàn bộ mẫu và số bit.
2. Rỗng, một byte lặp (cả byte 0x00), dữ liệu có 0xFF.
3. Đủ 256 giá trị byte mỗi giá trị một lần: 511 nút, 255 bước gộp, tất cả mã dài 8, encoded_bits=2048.
4. Nhiều byte bằng tần suất: gọi lại nhiều lần cho cùng kết quả.
5. UTF-8 tiếng Việt: đếm byte đúng, không coi một chữ là một byte.
6. analyze và tree trên cùng bảng tần suất cho JSON bằng nhau.
7. Kiểm tra mã tiền tố, mã không rỗng, trọng số mỗi cha bằng tổng hai con; root bằng original_size; số bước k-1 khi k>=1.
8. File không tồn tại, sai tham số, bảng thiếu/thừa số, số âm, ký tự lạ, tràn số, tổng vượt giới hạn.
9. Dữ liệu có mã dài hơn 8 bit để tránh lỗi giới hạn bộ đệm.
Có thể test giải mã trong Python bằng cách DUYỆT cây JSON; đó là bộ kiểm tra, không phải một lõi Huffman thứ hai.
Nêu rõ đã chạy test nào, môi trường nào, kết quả thực tế. Không tuyên bố test pass nếu chưa thực thi.

## 10. Yêu cầu làm việc ngay
- Bắt đầu bằng tóm tắt ngắn phần Kiệt và bắt tay tạo đầy đủ file C theo đặc tả.
- Ưu tiên analyze + tree + JSON đúng trước, sau đó lịch sử và test. Nếu bàn giao trung gian chưa đủ trường, phải ghi rõ chưa tương thích hoàn toàn; bản cuối bắt buộc đủ schema.
- Nếu có công cụ thực thi, biên dịch và chạy kiểm thử. Nếu không có, cung cấp nội dung đầy đủ từng file và lệnh để tôi chạy, không giả vờ đã chạy.
- Không hỏi lại lựa chọn đã chốt. Không đổi CLI, schema, quy tắc tie-break hoặc định dạng file.
- Nếu phát hiện mâu thuẫn thực sự, chỉ rõ chỗ đó và đề xuất sửa tối thiểu để Tín đồng bộ; không âm thầm đổi.
- Giải thích ngắn gọn các phần giúp tôi hiểu và thuyết trình.
- Cuối cùng trả bản bàn giao cho Tín: danh sách file, lệnh build/run, kết quả test thực tế, banana.json, lỗi còn lại.

