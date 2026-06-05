# Active Context

## Trọng tâm phát triển hiện tại
Chúng ta đã hoàn thành đợt nâng cấp chiến lược: **Chuyển đổi toàn diện Dashboard SPA sang kiến trúc ReactJS (Vite)** + **Di trú LLM sang 9Router** + **Tích hợp API Backend toàn diện**.

1. **🚀 Di trú giao diện sang ReactJS (Vite)** ✅:
   - Khởi tạo thư mục dự án frontend React chuyên biệt (`frontend/`).
   - Port toàn bộ hệ thống CSS Variables, Reset Styles và Glassmorphism sang `frontend/src/index.css`.
   - Viết component React tập trung [App.jsx](file:///d:/evo/chatbot/demo_langGraph/frontend/src/App.jsx) để quản lý trơn tru mọi trạng thái dữ liệu (Agents, Skills, Tools, Chat messages).

2. **📐 Tối ưu hóa layout 100% Full-Bleed (Lược bỏ Right Panel)** ✅:
   - **Cột trạng thái hệ thống và log bên phải đã được loại bỏ hoàn toàn** khỏi mã nguồn React UI.
   - Không gian chính của Khung Chat và các Tab quản trị (Agents, Kỹ năng, Tools) được tự động kéo giãn bao trọn 100% chiều rộng màn hình.

3. **📦 Đóng gói Production & Unified Web Server** ✅:
   - Vite build ra `frontend/dist/`, FastAPI tự động phục vụ bản build React tại `/` với fallback an toàn.

4. **💻 Thiết lập Proxy phát triển** ✅:
   - Cấu hình `vite.config.js` proxy cổng 3000 → backend cổng 8000, hỗ trợ Hot Reloading.

5. **🔌 Di trú LLM Provider sang 9Router** ✅:
   - Backend không còn phụ thuộc vào Groq API. Toàn bộ LLM config trỏ về 9Router proxy (`http://172.31.2.23:20128/v1`), model `evotek_flash`.

6. **🔗 Tích hợp API Backend toàn diện** ✅:
   - Toàn bộ App.jsx đã gọi `fetch()` API thực tế đến FastAPI: Chat (`POST /api/chat`), Agents CRUD, Skills (load/draft/publish/delete), Tools (CRUD + toggle), Login (RBAC). Không còn mock state nào.

## Hoàn thành gần đây
- **🔌 Di trú LLM Provider sang 9Router**: Backend không còn phụ thuộc trực tiếp vào Groq API. Toàn bộ LLM config được trỏ về 9Router proxy nội bộ (`http://172.31.2.23:20128/v1`). Biến môi trường `GROQ_API_KEY` đã được đổi thành `LLM_API_KEY` chung, `settings.py` đọc động từ `.env`.
- **🔗 Tích hợp API Backend**: Đã thay thế hoàn toàn mock state — `App.jsx` hiện gọi `fetch()` thực tế đến mọi endpoint FastAPI (Chat, Agents, Skills, Tools). Dữ liệu được lưu và đọc trực tiếp từ SQLite + file-system JSON.
- **📄 CV Processor**: Tính năng chuyển đổi CV PDF sang mẫu CV mới. Flow: upload PDF → pdfplumber extract text → LLM (9Router) trả JSON có cấu trúc → UI cho chỉnh sửa → Jinja2 render HTML template → browser print ra PDF. Accessible với mọi user đã đăng nhập (không giới hạn role). Các file chính: `backend/cv_agent.py`, `backend/api/cv_routes.py`, `backend/templates/cv_template.html`, `frontend/src/components/cv/CVProcessor.jsx`.

## Lưu ý kỹ thuật quan trọng (CV Processor)
- `cv_agent.py` phải đặt ở `backend/` root, **không** trong `backend/agents/` — nếu đặt trong `agents/` sẽ kéo theo `agents/__init__.py` → `instances.py` → `skills/loader.py` → `print(emoji)` → UnicodeEncodeError trên Windows cp1252.
- Prompt template chứa JSON schema có `{` `}` → dùng `.replace("{cv_text}", ...)` thay vì `.format()` để tránh `KeyError`.

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ cơ chế `user_id` query param hiện tại sang Token JWT bảo mật, tích hợp vào header `Authorization: Bearer <token>` cho mọi request API.
- **Cải thiện UI/UX Admin**: Tinh chỉnh trải nghiệm Skill Studio (HITL review flow), thêm loading skeletons, error boundaries.
- **Testing & Error Handling**: Bổ sung error handling toàn diện hơn cho các edge case (network failure, LLM timeout, etc).
