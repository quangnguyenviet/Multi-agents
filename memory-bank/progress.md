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
- [x] **Skill → LLM Node Integration**: `_build_system_prompt()` trong `llm_node.py` inject system_prompt từ skills có `agent_id: "llm_node"`. Tạo `cv_processor.json` skill hướng dẫn flow CV.
- [x] **Bug fix llm_node re-entry**: Khi LLM gọi lại sau ToolNode, nay luôn prepend `[SystemMessage, HumanMessage]` vào history.
- [x] **Logging**: Thêm `logging.basicConfig` trong `server.py` + `logger` trong `llm_node.py`.
- [x] **Generalize Chat Flow (bỏ hardcode CV)**: Đổi marker `"cv_id:"` → `"__html_id__:"`. Response API: `{"response": text, "rich_html": html|null}`.
- [x] **Xuất CV Word (.docx) qua Chat**: Tool `generate_cv_word_file()` tạo Bản Lý Lịch Chuyên Môn — bảng nhân sự, học vấn, kinh nghiệm 2 cột (ngày | chi tiết dự án với Tên Dự án / Vị trí / Công việc thực hiện / Công nghệ sử dụng). Endpoint download `GET /api/cv/download-word/{docx_id}`. Frontend nút tải về. `cv_agent.py` schema thêm `technologies` per experience entry.
- [x] **Xóa toàn bộ phần đa agent**: Bỏ 4 BaseAgent instances, bỏ `agent_id` routing trong skill system, bỏ filter `agent_id == "llm_node"`. `_build_system_prompt()` giờ load tất cả skills. Bỏ `GET /api/agents`, thêm `GET /api/user`. Đơn giản hóa tất cả skill endpoints và `main.py` CLI.
- [x] **Tool Registry theo coding agent pattern**: Xóa `storage/tool_store.py` + `storage/tools.json`. `GET /api/tools` giờ derive trực tiếp từ `TOOLS` list trong `llm_node.py` — trả về name + description từ docstring của `@tool` function. Xóa POST/PUT/DELETE tool endpoints. `ToolRegistry.jsx` redesign thành read-only display. Thêm tool mới = viết Python function.
- [x] **Skill System theo coding agent pattern + Progressive Disclosure**: Skill = file Markdown (`backend/skills/library/*.md`) với frontmatter `name`/`description` + body. `_build_system_prompt()` chỉ inject CATALOG (name+description), LLM gọi tool mới `load_skill(name)` để nạp body on-demand (TOOLS=9). `GET /api/skills` read-only trả `[{name, description}]`. Skill model rút gọn còn name/description/body; registry phẳng. Bỏ AI factory + endpoint draft/publish/create/delete. Frontend: App.jsx fetch `/api/skills` khi login, `SkillManager.jsx` read-only, xóa `SkillDraftModal.jsx`. Xóa code/data chết: `factory.py`, `skills/builtin/`, `skills/executor.py`, `agents/base_agent.py`, `storage/custom_skills/`.

## Trạng thái hiện tại
- **Workflow**: LangGraph ReAct — llm node bind **9 tools** (gồm `load_skill`), conditional edge tới ToolNode.
- **System Prompt**: `BASE_SYSTEM_PROMPT` + **CATALOG** skill (chỉ name+description). Progressive disclosure — body nạp on-demand qua `load_skill`.
- **Skill System**: file Markdown (`skills/library/*.md`) là source of truth, read-only. Frontmatter name/description + body. Không còn JSON/factory/CRUD.
- **Tool System**: Code là source of truth — `@tool` decorated functions trong `backend/tools/`. `GET /api/tools` derive từ `TOOLS` list. Không có CRUD tool qua UI.
- **Chat**: `POST /api/chat` (multipart Form) → LangGraph → tool calls (nếu cần) → `{"response": text, "rich_html": html|null, "word_download_url": url|null}`.
- **Rich HTML output**: Tool nào tạo HTML lưu vào `_cv_html_store`, trả `__html_id__: {id}`. Frontend hiển thị text + iframe.
- **Word output**: Tool `generate_cv_word_file` lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}`. Frontend hiển thị nút tải về `.docx`.
- **API Backend**: Chat, Skills, Tools (read-only), CV Processor — tất cả hoạt động.
- **Frontend**: Chat với file attach + rich HTML card + Word download card. Admin: Skills, Tools (read-only display).
- **Việc tiếp theo**: JWT authentication + TTL cho in-memory stores.
