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
- [x] **Single LLM Node**: Gộp 5 agent nodes + router thành 1 node `llm` duy nhất. Topology: `START → llm → END`. Xóa 6 file agent không còn dùng.
- [x] **Đơn giản hóa Frontend**: Bỏ agent selection dropdown, bỏ AgentManager UI, bỏ `/admin/agents` route.
- [x] **Tool Node LangGraph**: Thêm `ToolNode` + conditional edge. Topology: `START → llm → [tools] → llm → END`. 7 tools.
- [x] **CV Processor tích hợp Chat**: 2 tools `read_cv_file` + `generate_cv_file`. LLM tự gọi tool khi nhận file_id. `/api/chat` đổi sang multipart/form-data. Frontend: nút đính kèm PDF + CV preview card trong chat.
- [x] **[NEW] Skill → LLM Node Integration**: `_build_system_prompt()` trong `llm_node.py` inject system_prompt từ skills có `agent_id: "llm_node"`. Tạo `cv_processor.json` skill hướng dẫn flow CV. Convention mới: thêm behavior cho LLM = tạo JSON skill, không cần sửa code.

## Trạng thái hiện tại
- **Workflow**: LangGraph ReAct — llm node bind 7 tools, conditional edge tới ToolNode.
- **System Prompt**: Dynamic — `BASE_SYSTEM_PROMPT` + skill prompts có `agent_id == "llm_node"` từ `skill_registry`.
- **Chat**: `POST /api/chat` (multipart Form) → LangGraph → tool calls (nếu cần) → phản hồi + optional `cv_html`.
- **CV in Chat**: Upload PDF → LLM gọi `read_cv_file` → `generate_cv_file` → iframe CV + Print button.
- **API Backend**: Chat, Skills, Tools, CV Processor trang riêng — tất cả hoạt động.
- **Frontend**: Chat với file attach + CV preview card. Admin: Skills, Tools.
- **Việc tiếp theo**: JWT authentication.
