# System Patterns

## Kiến trúc Hệ thống

### 1. LangGraph Workflow (ReAct Pattern)
- **Topology**: `START → llm ──[tool_calls?]──→ tools → llm → END`
- **`MultiAgentState`**: 5 fields — `user_id`, `user_name`, `query`, `agent_response`, `messages: Annotated[list, add_messages]`
- **`llm_node`** (`backend/agents/llm_node.py`):
  - `llm_with_tools = ChatOpenAI(...).bind_tools(TOOLS)` — khởi tạo ở module level
  - `_build_system_prompt()` — gọi mỗi request, ghép `BASE_SYSTEM_PROMPT` + **CATALOG** skill (`- {name}: {description}`). KHÔNG nhồi body — progressive disclosure qua `load_skill`
  - **Lần đầu VÀ re-entry**: đều prepend `[SystemMessage, HumanMessage(query)]` — re-entry thêm `+ existing_messages`
  - `agent_response` chỉ set khi `not response.tool_calls` (turn cuối)
- **`ToolNode`** (`langgraph.prebuilt`): tự động execute tool calls từ last AIMessage
- **`tools_condition`** (`langgraph.prebuilt`): conditional edge — `"tools"` nếu có tool_calls, else `END`

### 2. Tool Registry (9 tools — coding agent pattern)
**Source of truth**: `@tool` decorated Python functions trong `backend/tools/`. Docstring = description hiển thị trên UI và gửi cho LLM.

**`backend/tools/company_tools.py`**:
- `get_company_info()` — đọc `storage/company_info.json`
- `get_current_datetime()` — ngày giờ hệ thống
- `calculate(expression)` — eval toán học với math whitelist
- `get_company_employee_list()` — query SQLite employees table
- `get_demo_users_list()` — gọi API http://127.0.0.1:8080

**`backend/tools/cv_tools.py`**:
- `read_cv_file(file_id)` — tra `_pdf_store[file_id]` → `extract_cv_data()` → JSON string
- `generate_cv_file(cv_json)` — Jinja2 render → `_cv_html_store[cv_id]` → trả `"__html_id__: {id}"`
- `generate_cv_word_file(cv_json)` — python-docx render Bản Lý Lịch Chuyên Môn → `_cv_docx_store[docx_id]` → trả `"__docx_id__: {id}"`

**`backend/tools/skill_tools.py`**:
- `load_skill(skill_name)` — tra `skill_registry.get(name)` → trả `skill.body` (hướng dẫn đầy đủ). Cơ chế progressive disclosure
- **Convention HTML tool**: lưu vào `_cv_html_store`, trả `__html_id__: {id}`
- **Convention Word tool**: lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}`

**Tool API**:
- `GET /api/tools` → derive từ `TOOLS` list trong `llm_node.py`, trả `{id, name, description, active: true}`
- **Không có** POST/PUT/DELETE — tools là code, không configurable qua UI
- **Thêm tool mới**: viết `@tool` function → import vào `llm_node.py` → thêm vào `TOOLS = [...]` → restart server

### 3. Skill System — Progressive Disclosure (coding agent pattern)
- **Source of truth**: file Markdown tại `backend/skills/library/*.md` với frontmatter `name`/`description` + body. `SkillLoader` quét `.md`, `_parse_skill_md()` tách frontmatter (PyYAML) → `Skill(name, description, body)` → `registry.register(skill)`.
- **`_build_system_prompt()`** trong `llm_node.py`: chỉ inject CATALOG `- {name}: {description}` + hướng dẫn "gọi `load_skill` để lấy chi tiết". KHÔNG nhồi body → tiết kiệm token, scale.
- **`load_skill(skill_name)`** (@tool): LLM tự gọi khi yêu cầu khớp một skill → trả `skill.body` → re-entry ToolNode, LLM làm theo. `description` PHẢI nêu rõ "khi nào dùng" để LLM quyết định nạp.
- **Thêm skill**: tạo file `.md` mới trong `skills/library/` → restart server. Read-only qua UI (giống tool).
- `cv_processor.md` hướng dẫn LLM: đọc CV → (dịch nếu cần) → HTML (`generate_cv_file`) hoặc Word (`generate_cv_word_file`).
- ⚠️ `print` trong loader/registry dùng ASCII `[SKILL]` (không emoji) để tránh UnicodeEncodeError cp1252 trên Windows.

### 4. Output Pattern trong Chat — Generic Flow
```
Frontend FormData (user_id, query, file?)
  → POST /api/chat
  → routes.py: lưu PDF vào _pdf_store[file_id], inject file_id vào query
  → chatbot.ainvoke()
  → LangGraph: llm → tool(s) → llm → ... → END
  → routes.py post-process: quét ngược ToolMessages tìm marker
      - "__html_id__:" → lấy HTML từ _cv_html_store
      - "__docx_id__:" → tạo word_download_url = /api/cv/download-word/{id}
  → return {"response": text, "rich_html": html|null, "word_download_url": url|null}
  → Frontend App.jsx: botMsg.richHtml, botMsg.wordDownloadUrl
  → MessageItem: hiện iframe nếu richHtml, hiện nút tải nếu wordDownloadUrl
```

### 5. Chat Endpoint Pattern
- **`POST /api/chat`**: `Form(user_id, query)` + `File(file=None)` optional
- **Không set `Content-Type`** từ frontend — browser tự set `multipart/form-data; boundary=...`
- Response: `{"response": str, "rich_html": str|null, "word_download_url": str|null}`
- **Thêm output format mới**: implement tool → lưu vào store, trả marker `__xxx_id__: {id}` → thêm detect trong routes.py → thêm endpoint serve file

### 6. Word Document Format — Bản Lý Lịch Chuyên Môn
Cấu trúc Word output (python-docx):
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

### 7. Skill Model & Registry (phẳng)
- `Skill` (pydantic): chỉ `name`, `description`, `body`. Bỏ hết field đa-agent cũ (skill_type, parameters, permission, examples, metadata, id, version).
- `SkillRegistry`: dict `name -> Skill`, chỉ `register(skill)` / `get(name)` / `list_all()`.
- `GET /api/skills` read-only → `[{name, description}]`. Không có draft/publish/create/delete.

### 8. Kiến trúc ReactJS Client
- **`App.jsx`**: `handleSendMessage(text, file=null)` — FormData; `botMsg.richHtml`, `botMsg.wordDownloadUrl`
- **`ChatInputBar.jsx`**: state `attachedFile`, nút đính kèm, file badge
- **`MessageItem.jsx`**: `msg-bubble` (text) + `rich-output-card` (iframe nếu richHtml) + `word-download-card` (nút tải nếu wordDownloadUrl)

### 9. Tích hợp LLM & Proxy
- **9Router LLM Proxy**: `http://172.31.2.23:20128/v1`, model `evotek_flash`
- **Vite Proxy**: Dev port 3000 → Backend port 8000
- **FastAPI Static**: Serve React build từ `/frontend/dist/`

### 10. CV Processor Pipeline
- `POST /api/cv/extract`: pdfplumber → LLM (9Router) → JSON có cấu trúc (incl. `technologies` per experience)
- `POST /api/cv/render`: JSON data → Jinja2 → HTML A4 2 cột
- `GET /api/cv/download-word/{docx_id}`: `_cv_docx_store[docx_id]` → StreamingResponse `.docx`

## File Structure Backend
```
backend/
├── agents/
│   ├── workflow.py         ← build_multi_agent_system(), chatbot
│   ├── workflow_state.py   ← MultiAgentState TypedDict (5 fields)
│   ├── llm_node.py         ← llm_node + TOOLS (9) + _build_system_prompt() (catalog)
│   ├── instances.py        ← skill_registry + SkillLoader
│   └── __init__.py
├── skills/                 ← SOURCE OF TRUTH cho skill (Markdown)
│   ├── base.py             ← Skill(name, description, body)
│   ├── loader.py           ← quét *.md + frontmatter (PyYAML)
│   ├── registry.py         ← dict name->Skill
│   └── library/
│       └── cv_processor.md ← skill: đọc CV → HTML hoặc Word tùy yêu cầu
├── tools/                  ← SOURCE OF TRUTH cho tool registry
│   ├── company_tools.py    ← 5 general @tool functions
│   ├── cv_tools.py         ← read_cv_file, generate_cv_file, generate_cv_word_file
│   │                          + _pdf_store, _cv_html_store, _cv_docx_store
│   └── skill_tools.py      ← load_skill (progressive disclosure)
├── storage/
│   └── company_info.json
├── cv_agent.py             ← extract_cv_data() — PHẢI ở backend/ root
│                              schema experience có trường technologies
└── api/
    ├── routes.py           ← /chat (Form+File), /skills + /tools (read-only), detect markers
    └── cv_routes.py        ← /cv/extract, /cv/render, /cv/download-word/{id}
```
