# System Patterns

## Kiến trúc Hệ thống

### 1. LangGraph Workflow (ReAct Pattern)
- **Topology**: `START → llm ──[tool_calls?]──→ tools → llm → END`
- **`MultiAgentState`**: 5 fields — `user_id`, `user_name`, `query`, `agent_response`, `messages: Annotated[list, add_messages]`
- **`llm_node`** (`backend/agents/llm_node.py`):
  - `llm_with_tools = ChatOpenAI(...).bind_tools(TOOLS)` — khởi tạo ở module level
  - `_build_system_prompt()` — gọi mỗi request, ghép `BASE_SYSTEM_PROMPT` + skill prompts từ `skill_registry`
  - **Lần đầu VÀ re-entry**: đều prepend `[SystemMessage, HumanMessage(query)]` — re-entry thêm `+ existing_messages` để LLM không quên ngữ cảnh gốc
  - `agent_response` chỉ set khi `not response.tool_calls` (turn cuối)
- **`ToolNode`** (`langgraph.prebuilt`): tự động execute tool calls từ last AIMessage
- **`tools_condition`** (`langgraph.prebuilt`): conditional edge — `"tools"` nếu có tool_calls, else `END`

### 2. Tool Registry (7 tools hiện tại)
**`backend/tools/company_tools.py`**:
- `get_company_info()` — đọc `storage/company_info.json`
- `get_current_datetime()` — ngày giờ hệ thống
- `calculate(expression)` — eval toán học với math whitelist
- `get_company_employee_list()` — query SQLite employees table
- `get_demo_users_list()` — gọi API http://127.0.0.1:8080

**`backend/tools/cv_tools.py`**:
- `read_cv_file(file_id)` — tra `_pdf_store[file_id]` → `extract_cv_data()` → JSON string
- `generate_cv_file(cv_json)` — `json.loads()` → Jinja2 render → `_cv_html_store[cv_id]` → trả `"__html_id__: {id}"`
- **Convention HTML tool**: bất kỳ tool nào muốn trả rich HTML → lưu vào `_cv_html_store`, trả string chứa `__html_id__: {id}` → routes.py tự detect và forward về frontend

### 3. Skill → LLM Node Integration (Convention mới)
- **Convention**: skill có `metadata.agent_id == "llm_node"` → `system_prompt` được inject vào LangGraph workflow
- **`_build_system_prompt()`** trong `llm_node.py`: import `skill_registry` từ `.instances`, lọc skills theo `agent_id`, ghép prompts
- **Thêm behavior cho LLM**: tạo JSON file trong `storage/custom_skills/` với `agent_id: "llm_node"` — hiệu lực ngay, không cần restart, không cần sửa code
- **Ví dụ**: `cv_processor.json` hướng dẫn LLM gọi `read_cv_file → generate_cv_file` khi có file_id
- Skills cho `BaseAgent` (hr_policies, salary_management...) **không bị ảnh hưởng** — chỉ skills có `agent_id: "llm_node"` mới được inject

### 4. Rich HTML Output trong Chat — Flow (Generic)
```
Frontend FormData (user_id, query, file?)
  → POST /api/chat
  → routes.py: lưu PDF vào _pdf_store[file_id], inject file_id vào query
  → chatbot.ainvoke()
  → LangGraph: llm → tool(s) → llm → ... → END
  → routes.py post-process: quét ngược ToolMessages tìm "__html_id__:", lấy HTML từ _cv_html_store
  → return {"response": text, "rich_html": html | null}
  → Frontend App.jsx: botMsg.richHtml = data.rich_html
  → MessageItem: hiện text bubble + iframe bên dưới nếu richHtml tồn tại
```
**LLM không gọi generate_cv_file → không có rich_html → chỉ text response. Không có fallback.**

### 5. Chat Endpoint Pattern
- **`POST /api/chat`**: `Form(user_id, query)` + `File(file=None)` optional
- **Không set `Content-Type`** từ frontend — browser tự set `multipart/form-data; boundary=...`
- Response: `{"response": str, "rich_html": str | null}`
- Extensible: thêm loại output HTML mới → thêm tool trả `__html_id__:`, không cần sửa routes.py

### 6. Skill System (2 tầng)
- **Tầng 1 — BaseAgent skills** (`agent_id`: hr_policies, salary_management, system_admin, user_management): dùng cho skill enable/disable qua Admin UI (`/api/skills/publish`, `/api/delete_skill`)
- **Tầng 2 — LLM Node skills** (`agent_id`: llm_node): inject system_prompt vào LangGraph, ảnh hưởng trực tiếp đến hành vi LLM trong chat
- Cả 2 tầng đều lưu trên đĩa dưới dạng JSON tại `storage/custom_skills/`

### 7. Kiến trúc ReactJS Client
- **`App.jsx`**: `handleSendMessage(text, file=null)` — luôn dùng FormData; `botMsg.richHtml = data.rich_html || null`
- **`ChatInputBar.jsx`**: state `attachedFile`, nút 📎, file badge với ✕, placeholder generic "file đính kèm"
- **`MessageItem.jsx`**: luôn hiển thị `msg-bubble` (text); hiển thị thêm `rich-output-card` (iframe) nếu `msg.richHtml` tồn tại
- **Chat flow**: `POST /api/chat` (FormData) → `{response, rich_html?}` → append bot message với optional richHtml

### 8. Tích hợp LLM & Proxy
- **9Router LLM Proxy**: `http://172.31.2.23:20128/v1`, model `evotek_flash`
- **Vite Proxy**: Dev port 3000 → Backend port 8000 (loại bỏ CORS)
- **FastAPI Static**: Serve React build từ `/frontend/dist/`

### 9. CV Processor Pipeline (Standalone — trang riêng vẫn hoạt động)
- `POST /api/cv/extract`: pdfplumber → LLM (9Router) → JSON có cấu trúc
- `POST /api/cv/render`: JSON data → Jinja2 template → HTML A4 2 cột

## File Structure Backend
```
backend/
├── agents/
│   ├── workflow.py         ← build_multi_agent_system(), chatbot
│   ├── workflow_state.py   ← MultiAgentState TypedDict (5 fields)
│   ├── llm_node.py         ← llm_node + TOOLS (7) + _build_system_prompt()
│   ├── base_agent.py       ← BaseAgent class (skill execution)
│   ├── instances.py        ← skill_registry, 4 BaseAgent instances
│   └── __init__.py
├── tools/
│   ├── company_tools.py    ← 5 general tools
│   └── cv_tools.py         ← read_cv_file, generate_cv_file + in-memory stores
├── storage/
│   ├── company_info.json   ← dữ liệu công ty
│   └── custom_skills/      ← JSON skills (agent_id: llm_node | hr_policies | ...)
│       └── cv_processor.json ← skill hướng dẫn CV flow cho llm_node
├── cv_agent.py             ← extract_cv_data() — PHẢI ở backend/ root
└── api/
    ├── routes.py           ← /chat (Form+File), skills, tools, agents
    └── cv_routes.py        ← /cv/extract, /cv/render (standalone)
```
