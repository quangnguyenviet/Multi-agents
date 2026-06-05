# Active Context

## Trọng tâm phát triển hiện tại
Đã hoàn thành 3 tính năng lớn trong các session gần đây:

1. **🛠️ Tool Node LangGraph** ✅:
   - Topology: `START → llm ──[tool_calls?]──→ tools → llm → END`
   - Sử dụng `langgraph.prebuilt.ToolNode` + `tools_condition`
   - 7 tools: `get_company_info`, `get_current_datetime`, `calculate`, `get_company_employee_list`, `get_demo_users_list`, `read_cv_file`, `generate_cv_file`

2. **📄 CV Processor tích hợp vào Chat** ✅:
   - 2 tools: `read_cv_file(file_id)` + `generate_cv_file(cv_json)`
   - `/api/chat` đổi từ JSON sang `multipart/form-data` (hỗ trợ file upload optional)
   - Frontend: nút 📎 trong chat input, CV preview card (iframe + Print) trong message bubble
   - routes.py: parse cv_id từ ToolMessage (quét ngược, `.split()[0]`)

3. **🔗 Skill → LLM Node Integration** ✅:
   - `llm_node.py` có `_build_system_prompt()` — load skills từ `skill_registry` có `metadata.agent_id == "llm_node"`
   - Tạo `storage/custom_skills/cv_processor.json` với `agent_id: "llm_node"` để hướng dẫn LLM gọi đúng flow CV
   - Convention: skill nào có `agent_id: "llm_node"` → system_prompt của nó được inject vào LangGraph
   - Thêm hành vi mới cho LLM chỉ cần tạo file JSON skill — không cần sửa code

## Cấu trúc backend/agents/ hiện tại
```
backend/agents/
├── workflow.py         ← START → llm → tools → llm → END
├── workflow_state.py   ← 5 fields: user_id, user_name, query, agent_response, messages
├── llm_node.py         ← LLM bind 7 tools, _build_system_prompt() load từ skill_registry
├── base_agent.py       ← còn dùng bởi instances.py
├── instances.py        ← skill_registry + 4 agent instances (skill management)
└── __init__.py
```

## Cấu trúc backend/tools/ hiện tại
```
backend/tools/
├── company_tools.py    ← get_company_info, get_current_datetime, calculate,
│                          get_company_employee_list, get_demo_users_list
└── cv_tools.py         ← read_cv_file, generate_cv_file
                           _pdf_store, _cv_html_store (in-memory dict)
```

## Lưu ý kỹ thuật quan trọng
- `/api/chat` dùng `Form(...)` + `File(None)` — **không còn là JSON endpoint**. Frontend phải gửi FormData (không set Content-Type header)
- `_pdf_store` / `_cv_html_store` là in-memory dict — đủ cho dev server single-process. Production cần Redis/tmp files
- `cv_agent.py` import `from cv_agent import extract_cv_data` — `cv_agent.py` phải ở `backend/` root (tránh UnicodeEncodeError Windows cp1252)
- `_build_system_prompt()` gọi mỗi request (lần đầu vào llm_node) — skill mới tạo xong có hiệu lực ngay không cần restart
- Skills cho llm_node phải có `metadata.agent_id == "llm_node"` — các skill khác (`hr_policies`, `salary_management`...) không bị inject vào LangGraph

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ `user_id` form param hiện tại sang Token JWT bảo mật
- **CV tool enhancement**: LLM đang pass toàn bộ JSON lớn vào `generate_cv_file` — có thể tối ưu để LLM chỉ chỉnh sửa phần cụ thể
- **Cleanup in-memory store**: Thêm TTL/auto-cleanup cho `_cv_html_store` để tránh memory leak lâu dài
