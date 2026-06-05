# Progress

## Các mốc đã hoàn thành
- [x] Thiết kế UI Dashboard & Skill Studio mượt mà.
- [x] Di trú toàn bộ 5 Built-in Skills thành tệp JSON động trong `storage/custom_skills/`.
- [x] Đồng bộ hóa, xóa mã Python tĩnh để `main.py` nạp hoàn toàn động từ JSON.
- [x] Cấu hình định tuyến thông minh ưu tiên lựa chọn workspace tab hoạt động trên UI.
- [x] Tích hợp Tool Calling tự động vào `BaseAgent` và hoàn thiện Tool danh sách nhân viên.
- [x] Khắc phục lỗi không cho bôi đen/sao chép chữ trên Web UI.
- [x] Chuẩn hóa định dạng log Console của Agent khi kích hoạt `[SKILL]` và thực thi `[TOOL]`.
- [x] Khắc phục lỗi `tool_use_failed` (Error 400) trên Groq/Llama.
- [x] Di trú dữ liệu sang SQLite thực tế (`data/company.db`).
- [x] Tích hợp Auto-Router: phân loại ý định để gọi Agent tự động.
- [x] Quản lý Prompt & Khởi tạo Agent động.
- [x] Workspace Quản lý Tools (Tool Registry).
- [x] **Chuyển đổi toàn diện sang ReactJS (Vite)**: Hoàn tất porting sang component modular ReactJS.
- [x] **Streamline UI**: Gỡ bỏ cột log bên phải, tối ưu 100% diện tích.
- [x] **Unified Build & Hosting**: Vite build + FastAPI host tĩnh.
- [x] **Di trú từ Groq sang 9Router**: `LLM_BASE_URL=http://172.31.2.23:20128/v1`, model `evotek_flash`.
- [x] **Tích hợp API Backend toàn diện**: Thay mock state bằng `fetch()` API thực tế.
- [x] **CV Processor**: PDF → pdfplumber → LLM JSON → React form → Jinja2 HTML → print PDF.
- [x] **[NEW] Single LLM Node**: Gộp 5 agent nodes + router thành 1 node `llm` duy nhất. Topology: `START → llm → END`. Xóa 6 file agent không còn dùng.
- [x] **[NEW] Đơn giản hóa Frontend**: Bỏ agent selection dropdown, bỏ AgentManager UI, bỏ `/admin/agents` route. Chat gửi `{user_id, query}`, nhận `{response}`.

## Trạng thái hiện tại
- **Workflow**: LangGraph đơn giản — 1 node LLM, không RBAC, không routing.
- **Chat**: `POST /api/chat` → `llm_node` → 9Router → phản hồi.
- **API Backend**: Tất cả endpoint hoạt động (Chat, Skills, Tools, CV). Agent CRUD endpoints vẫn tồn tại ở backend nhưng không còn UI.
- **Frontend**: Giao diện đơn giản — Chat + CV Processor + (Admin: Skills, Tools).
- **Việc tiếp theo**: Xác thực JWT.
