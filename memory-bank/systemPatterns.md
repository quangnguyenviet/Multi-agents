# System Patterns

## LangGraph Workflow
- Topology: `START → llm ──[tool_calls?]──→ tools → llm → END` (ReAct)
- Checkpointer: `_make_checkpointer()` → `SqliteSaver` (dev) hoặc `PostgresSaver+ConnectionPool` (prod). Thread_id = conversation_id. Invoke qua `asyncio.to_thread(chatbot.invoke, input, {"configurable":{"thread_id": conv_id}})`
- `llm_node`: `ChatOpenAI.bind_tools(TOOLS)`. System prompt = BASE + CATALOG skill (name+description chỉ). History-aware: lượt mới thêm HumanMessage; re-entry (last=ToolMessage) không thêm. SystemMessage không lưu vào checkpointer.

## Tool Registry
- Source of truth: `@tool` functions trong `backend/tools/`. Docstring = description gửi cho LLM.
- `GET /api/tools` derive từ `TOOLS` list trong `llm_node.py`. Không có CRUD qua UI.
- Thêm tool: viết `@tool` → import vào `llm_node.py` → thêm vào `TOOLS` → restart.

## Skill System (Progressive Disclosure)
- Nguồn: MinIO bucket `skills`, mỗi object `.md` = 1 skill (frontmatter `name`/`description` + body).
- Cache RAM + TTL (`SKILLS_CACHE_TTL` 300s). MinIO down → giữ cache cũ / registry rỗng. Server không sập.
- `_build_system_prompt()` inject chỉ CATALOG. LLM gọi `load_skill(name)` on-demand → trả body → re-entry.
- Thêm skill: upload `.md` lên MinIO Console → hiệu lực sau TTL, không cần restart.

## Chat Endpoint
- `POST /api/chat`: `Form(user_id, query="", conversation_id)` + `File(file=None)`. Không set Content-Type (browser tự set boundary).
- File upload: lưu PDF vào `_pdf_store[file_id]`, inject `[file_id]` vào query.
- Post-process: quét ngược ToolMessages đến HumanMessage, tìm `__docx_id__:` → `word_download_url`.
- Response: `{"response": str, "word_download_url": str|null}`.
- Sau mỗi lượt: `conversation_store.upsert(conv_id, user_id, query)` (title = câu hỏi đầu).

## Conversation & User Store
- `conversation_store`: SQLite (`data/conversations.db`) dev / Postgres prod. `list_for_user`, `delete` + `workflow.delete_thread`.
- `user_store`: Postgres only. bcrypt trực tiếp. `POST /api/auth/login` → `{user_id, username, name, role}` / 401. Admin CRUD tại `GET/POST/PUT/DELETE /api/users`.

## CV Processor
- Luồng chat: upload PDF → `read_cv_file` → JSON → `generate_cv_word_file(template_id="1"|"2")` → `__docx_id__`.
- 2 mẫu: `_build_docx_template1` (Bản Lý Lịch Chuyên Môn) / `_build_docx_template2` (Hồ sơ năng lực). Chi tiết field → `cv_tools.py`.
- `GET /api/cv/download-word/{id}`: `_cv_docx_store[id]` → StreamingResponse `.docx`.

## LLM Proxy
- Endpoint: `http://172.31.2.23:20128/v1`, model `evotek_flash`. Vite dev proxy port 3000→8000.
