# System Patterns

## Kiến trúc Hệ thống

### 1. LangGraph Workflow (ReAct Pattern) + Checkpointer
- **Topology**: `START → llm ──[tool_calls?]──→ tools → llm → END`
- **Checkpointer (cấu hình được)**: `workflow._make_checkpointer()` theo `DB_BACKEND` → `SqliteSaver` (dev, `data/checkpoints.db`, `check_same_thread=False`) hoặc `PostgresSaver` + `psycopg_pool.ConnectionPool` (prod). `.setup()` tạo bảng. Lịch sử persist theo `thread_id` = `conversation_id`. Gọi qua `asyncio.to_thread(chatbot.invoke, input, {"configurable":{"thread_id": conv_id}})` (node sync → saver sync). Version: `langgraph-checkpoint-sqlite>=2,<3` / `langgraph-checkpoint-postgres>=2,<3` (khớp langgraph 0.2.76).
- **`MultiAgentState`**: 5 fields — `user_id`, `user_name`, `query`, `agent_response`, `messages: Annotated[list, add_messages]` (history tích lũy qua checkpointer)
- **`llm_node`** (`backend/agents/llm_node.py`):
  - `llm_with_tools = ChatOpenAI(...).bind_tools(TOOLS)` — khởi tạo ở module level
  - `_build_system_prompt()` — gọi mỗi request, ghép `BASE_SYSTEM_PROMPT` + **CATALOG** skill. KHÔNG nhồi body — progressive disclosure qua `load_skill`
  - **History-aware**: lượt mới → thêm `HumanMessage(query)` vào history; re-entry (last là ToolMessage) → không thêm. Gọi LLM với `[SystemMessage] + existing_messages + new`. SystemMessage KHÔNG lưu (catalog luôn mới). Trả `new_messages` (human+response) cho reducer
  - `agent_response` chỉ set khi `not response.tool_calls` (turn cuối)
- **`ToolNode`** / **`tools_condition`** (`langgraph.prebuilt`): execute tool calls + conditional edge

### 2. Tool Registry (8 tools — coding agent pattern)
**Source of truth**: `@tool` decorated Python functions trong `backend/tools/`. Docstring = description hiển thị trên UI và gửi cho LLM.

**`backend/tools/company_tools.py`**:
- `get_company_info()` — đọc `storage/company_info.json`
- `get_current_datetime()` — ngày giờ hệ thống
- `calculate(expression)` — eval toán học với math whitelist
- `get_company_employee_list()` — query SQLite employees table
- `get_demo_users_list()` — gọi API http://127.0.0.1:8080

**`backend/tools/cv_tools.py`**:
- `read_cv_file(file_id)` — tra `_pdf_store[file_id]` → `extract_cv_data()` → JSON string
- `generate_cv_word_file(cv_json, template_id="1"|"2")` — python-docx → `_cv_docx_store[docx_id]` → trả `"__docx_id__: {id}"`. `_build_docx_template1` (Bản Lý Lịch Chuyên Môn) / `_build_docx_template2` (Hồ sơ năng lực chi tiết)

**`backend/tools/skill_tools.py`**:
- `load_skill(skill_name)` — tra `skill_registry.get(name)` → trả `skill.body` (hướng dẫn đầy đủ). Cơ chế progressive disclosure

- **Convention Word tool**: lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}` (HTML đã bỏ khỏi chat)

**Tool API**:
- `GET /api/tools` → derive từ `TOOLS` list trong `llm_node.py`, trả `{id, name, description, active: true}`
- **Không có** POST/PUT/DELETE — tools là code, không configurable qua UI
- **Thêm tool mới**: viết `@tool` function → import vào `llm_node.py` → thêm vào `TOOLS = [...]` → restart server

### 3. Skill System — Progressive Disclosure (coding agent pattern) + MinIO storage
- **Nguồn lưu trữ = MinIO** (bucket `skills`, mỗi object `.md` = 1 skill). `load_skills_from_minio()` (loader.py) gọi `storage/minio_skills.py` (`list_skill_objects` + `get_skill_text`), `_parse_skill_md()` tách frontmatter (PyYAML) → `Skill(name, description, body)`.
- **TTL cache**: `SkillRegistry(ttl_seconds, fetch_fn)` giữ skills trong RAM; `_ensure_fresh()` (gọi từ `get`/`list_all`) refresh từ MinIO khi quá `SKILLS_CACHE_TTL` (300s). `time.monotonic()` + `threading.Lock` (double-check) chống refresh đồng thời. Sửa skill trên MinIO → hiệu lực sau TTL, KHÔNG restart.
- **Degrade**: MinIO down → giữ cache cũ, vẫn cập nhật mốc (back-off). Startup lỗi → registry rỗng, server vẫn chạy. `instances.py` gọi `skill_registry.warm()` để nạp + log lúc startup.
- **Seed**: `skills/library/*.md` trong git để version control + upload (`scripts/sync_skills_to_minio.py`); runtime KHÔNG đọc local. `MINIO_ENDPOINT` = host:port (không scheme), scheme do `MINIO_SECURE`.
- **`_build_system_prompt()`** trong `llm_node.py`: chỉ inject CATALOG `- {name}: {description}` + hướng dẫn "gọi `load_skill` để lấy chi tiết". KHÔNG nhồi body → tiết kiệm token, scale.
- **`load_skill(skill_name)`** (@tool): LLM tự gọi khi yêu cầu khớp một skill → trả `skill.body` → re-entry ToolNode, LLM làm theo. `description` PHẢI nêu rõ "khi nào dùng" để LLM quyết định nạp.
- **Thêm skill**: tạo file `.md` mới trong `skills/library/` → restart server. Read-only qua UI (giống tool).
- `cv_processor.md` hướng dẫn LLM: đọc CV → chọn 1 trong 2 mẫu Word (không rõ thì hỏi) → (dịch Anh/Việt nếu cần) → `generate_cv_word_file(template_id="1"|"2")`.
- ⚠️ `print` trong loader/registry dùng ASCII `[SKILL]` (không emoji) để tránh UnicodeEncodeError cp1252 trên Windows.

### 4. Output Pattern trong Chat — Generic Flow
```
Frontend FormData (user_id, query, file?)
  → POST /api/chat
  → routes.py: lưu PDF vào _pdf_store[file_id], inject file_id vào query
  → chatbot.ainvoke()
  → LangGraph: llm → tool(s) → llm → ... → END
  → routes.py post-process: quét ngược ToolMessages tìm marker
      - "__docx_id__:" → tạo word_download_url = /api/cv/download-word/{id}
  → return {"response": text, "word_download_url": url|null}
  → Frontend App.jsx: botMsg.wordDownloadUrl
  → MessageItem: hiện nút tải nếu wordDownloadUrl
```

### 5. Chat Endpoint Pattern
- **`POST /api/chat`**: `Form(user_id, query, conversation_id)` + `File(file=None)` optional. `conversation_id` BẮT BUỘC (thread_id checkpointer)
- **Không set `Content-Type`** từ frontend — browser tự set `multipart/form-data; boundary=...`
- Invoke: `asyncio.to_thread(chatbot.invoke, {...}, {"configurable":{"thread_id": conversation_id}})`. Không truyền `messages` (checkpointer giữ)
- Quét `__docx_id__`: scan ngược `result["messages"]`, **dừng khi gặp HumanMessage** (chỉ lượt hiện tại)
- Sau mỗi lượt: `conversation_store.upsert(conversation_id, user_id, query)` (title = câu hỏi đầu)
- Response: `{"response": str, "word_download_url": str|null}`

### 5b. Conversation Management (chọn cuộc hội thoại cũ)
- **`storage/conversation_store.py`** (SQLite `data/conversations.db` dev / PostgreSQL prod theo `DB_BACKEND`): `conversations(id, user_id, title, created_at, updated_at)`. `upsert/list_for_user/owner/delete`. Placeholder `_PH` (`?`/`%s`), upsert `ON CONFLICT (id) DO UPDATE`, helper `_run()` đóng connection.
- `GET /api/conversations?user_id` → list (updated_at desc). `GET /api/conversations/{id}/messages?user_id` → nạp từ `chatbot.get_state` (Human→user, AIMessage có content→assistant). `DELETE /api/conversations/{id}?user_id` → xóa store + `workflow.delete_thread` (xóa checkpoint).
- Frontend: Sidebar danh sách (active highlight, xóa hover) + "Chat mới"; `App.jsx` loadConversation/deleteConversation/fetchConversations.
- **Thêm output format mới**: implement tool → lưu vào store, trả marker `__xxx_id__: {id}` → thêm detect trong routes.py → thêm endpoint serve file

### 6. Word Document Format — 2 mẫu (template_id)
**Mẫu 1 — Bản Lý Lịch Chuyên Môn** (`_build_docx_template1`, template_id="1"):
1. Tiêu đề "BẢN LÝ LỊCH CHUYÊN MÔN CỦA NHÂN SỰ CHỦ CHỐT" (căn giữa, bold, navy)
2. "Vị trí: [experience[0].position]"
3. Bảng 3 cột (`Table Grid`): `Thông tin nhân sự | Tên/Email/ĐT | Ngày sinh/Địa chỉ`
4. "Trình độ chuyên môn: [degree field] - [institution]"
5. Section heading "KINH NGHIỆM CHUYÊN MÔN"
6. Mỗi experience entry: bảng 2 cột — cột trái (ngày ~3.8cm) | cột phải (14.2cm):
   - **Tên Dự án**: `company`
   - **Vị trí công việc**: `position`
   - **Công việc thực hiện**: bullets từ `description[]`
   - **Công nghệ sử dụng**: `technologies` (field mới trong cv_agent.py schema)
7. Kỹ năng / Ngoại ngữ / Chứng chỉ (nếu có)

**Mẫu 2 — Hồ sơ năng lực chi tiết** (`_build_docx_template2`, template_id="2"):
1. Bảng `HỌ VÀ TÊN | full_name`, `VỊ TRÍ | position`
2. **TỔNG QUAN**: bullets từ `summary_points` (fallback `summary`)
3. **HỌC VẤN**: mỗi mục `start–end | field/degree + institution`
4. **NGÔN NGỮ**: bảng 4 cột — ngôn ngữ | Thành thạo | Khá | Trung bình, đánh dấu `(x)` theo `level` (so khớp đã bỏ dấu qua `_strip_accents`)
5. **CÔNG NGHỆ**: 5 nhóm từ `skills.tech_stack` (operating_systems/core/databases/tools/methodologies); fallback `core` ← `skills.technical`
6. **KINH NGHIỆM LÀM VIỆC (N dự án)**: mỗi dự án bảng 2 cột — Dự án(`company`)/Thời gian/Vị trí/Quy mô(`team_size`)/Mô tả(`overview`)/Nhiệm vụ(`description[]`)/Công nghệ(`technologies`)
- Tất cả block fallback an toàn khi thiếu trường.

### 7. Skill Model & Registry (phẳng)
- `Skill` (pydantic): chỉ `name`, `description`, `body`. Bỏ hết field đa-agent cũ (skill_type, parameters, permission, examples, metadata, id, version).
- `SkillRegistry`: dict `name -> Skill`, chỉ `register(skill)` / `get(name)` / `list_all()`.
- `GET /api/skills` read-only → `[{name, description}]`. Không có draft/publish/create/delete.

### 8. Kiến trúc ReactJS Client
- **`App.jsx`**: `handleSendMessage(text, file=null)` — FormData (kèm `conversation_id`); `botMsg.wordDownloadUrl`. State `conversationId` (uuid, sinh khi login/"Chat mới"/logout); `handleNewChat` reset chatMessages + id mới
- **`ChatWorkspace.jsx`**: nút **"Chat mới"** ở `chat-header` (prop `onNewChat`)
- **`ChatInputBar.jsx`**: state `attachedFile`, nút đính kèm, file badge
- **`MessageItem.jsx`**: `msg-bubble` (text) + `word-download-card` (nút tải `.docx` nếu wordDownloadUrl). Không còn iframe HTML / trang CV Processor

### 9. Tích hợp LLM & Proxy
- **9Router LLM Proxy**: `http://172.31.2.23:20128/v1`, model `evotek_flash`
- **Vite Proxy**: Dev port 3000 → Backend port 8000
- **FastAPI Static**: Serve React build từ `/frontend/dist/`

### 10. CV Processor — chỉ qua chat (đã bỏ trang riêng + HTML)
- Luồng: chat upload PDF → tool `read_cv_file` (pdfplumber → LLM → JSON) → (dịch) → `generate_cv_word_file(template_id)` → `__docx_id__`
- `GET /api/cv/download-word/{docx_id}`: `_cv_docx_store[docx_id]` → StreamingResponse `.docx`
- Đã xóa: `POST /cv/extract`, `POST /cv/render`, `templates/cv_template.html`, trang `CVProcessor.jsx`

## File Structure Backend
```
backend/
├── agents/
│   ├── workflow.py         ← build_multi_agent_system(checkpointer) + SqliteSaver (data/checkpoints.db)
│   ├── workflow_state.py   ← MultiAgentState TypedDict (5 fields)
│   ├── llm_node.py         ← llm_node + TOOLS (8) + _build_system_prompt() (catalog)
│   ├── instances.py        ← skill_registry(ttl, fetch_fn=load_skills_from_minio) + warm()
│   └── __init__.py
├── skills/
│   ├── base.py             ← Skill(name, description, body)
│   ├── loader.py           ← load_skills_from_minio() + _parse_skill_md (PyYAML)
│   ├── registry.py         ← TTL cache RAM (refresh từ MinIO)
│   └── library/            ← SEED (git) để upload — runtime KHÔNG đọc local
│       └── cv_processor.md
├── tools/                  ← SOURCE OF TRUTH cho tool registry
│   ├── company_tools.py    ← 5 general @tool functions
│   ├── cv_tools.py         ← read_cv_file, generate_cv_word_file (template 1|2)
│   │                          + _pdf_store, _cv_docx_store; _build_docx_template1/2
│   └── skill_tools.py      ← load_skill (progressive disclosure)
├── scripts/
│   └── sync_skills_to_minio.py  ← ensure bucket + upload seed *.md
├── storage/
│   ├── minio_skills.py     ← MinIO client wrapper (NGUỒN skill runtime)
│   ├── conversation_store.py ← metadata hội thoại (SQLite dev / Postgres prod)
│   ├── blob_store.py       ← blob tạm PDF/Word (in-memory dev / Redis prod, dict-like)
│   └── company_info.json
├── requirements.txt        ← base deps
├── requirements-prod.txt   ← postgres + redis (cài thêm khi production)
├── cv_agent.py             ← extract_cv_data() — PHẢI ở backend/ root
│                              schema: +summary_points, +experience.team_size/overview, +skills.tech_stack
└── api/
    ├── routes.py           ← /chat (+conversation_id), /conversations (list/messages/delete), /skills + /tools
    └── cv_routes.py        ← /cv/download-word/{id}
```
