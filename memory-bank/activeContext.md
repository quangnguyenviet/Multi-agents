# Active Context

## Trọng tâm phát triển hiện tại
Các session gần đây đã hoàn thành:

1. **🔧 Bug fix llm_node re-entry** ✅:
   - Lỗi: khi LLM gọi lại sau ToolNode, `messages_to_send = existing_messages` làm mất SystemMessage + HumanMessage gốc → LLM quên ngữ cảnh
   - Fix: re-entry luôn dùng `[SystemMessage, HumanMessage] + existing_messages`

2. **📝 Logging** ✅:
   - `server.py`: `logging.basicConfig(level=INFO)`
   - `llm_node.py`: log từng lần gọi (first call / re-entry), tool calls, final response

3. **🌐 Generalize Chat Flow** ✅:
   - Marker `"__html_id__:"` và `"__docx_id__:"` (generic)
   - API response: `{"response": text, "rich_html": html|null, "word_download_url": url|null}`

4. **📄 Xuất CV Word (.docx) qua Chat** ✅:
   - Tool `generate_cv_word_file()` trong `cv_tools.py` (python-docx)
   - Endpoint: `GET /api/cv/download-word/{docx_id}`

5. **🧹 Xóa toàn bộ phần đa agent** ✅:
   - Bỏ 4 BaseAgent instances (hr, salary, system_admin, user_management) khỏi `instances.py`
   - Bỏ filter `agent_id == "llm_node"` trong `_build_system_prompt()` — giờ load **tất cả** skills
   - Bỏ agent_id routing trong `SkillLoader` và `SkillFactory`
   - Bỏ field `agent_id` khỏi `CreateSkillRequest`, `PublishSkillRequest`
   - Bỏ `GET /api/agents` (RBAC listing), thêm `GET /api/user` cho login
   - Đơn giản hóa các endpoints `/skills`, `/create_skill`, `/skills/draft`, `/skills/publish`, `/delete_skill`
   - Viết lại `main.py` CLI không còn multi-agent commands

## Cấu trúc backend/agents/ hiện tại
```
backend/agents/
├── workflow.py         ← START → llm → tools → llm → END
├── workflow_state.py   ← 5 fields: user_id, user_name, query, agent_response, messages
├── llm_node.py         ← LLM bind 8 tools, _build_system_prompt(), logging
├── base_agent.py       ← giữ lại file nhưng không còn được dùng
├── instances.py        ← skill_registry + skill_factory + SkillLoader (chỉ vậy thôi)
└── __init__.py
```

## Cấu trúc backend/tools/ hiện tại
```
backend/tools/
├── company_tools.py    ← get_company_info, get_current_datetime, calculate,
│                          get_company_employee_list, get_demo_users_list
└── cv_tools.py         ← read_cv_file, generate_cv_file, generate_cv_word_file
                           _pdf_store, _cv_html_store, _cv_docx_store (in-memory dicts)
```

## Lưu ý kỹ thuật quan trọng
- `/api/chat` dùng `Form(...)` + `File(None)` — **không còn là JSON endpoint**. Frontend phải gửi FormData (không set Content-Type header)
- `_pdf_store` bị xóa sau mỗi request. `_cv_html_store` và `_cv_docx_store` không bao giờ xóa — memory leak lâu dài
- `cv_agent.py` phải ở `backend/` root (tránh UnicodeEncodeError Windows cp1252)
- `_build_system_prompt()` gọi mỗi request, load **toàn bộ** skills từ registry — skill mới có hiệu lực ngay không cần restart
- Tool trả rich HTML: lưu vào `_cv_html_store`, trả `__html_id__: {id}`
- Tool trả Word file: lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}` → routes.py tạo `word_download_url`
- Login frontend gọi `GET /api/user?user_id=...` (không còn `/api/agents`)

## Cấu trúc Tool System hiện tại (coding agent pattern)
```
Thêm tool mới:
  1. Viết @tool function trong backend/tools/*.py
  2. Import vào backend/agents/llm_node.py
  3. Thêm vào TOOLS = [...] list
  4. Restart server → GET /api/tools tự hiển thị tool mới

Không còn:
  - storage/tool_store.py (đã xóa)
  - storage/tools.json (đã xóa)
  - POST/PUT/DELETE /api/tools (đã xóa)
  - ToolModal.jsx (đã xóa khỏi App.jsx)
  - toggleToolStatus / deleteTool handlers trong App.jsx (đã xóa)
```

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ `user_id` form param hiện tại sang Token JWT bảo mật
- **Cleanup in-memory store**: Thêm TTL/auto-cleanup cho `_cv_html_store` và `_cv_docx_store` để tránh memory leak
