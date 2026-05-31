# Progress

## Các mốc đã hoàn thành
- [x] Thiết kế UI Dashboard & Skill Studio mượt mà.
- [x] Di trú toàn bộ 5 Built-in Skills (Kỹ năng mặc định) thành tệp JSON động trong ổ đĩa `storage/custom_skills/`.
- [x] Đồng bộ hóa, xóa mã Python tĩnh để `main.py` nạp hoàn toàn động từ JSON.
- [x] Cấu hình định tuyến thông minh ưu tiên lựa chọn workspace tab hoạt động trên UI.
- [x] Tích hợp khả năng Tool Calling tự động vào cấu trúc `BaseAgent` và hoàn thiện Tool danh sách nhân viên công ty.
- [x] Khắc phục triệt để lỗi không cho bôi đen/sao chép chữ trên giao diện Web UI (gỡ bỏ CSS `user-select: none`).
- [x] Chuẩn hóa định dạng hiển thị log Console của Agent khi kích hoạt `[SKILL]` và thực thi `[TOOL]` đồng bộ với bộ định tuyến `[ROUTER]`.
- [x] Khắc phục lỗi `tool_use_failed` (Error 400) trên Groq/Llama bằng cách bổ sung chỉ thị System Instruction phân tách rõ ràng lượt gọi tool và lượt vẽ bảng.
- [x] Di trú toàn bộ dữ liệu giả lập (thông tin nhân viên & bảng lương) sang cơ sở dữ liệu SQLite thực tế (`data/company.db`).
- [x] Tích hợp "Tự động định tuyến (Auto-Router)": Phân loại ý định để gọi Agent tự động.
- [x] Quản lý Prompt & Khởi tạo Agent động: Accordion sửa prompt, và Modal tạo Agent tự động đồng bộ.
- [x] Thiết kế Workspace Quản lý Tools (Tool Registry) liên kết với Agent.
- [x] **[NEW] Chuyển đổi toàn diện sang ReactJS (Vite)**: Hoàn tất porting mã nguồn HTML/JS cũ sang component modular ReactJS trong `frontend/src/App.jsx`.
- [x] **[NEW] Streamline UI loại bỏ cột hệ thống bên phải**: Gỡ bỏ hoàn toàn panel CPU/RAM và logs bên phải theo yêu cầu của anh để tối ưu 100% diện tích cho Khung chat và các tab quản trị rộng rãi.
- [x] **[NEW] Unified Build & Hosting**: Thiết lập cơ chế build tĩnh Vite và tích hợp host trực tiếp + fallback an toàn bên trong server FastAPI `server.py`.

## Trạng thái hiện tại
- **Giao diện**: Hoàn thành ứng dụng ReactJS tuyệt đẹp, mượt mà, hỗ trợ RBAC phân quyền chặt chẽ trên giao diện.
- **Không gian làm việc**: Cột log bên phải đã được ẩn hoàn toàn giúp không gian chat và quản lý rộng lớn, tập trung.
- **Tương thích**: Server FastAPI tự động phục vụ bản build React khi đã build, hoặc fallback về trang nguyên mẫu cũ.
