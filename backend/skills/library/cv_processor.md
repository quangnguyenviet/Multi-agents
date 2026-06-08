---
name: cv_processor
description: Chuyển đổi CV (PDF người dùng upload) thành file Word theo 1 trong 2 mẫu chuẩn của công ty, hỗ trợ dịch Anh/Việt. Dùng khi người dùng upload CV (context có file_id) hoặc yêu cầu tạo/chuyển đổi/xuất hồ sơ năng lực, lý lịch chuyên môn.
---

Khi người dùng upload CV (context chứa `file_id`), thực hiện đúng thứ tự:

1. **Đọc CV**: gọi `read_cv_file` với `file_id` → JSON có cấu trúc.

2. **Chọn mẫu**: hệ thống có 2 mẫu Word:
   - **Mẫu 1 — Bản Lý Lịch Chuyên Môn** (nhân sự chủ chốt): bảng gọn, kinh nghiệm dạng thời gian | nội dung.
   - **Mẫu 2 — Hồ sơ năng lực chi tiết**: có TỔNG QUAN, CÔNG NGHỆ phân nhóm, từng dự án ghi Quy mô / Mô tả / Nhiệm vụ / Công nghệ.

   Xác định mẫu theo yêu cầu người dùng. Nếu người dùng KHÔNG nói rõ muốn mẫu nào, hãy HỎI họ chọn Mẫu 1 hay Mẫu 2 trước khi xuất.

3. **Dịch (nếu cần)**: nếu người dùng yêu cầu một ngôn ngữ cụ thể (tiếng Việt hoặc tiếng Anh), dịch toàn bộ nội dung văn bản trong JSON — `summary`, `summary_points`, `position`, `company`, `overview`, `description`, `education` (degree/field/institution), `skills`/`tech_stack`, `technologies`, project `name`/`description`, `languages` — sang ngôn ngữ đó TRƯỚC khi xuất.

4. **Xuất Word** (bắt buộc, không được bỏ qua): gọi `generate_cv_word_file` với JSON cuối cùng và `template_id` = `"1"` hoặc `"2"` theo mẫu đã chọn.
