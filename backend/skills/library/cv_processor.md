---
name: cv_processor
description: Xử lý file CV PDF — đọc, trích xuất và tạo bản CV đẹp dạng HTML hoặc Word (.docx). Dùng khi người dùng upload file CV (context có file_id) hoặc yêu cầu tạo/cải thiện/xuất CV.
---

Khi người dùng upload file CV (context chứa `file_id`), thực hiện đúng thứ tự sau:

1. **Đọc CV**: Gọi tool `read_cv_file` với `file_id` để lấy dữ liệu JSON có cấu trúc.

2. **Dịch (nếu cần)**: Nếu người dùng yêu cầu một ngôn ngữ cụ thể (ví dụ tiếng Việt), hãy dịch toàn bộ nội dung văn bản trong JSON — bao gồm `summary`, `position`, `company`, `experience description`, `education degree/field`, `skills`, project `name`/`description` — sang ngôn ngữ đó TRƯỚC khi sang bước tiếp theo.

3. **Xuất bản CV** (bắt buộc, không được bỏ qua): xác định định dạng đầu ra theo yêu cầu người dùng:
   - Yêu cầu **Word / .docx** → gọi `generate_cv_word_file` với JSON cuối cùng.
   - Không nêu rõ, hoặc yêu cầu **HTML / xem trực tiếp** → gọi `generate_cv_file`.
