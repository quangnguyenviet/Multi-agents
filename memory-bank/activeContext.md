# Active Context

## Trọng tâm phát triển hiện tại
Các session gần đây đã hoàn thành:

1. **🔧 Bug fix llm_node re-entry** ✅:
   - Lỗi: khi LLM gọi lại sau ToolNode, `messages_to_send = existing_messages` làm mất SystemMessage + HumanMessage gốc → LLM quên ngữ cảnh (vd: "tạo CV tiếng Việt")
   - Fix: re-entry luôn dùng `[SystemMessage, HumanMessage] + existing_messages`

2. **📝 Logging** ✅:
   - `server.py`: `logging.basicConfig(level=INFO)`
   - `llm_node.py`: log từng lần gọi (first call / re-entry), tool calls, final response

3. **🌐 Generalize Chat Flow** ✅ (bỏ toàn bộ hardcode CV trong luồng chat):
   - Xóa fallback tự gọi `generate_cv_file` khi LLM không gọi
   - Marker đổi từ `"cv_id:"` → `"__html_id__:"` (generic cho mọi tool HTML)
   - API response: `{"response": text, "rich_html": html|null}` thay `{"response", "cv_html"}`
   - Frontend: `msg.richHtml`, CSS class `rich-output-*`, placeholder "file đính kèm"
   - MessageItem: luôn hiện text bubble + iframe bên dưới nếu `richHtml` tồn tại

## Cấu trúc backend/agents/ hiện tại
```
backend/agents/
├── workflow.py         ← START → llm → tools → llm → END
├── workflow_state.py   ← 5 fields: user_id, user_name, query, agent_response, messages
├── llm_node.py         ← LLM bind 7 tools, _build_system_prompt(), logging
├── base_agent.py       ← còn dùng bởi instances.py
├── instances.py        ← skill_registry + 4 agent instances (skill management)
└── __init__.py
```

## Cấu trúc backend/tools/ hiện tại
```
backend/tools/
├── company_tools.py    ← get_company_info, get_current_datetime, calculate,
│                          get_company_employee_list, get_demo_users_list
└── cv_tools.py         ← read_cv_file, generate_cv_file (marker: __html_id__)
                           _pdf_store, _cv_html_store (in-memory dict)
```

## Lưu ý kỹ thuật quan trọng
- `/api/chat` dùng `Form(...)` + `File(None)` — **không còn là JSON endpoint**. Frontend phải gửi FormData (không set Content-Type header)
- `_pdf_store` bị xóa sau mỗi request. `_cv_html_store` không bao giờ xóa — memory leak lâu dài nếu dùng nhiều
- `cv_agent.py` import `from cv_agent import extract_cv_data` — `cv_agent.py` phải ở `backend/` root (tránh UnicodeEncodeError Windows cp1252)
- `_build_system_prompt()` gọi mỗi request — skill mới tạo xong có hiệu lực ngay không cần restart
- Skills cho llm_node phải có `metadata.agent_id == "llm_node"` — các skill khác không bị inject vào LangGraph
- Tool muốn trả rich HTML: lưu HTML vào `_cv_html_store`, trả string chứa `__html_id__: {id}` — routes.py tự detect

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ `user_id` form param hiện tại sang Token JWT bảo mật
- **Cleanup in-memory store**: Thêm TTL/auto-cleanup cho `_cv_html_store` để tránh memory leak
