# Active Context

## Trọng tâm phát triển hiện tại

### 🎯 Skill System redesign — "coding agent pattern" + Progressive Disclosure (MỚI NHẤT) ✅
Thiết kế lại skill giống skill của AI coding agent (Claude Code / Anthropic Agent Skills):
- **File Markdown là source of truth**: mỗi skill = 1 file `.md` tại `backend/skills/library/` với frontmatter (`name`, `description`) + body hướng dẫn. Viết tay, git-tracked.
- **Progressive disclosure**: `_build_system_prompt()` chỉ inject CATALOG (`- {name}: {description}` của mọi skill), KHÔNG nhồi body. Tool mới `load_skill(skill_name)` để LLM nạp hướng dẫn đầy đủ on-demand khi yêu cầu khớp một skill.
- **Bỏ AI factory**: xóa `skills/factory.py`, endpoint `POST /skills/draft|publish`, `POST /create_skill`, `DELETE /delete_skill`. `GET /api/skills` giờ read-only trả `[{name, description}]`.
- **Skill model rút gọn**: chỉ còn `name`, `description`, `body` (bỏ `id, version, skill_type, parameters, permission, examples, metadata`).
- **Registry phẳng**: dict `name -> Skill`, chỉ `register/get/list_all`.
- **TOOLS = 9** (thêm `load_skill`). `SKILLS_DIR = "./skills/library"`.
- **Frontend**: `App.jsx` giờ fetch `/api/skills` khi login (trước đây KHÔNG fetch → grid luôn rỗng). `SkillManager.jsx` redesign read-only (giống ToolRegistry). Xóa `SkillDraftModal.jsx` + 3 handler (draft/publish/delete).
- **Đã xóa code/data chết**: `skills/factory.py`, `skills/builtin/`, `skills/executor.py`, `agents/base_agent.py`, toàn bộ JSON legacy trong `storage/custom_skills/` (đã xóa cả thư mục).
- **Thêm skill mới** = tạo file `.md` trong `backend/skills/library/` → restart server.
- ⚠️ Lưu ý: dùng `print` ASCII (không emoji) trong loader/registry để tránh `UnicodeEncodeError` cp1252 trên Windows.

---

Các session trước đó đã hoàn thành:

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
├── llm_node.py         ← LLM bind 9 tools, _build_system_prompt() (catalog skill), logging
├── instances.py        ← skill_registry + SkillLoader (đã bỏ skill_factory)
└── __init__.py

backend/skills/
├── base.py             ← Skill model tối giản (name, description, body)
├── loader.py           ← quét *.md + frontmatter (PyYAML)
├── registry.py         ← dict name->Skill (register/get/list_all)
└── library/            ← SOURCE OF TRUTH: các file skill .md
    └── cv_processor.md
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
- `cv_agent.py` phải ở `backend/` root (tránh UnicodeEncodeError Windows cp1252). Tương tự: KHÔNG dùng emoji trong `print` (loader/registry dùng `[SKILL]` ASCII)
- `_build_system_prompt()` gọi mỗi request, inject **CATALOG** (name+description) của mọi skill — KHÔNG nhồi body. LLM gọi `load_skill(name)` để lấy chi tiết. Thêm/sửa file `.md` → cần restart server
- Tool trả rich HTML: lưu vào `_cv_html_store`, trả `__html_id__: {id}`
- Tool trả Word file: lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}` → routes.py tạo `word_download_url`
- Login frontend gọi `GET /api/user?user_id=...` (không còn `/api/agents`)

## Cấu trúc Tool & Skill System hiện tại (coding agent pattern)
```
Thêm TOOL mới:
  1. Viết @tool function trong backend/tools/*.py
  2. Import vào backend/agents/llm_node.py → thêm vào TOOLS = [...]
  3. Restart server → GET /api/tools tự hiển thị

Thêm SKILL mới:
  1. Tạo file backend/skills/library/<name>.md
     ---
     name: <name>
     description: <mô tả + KHI NÀO dùng — quyết định LLM có load không>
     ---
     <body: quy trình hướng dẫn>
  2. Restart server → vào catalog system prompt + GET /api/skills

Không còn (tool):  storage/tool_store.py, storage/tools.json, POST/PUT/DELETE /api/tools, ToolModal.jsx
Không còn (skill): skills/factory.py, skills/builtin/, storage/custom_skills/*.json,
                   POST /skills/draft|publish, POST /create_skill, DELETE /delete_skill, SkillDraftModal.jsx
```

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ `user_id` form param hiện tại sang Token JWT bảo mật
- **Cleanup in-memory store**: Thêm TTL/auto-cleanup cho `_cv_html_store` và `_cv_docx_store` để tránh memory leak
