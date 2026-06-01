# Active Context

## Trọng tâm phát triển hiện tại
Chúng ta vừa hoàn thành đợt nâng cấp chiến lược: **Chuyển đổi toàn diện Dashboard SPA sang kiến trúc ReactJS (Vite)** hiện đại, modular và bền bỉ.

1. **🚀 Di trú giao diện sang ReactJS (Vite)**:
   - Khởi tạo thư mục dự án frontend React chuyên biệt (`frontend/`).
   - Port toàn bộ hệ thống CSS Variables, Reset Styles và Glassmorphism sang `frontend/src/index.css`.
   - Viết component React tập trung [App.jsx](file:///d:/evo/chatbot/demo_langGraph/frontend/src/App.jsx) để quản lý trơn tru mọi trạng thái dữ liệu (Agents, Skills, Tools, Chat messages) thay thế hoàn toàn cho cách thao tác DOM/JS tĩnh trước đó.

2. **📐 Tối ưu hóa layout 100% Full-Bleed (Lược bỏ Right Panel)**:
   - Theo yêu cầu của anh, **cột trạng thái hệ thống và log bên phải đã được loại bỏ hoàn toàn** khỏi mã nguồn React UI.
   - Nhờ đó, không gian chính của Khung Chat và các Tab quản trị (Agents, Kỹ năng, Tools) được tự động kéo giãn bao trọn 100% chiều rộng màn hình còn lại bên cạnh Sidebar, mang lại trải nghiệm quan sát thoáng đãng và đẳng cấp.

3. **📦 Đóng gói Production & Unified Web Server**:
   - Tích hợp cấu hình biên dịch tự động của Vite để xuất bản ứng dụng ra thư mục `frontend/dist/`.
   - Nâng cấp `server.py` để tự động phục vụ bản build React tại trang chủ `/` (mount thư mục `/assets` tĩnh) và tự động dùng cơ chế dự phòng (fallback) chuyển về nguyên mẫu HTML cũ nếu chưa build.

4. **💻 Thiết lập Proxy phát triển**:
   - Cấu hình `vite.config.js` proxy cổng 3000 sang backend cổng 8000, hỗ trợ chế độ Development nóng (`npm run dev`) giúp lập trình viên sửa code React cập nhật lập tức lên giao diện (Hot Reloading).

## Hoàn thành gần đây
- **🔌 Di trú LLM Provider sang 9Router**: Backend không còn phụ thuộc trực tiếp vào Groq API. Toàn bộ LLM config được trỏ về 9Router proxy nội bộ (`http://172.31.2.23:20128/v1`). Biến môi trường `GROQ_API_KEY` đã được đổi thành `LLM_API_KEY` chung, `settings.py` đọc động từ `.env`. 9Router mang lại token saving, format translation và multi-tier fallback.

## Nhiệm vụ tiếp theo
- **Tích hợp API Backend**: Thay thế các mock state hiện tại bằng các hàm gọi `fetch()` gọi API thực tế tới FastAPI để lưu "Lưu Prompt", "Khởi tạo Agent", "Xuất bản Skill" trực tiếp xuống cơ sở dữ liệu SQLite và ổ đĩa của Graph.
- **Xác thực JWT**: Nâng cấp phân quyền từ Session-based tạm thời sang Token JWT bảo mật.
