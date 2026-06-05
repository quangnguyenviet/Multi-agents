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
- [x] **[NEW] Di trú từ Groq sang 9Router**: Thay thế toàn bộ cấu hình Groq API bằng 9Router proxy. Đổi `GROQ_API_KEY` → `LLM_API_KEY`, cập nhật `LLM_BASE_URL` về `http://172.31.2.23:20128/v1`, model `evotek_flash`. Cập nhật `settings.py` đọc tất cả biến LLM từ environment.
- [x] **[NEW] Tích hợp API Backend toàn diện**: Thay thế toàn bộ mock state trong `App.jsx` bằng `fetch()` API thực tế đến FastAPI. Chat gọi `POST /api/chat` qua LangGraph + 9Router. Agents/Skills/Tools CRUD đọc/ghi trực tiếp SQLite + file-system JSON qua API. Không còn mock data.

## Trạng thái hiện tại
- **Giao diện**: Hoàn thành ứng dụng ReactJS tuyệt đẹp, mượt mà, hỗ trợ RBAC phân quyền chặt chẽ trên giao diện.
- **Chat**: Hoạt động thực tế 100% — `App.jsx` gọi `POST /api/chat` → LangGraph → 9Router LLM → phản hồi thật.
- **API Backend**: Tất cả endpoint (Agents, Skills, Tools, Chat) đã được tích hợp đầy đủ qua `fetch()`, không còn mock.
- **Không gian làm việc**: Cột log bên phải đã được ẩn hoàn toàn, không gian chat và quản lý rộng 100%.
- **Tương thích**: Server FastAPI tự động phục vụ bản build React khi đã build, hoặc fallback về trang nguyên mẫu cũ.
- **Việc tiếp theo**: Xác thực JWT (thay `user_id` query param bằng Bearer token).
