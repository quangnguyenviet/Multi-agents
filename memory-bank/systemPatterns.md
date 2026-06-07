# System Patterns

## Kiến trúc Hệ thống

### 1. LangGraph Workflow (ReAct Pattern)
- **Topology**: `START → llm ──[tool_calls?]──→ tools → llm → END`
- **`MultiAgentState`**: 5 fields — `user_id`, `user_name`, `query`, `agent_response`, `messages: Annotated[list, add_messages]`
- **`llm_node`** (`backend/agents/llm_node.py`):
  - `llm_with_tools = ChatOpenAI(...).bind_tools(TOOLS)` — khởi tạo ở module level
  - `_build_system_prompt()` — gọi mỗi request, ghép `BASE_SYSTEM_PROMPT` + skill prompts từ `skill_registry`
  - **Lần đầu VÀ re-entry**: đều prepend `[SystemMessage, HumanMessage(query)]` — re-entry thêm `+ existing_messages`
  - `agent_response` chỉ set khi `not response.tool_calls` (turn cuối)
- **`ToolNode`** (`langgraph.prebuilt`): tự động execute tool calls từ last AIMessage
- **`tools_condition`** (`langgraph.prebuilt`): conditional edge — `"tools"` nếu có tool_calls, else `END`

### 2. Tool Registry (8 tools hiện tại)
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
- **Convention HTML tool**: lưu vào `_cv_html_store`, trả `__html_id__: {id}`
- **Convention Word tool**: lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}`

### 3. Skill → LLM Node Integration
- **`_build_system_prompt()`** trong `llm_node.py`: import `skill_registry` từ `.instances`, ghép `system_prompt` của **tất cả** skills từ `skill_registry.list_all()`
- **Thêm behavior cho LLM**: tạo JSON file bất kỳ trong `storage/custom_skills/` — có hiệu lực ngay, không cần restart, không cần khai báo `agent_id`
- `cv_processor.json` hướng dẫn LLM: nếu yêu cầu HTML → gọi `generate_cv_file`; nếu yêu cầu Word/docx → gọi `generate_cv_word_file`

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

### 7. Skill System (1 tầng phẳng)
- Tất cả skills lưu dưới dạng JSON tại `storage/custom_skills/`
- Tất cả đều được inject vào `_build_system_prompt()` — không phân biệt agent_id
- `SkillLoader` đăng ký với `registry.register(skill, [])` — không routing
- `GET /api/skills` trả toàn bộ skills, không filter

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
│   ├── llm_node.py         ← llm_node + TOOLS (8) + _build_system_prompt()
│   ├── base_agent.py       ← BaseAgent class (skill execution)
│   ├── instances.py        ← skill_registry, 4 BaseAgent instances
│   └── __init__.py
├── tools/
│   ├── company_tools.py    ← 5 general tools
│   └── cv_tools.py         ← read_cv_file, generate_cv_file, generate_cv_word_file
│                              + _pdf_store, _cv_html_store, _cv_docx_store
├── storage/
│   ├── company_info.json
│   └── custom_skills/
│       └── cv_processor.json  ← skill llm_node: HTML hoặc Word tùy yêu cầu
├── cv_agent.py             ← extract_cv_data() — PHẢI ở backend/ root
│                              schema experience có trường technologies
└── api/
    ├── routes.py           ← /chat (Form+File), detect __html_id__ + __docx_id__
    └── cv_routes.py        ← /cv/extract, /cv/render, /cv/download-word/{id}
```
