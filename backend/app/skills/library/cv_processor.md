---
name: cv_processor
description: Chuyển đổi CV (PDF người dùng upload) thành file Word theo 1 trong 2 mẫu chuẩn của công ty, hỗ trợ dịch Anh/Việt. Dùng khi người dùng upload CV (context có file_id) hoặc yêu cầu tạo/chuyển đổi/xuất hồ sơ năng lực, lý lịch chuyên môn.
---

Khi người dùng upload CV (context chứa `file_id`), thực hiện đúng thứ tự:

1. **Đọc CV**: gọi `read_cv_file` với `file_id` → JSON có cấu trúc.
   - Nếu người dùng không upload file mới nhưng đã upload trong hội thoại này, lấy `file_id` từ lịch sử hội thoại và gọi lại — dữ liệu đã được cache, không cần upload lại.

2. **Tóm tắt nội dung CV**: sau khi đọc xong, trình bày ngắn gọn những gì đã trích xuất được — họ tên, vị trí, số năm kinh nghiệm, kỹ năng chính, học vấn — để người dùng xác nhận thông tin đúng. Sau đó gợi ý bước tiếp theo (xuất ra file Word).

3. **Chọn mẫu**: hệ thống có 2 mẫu Word:
   - **Mẫu 1 — Bản Lý Lịch Chuyên Môn** (nhân sự chủ chốt): bảng gọn, kinh nghiệm dạng thời gian | nội dung.
   - **Mẫu 2 — Hồ sơ năng lực chi tiết**: có TỔNG QUAN, CÔNG NGHỆ phân nhóm, từng dự án ghi Quy mô / Mô tả / Nhiệm vụ / Công nghệ.

   Xác định mẫu theo yêu cầu người dùng. Nếu người dùng KHÔNG nói rõ muốn mẫu nào, hãy HỎI họ chọn Mẫu 1 hay Mẫu 2 (và ngôn ngữ: tiếng Việt hay tiếng Anh) trước khi xuất.

4. **Dịch (nếu cần)**: nếu người dùng yêu cầu một ngôn ngữ cụ thể (tiếng Việt hoặc tiếng Anh), dịch toàn bộ nội dung văn bản trong JSON — `summary`, `summary_points`, `position`, `company`, `overview`, `description`, `education` (degree/field/institution), `skills`/`tech_stack`, `technologies`, project `name`/`description`, `languages` — sang ngôn ngữ đó TRƯỚC khi xuất.

5. **Xuất Word** (bắt buộc, không được bỏ qua): gọi `generate_cv_word_file` với JSON cuối cùng và `template_id` = `"1"` hoặc `"2"` theo mẫu đã chọn.
