# Product Context

## Tại sao dự án này tồn tại?
Hệ thống chatbot doanh nghiệp thường yêu cầu lập trình viên sửa code Python tĩnh mỗi khi cần thêm/đổi hành vi AI. Dự án này giải quyết bằng cách **động hóa Skill của AI**:
- Admin upload file `.md` lên MinIO Console để thêm/sửa skill — không cần sửa code, không cần restart.
- Nhân viên trò chuyện mượt mà, bảo mật thông tin theo role (RBAC).

## Trải nghiệm mong muốn
- **Admin**: Thêm skill mới bằng cách soạn file Markdown + upload lên MinIO. Quản lý users qua UI.
- **Nhân viên**: Chat với AI có tool calling thực tế (tra cứu nhân viên, xử lý CV, tính toán...).
