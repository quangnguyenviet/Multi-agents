# System Patterns

## LangGraph Workflow
- Topology: `START → llm ──[tool_calls?]──→ tools → llm → END` (ReAct)
- Checkpointer: `PostgresSaver` + `ConnectionPool` (psycopg_pool). Thread_id = conversation_id. Invoke qua `asyncio.to_thread(chatbot.invoke, input, {"configurable":{"thread_id": conv_id}})`
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

## Database Layer (SQLAlchemy + Alembic)
- Models: `backend/models/user.py` (User), `backend/models/conversation.py` (Conversation).
- Engine + session: `core/database.py` — `engine` + `SessionLocal`. URL tự convert `postgresql://` → `postgresql+psycopg://`.
- Stores dùng context manager: `with SessionLocal() as s:` — không còn raw SQL.
- Chỉ dùng Postgres. Schema do Alembic quản lý: `alembic upgrade head` trước khi deploy. Migration đầu: `alembic/versions/0001_initial.py`.
- Thêm cột/bảng mới: `alembic revision --autogenerate -m "mô tả"` → `alembic upgrade head`.

## CV Processor
- Luồng chat: upload PDF → `read_cv_file` → JSON cache → `generate_cv_word_file(template_id, language)` → `__docx_id__`.
- Cache: `_cv_json_store[file_id]` giữ JSON sau lần đọc đầu → follow-up message dùng lại không cần upload lại PDF.
- 2 mẫu: `_build_docx_template1` (Bản Lý Lịch Chuyên Môn) / `_build_docx_template2` (Hồ sơ năng lực). Chi tiết field → `cv_tools.py`.
- `language="vi"|"en"` — tất cả label/đề mục đã có song ngữ trong `_LABELS` dict.
- `GET /api/cv/download-word/{id}`: `_cv_docx_store[id]` → StreamingResponse `.docx`.

## LLM Proxy
- Endpoint: `http://172.31.2.23:20128/v1`, model `evotek_flash`. Vite dev proxy port 3000→8000.
