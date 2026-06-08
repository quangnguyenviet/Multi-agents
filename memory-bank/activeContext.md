# Active Context

## Trọng tâm phát triển hiện tại

### 👤 User Management — đăng nhập thật + CRUD qua UI (MỚI NHẤT) ✅
Thay login dropdown hardcoded bằng hệ thống đăng nhập username/password thật, lưu trong Postgres, admin quản lý được users qua UI.
- **`backend/storage/user_store.py`** (Postgres only): bảng `users(id, username, password_hash, name, role, created_at)`. Dùng `bcrypt` trực tiếp (không passlib — không tương thích bcrypt>=4.0). Hàm: `init_table`, `seed_default_users`, `verify_password`, `get_by_id`, `list_all`, `create_user`, `update_user`, `delete_user`. Seed mặc định: `admin/admin123/admin`, `user1/user123/user`.
- **API mới** (`routes.py`): `POST /api/auth/login` (JSON `{username,password}` → `{user_id,username,name,role}` hoặc 401), `GET /api/users` (admin), `POST /api/users` (admin), `PUT /api/users/{id}` (admin), `DELETE /api/users/{id}` (admin, không tự xóa chính mình). `GET /api/user?user_id=` giữ lại dùng user_store thay vì employees table.
- **`server.py`**: gọi `user_store.init_table()` + `user_store.seed_default_users()` khi startup (bao try/except).
- **`requirements.txt`**: thêm `bcrypt>=4.0.0`.
- **`LoginScreen.jsx`**: viết lại — form 2 field (username, password), error inline, loading state. Prop đổi từ `handleQuickLogin` → `handleLogin`.
- **`App.jsx`**: `handleLogin(username, password)` gọi `POST /api/auth/login`, state `users` + `fetchUsers()` (admin), route `/admin/users` → `<UserManager>`, truyền `usersCount` vào Sidebar.
- **`UserManager.jsx`** (mới): bảng danh sách users, form thêm user mới (username/password/name/role), nút sửa (modal: name/role/đổi password tùy chọn), nút xóa. Admin không tự xóa mình được.
- **`Sidebar.jsx`**: thêm NavLink "Quản lý Users" cho admin (badge usersCount, màu accent).
- **`index.css`**: thêm `.login-input`, `.login-input-wrapper`, `.login-error`, `.user-table`, `.user-add-form`, `.user-modal-*`, `.role-badge`, `.user-action-btn`.
- ⚠️ `passlib` không tương thích `bcrypt>=4.0` (`__about__` removed → crash khi hash). Đã bỏ passlib, dùng `bcrypt.hashpw`/`bcrypt.checkpw` trực tiếp.
- ⚠️ psycopg3 `Connection` không có `executemany()` — phải dùng `conn.cursor().executemany()`.
- ⚠️ User store Postgres only — không có SQLite fallback (khác conversation_store). Nếu `DB_BACKEND != postgres` thì user store không hoạt động.

### 🔌 Storage backend cấu hình được: SQLite↔Postgres + Redis ✅
Refactor để đổi nguồn lưu trữ qua env, sẵn cho production. **Default (env trống) = SQLite + in-memory = y hệt trước** (tương thích ngược tuyệt đối, lazy import nên dev không cần cài driver mới).
- **Config** (`settings.py`): `DB_BACKEND` (sqlite|postgres), `DATABASE_URL`, `REDIS_URL` (rỗng = in-memory), `BLOB_TTL`.
- **Checkpointer** (`workflow.py`): factory `_make_checkpointer()` → `SqliteSaver` (dev) hoặc `PostgresSaver` + `psycopg_pool.ConnectionPool` (production, xử lý concurrency). `.setup()` tự tạo bảng.
- **conversation_store.py**: chọn sqlite3/psycopg theo `DB_BACKEND`; placeholder `_PH` (`?`/`%s`); upsert hợp nhất bằng `ON CONFLICT (id) DO UPDATE`; helper `_run()` đóng connection đúng (sqlite cần commit, psycopg autocommit). Chữ ký hàm KHÔNG đổi → routes y nguyên.
- **blob_store.py** (mới): `make_blob_store(prefix)` → `_MemoryBlobStore` (dict) hoặc `_RedisBlobStore` (bytes + TTL, share đa worker). Interface dict-like (`[]`, `.get`, `.pop`, `in`). `cv_tools._pdf_store/_cv_docx_store` dùng nó — **fix luôn rò rỉ `_cv_docx_store`** khi dùng Redis.
- **`requirements-prod.txt`** (tách riêng): `langgraph-checkpoint-postgres`, `psycopg[binary]`, `psycopg-pool`, `redis`.
- **docker-compose**: thêm `postgres` + `redis` dưới `profiles:["prod"]` (`docker compose --profile prod up -d`). DEV_COMMANDS có hướng dẫn.
- employees/`company.db` ngoài phạm vi (vẫn SQLite — demo seed).

### 🗂️ UI chọn cuộc hội thoại cũ — danh sách + nạp lại + xóa ✅
Thêm quản lý nhiều cuộc hội thoại trên UI (sidebar trái, kiểu ChatGPT):
- **Store mới** `backend/storage/conversation_store.py` (SQLite `data/conversations.db`): bảng `conversations(id, user_id, title, created_at, updated_at)`. `upsert` (tạo mới đặt title = câu hỏi đầu, hoặc cập nhật updated_at), `list_for_user`, `owner`, `delete`.
- **Endpoints** (routes.py): `GET /api/conversations?user_id` (list mới nhất trước), `GET /api/conversations/{id}/messages?user_id` (nạp lại từ `chatbot.get_state` → map Human→user, AIMessage có content→assistant; cắt phần ghi chú file), `DELETE /api/conversations/{id}?user_id` (xóa store + `delete_thread` checkpoint). `/api/chat` gọi `conversation_store.upsert(...)` sau mỗi lượt.
- **`workflow.py`**: thêm `delete_thread(thread_id)` (dùng `SqliteSaver.delete_thread`).
- **Frontend**: `App.jsx` state `conversations` + `fetchConversations` (khi login & sau mỗi lượt gửi), `loadConversation` (nạp messages → setChatMessages + setConversationId), `deleteConversation`. `Sidebar.jsx` hiển thị danh sách (title, active highlight, nút xóa hover) + nút "Chat mới" (đã chuyển từ header ChatWorkspace sang sidebar). CSS `.conv-*` trong index.css.
- ⚠️ Nạp lại history chỉ hiện text (không khôi phục nút tải Word lượt cũ — `_cv_docx_store` in-memory mất khi restart).

### 💬 Chat nhớ lịch sử hội thoại — LangGraph checkpointer + SQLite ✅
Trước đây chat KHÔNG nhớ giữa các lượt (compile không checkpointer, ainvoke state mới mỗi request). Đã thêm trí nhớ:
- **Checkpointer SQLite**: `workflow.py` compile `chatbot` với `SqliteSaver(sqlite3.connect("data/checkpoints.db", check_same_thread=False))` + `.setup()`. Bền qua restart. `build_multi_agent_system(checkpointer=None)`.
- **Per-conversation**: `/api/chat` nhận `conversation_id` (Form) → `thread_id`. Mỗi cuộc 1 thread, lịch sử độc lập.
- **llm_node rework**: dùng `state["messages"]` (history đã persist). Lượt mới → thêm `HumanMessage(query)` vào history; re-entry (sau ToolNode) → không thêm. SystemMessage dựng mỗi lần gọi (catalog skill luôn mới), KHÔNG lưu. Trả `new_messages` (human + response) cho add_messages reducer. (Bỏ logic prepend hacky cũ.)
- **Invoke sync trong thread**: `await asyncio.to_thread(chatbot.invoke, input, config)` (node/tool đều sync → dùng SqliteSaver sync, tránh AsyncSqliteSaver + refactor lifecycle).
- **Quét `__docx_id__` chỉ trong lượt hiện tại**: scan ngược `result["messages"]`, dừng khi gặp `HumanMessage` → không lấy nhầm file Word của lượt cũ.
- **Frontend**: `App.jsx` giữ `conversationId` (uuid, sinh khi login/"Chat mới"/logout), gửi kèm mỗi lượt. Nút **"Chat mới"** ở `ChatWorkspace` header → reset chatMessages + conversation_id mới.
- ⚠️ **Version pin**: `langgraph 0.2.76` (core) chỉ hợp `langgraph-checkpoint-sqlite>=2.0,<3` (bản 3.x serialize metadata bằng json.dumps → lỗi Message not serializable). requirements pin `<3`.
- Lưu ý tương lai: history gửi nguyên mỗi lượt → token tăng dần (chưa cắt/tóm tắt). `data/checkpoints.db` đã gitignore.

### 📄 CV Processor — 2 mẫu Word + dịch Anh/Việt, bỏ HTML & trang riêng ✅
Yêu cầu gốc: user vứt CV bất kỳ → AI xuất ra **1 trong 2 mẫu file Word** theo yêu cầu + dịch Anh/Việt. Chỉ xử lý qua **chat**.
- **2 mẫu Word** trong 1 tool: `generate_cv_word_file(cv_json, template_id="1"|"2")`.
  - `_build_docx_template1` = Bản Lý Lịch Chuyên Môn (nhân sự chủ chốt) — như cũ.
  - `_build_docx_template2` = Hồ sơ năng lực chi tiết: HỌ TÊN / VỊ TRÍ / TỔNG QUAN / HỌC VẤN / NGÔN NGỮ (lưới mức Thành thạo·Khá·Trung bình, đánh dấu (x)) / CÔNG NGHỆ (5 nhóm) / KINH NGHIỆM (mỗi dự án: Quy mô, Mô tả, Nhiệm vụ, Công nghệ).
- **Schema mở rộng** (`cv_agent.py`, additive optional): `summary_points[]`, `experience[].team_size`, `experience[].overview`, `skills.tech_stack{operating_systems,core,databases,tools,methodologies}`. Mẫu 2 có fallback an toàn khi thiếu trường.
- **Bỏ HTML khỏi chat**: xóa tool `generate_cv_file`, `_cv_html_store`, marker `__html_id__`/`rich_html`, `templates/cv_template.html`. TOOLS còn **8**.
- **Bỏ trang CV Processor riêng**: xóa `CVProcessor.jsx`, NavLink Sidebar, route `cv-processor`, endpoint `/cv/extract` + `/cv/render`. Giữ `GET /cv/download-word/{id}` cho nút tải Word.
- **Skill `cv_processor.md`** viết lại: đọc CV → chọn mẫu (không rõ thì HỎI) → dịch (nếu cần) → `generate_cv_word_file` với `template_id`.
- `requirements.txt` thêm `python-docx>=1.1.0`, `openai>=1.0.0` (đang dùng mà thiếu).
- ⚠️ Map mức ngôn ngữ bỏ dấu tiếng Việt trước khi so (`_strip_accents`).

### 🗄️ Skill storage → MinIO (object storage) + TTL cache ✅
Chuyển nguồn lưu trữ skill từ file local sang **MinIO** (S3-compatible):
- **MinIO là nguồn DUY NHẤT** (không fallback local). Mỗi object `.md` trong bucket `skills` = 1 skill.
- **Cache + TTL refresh**: `SkillRegistry(ttl_seconds, fetch_fn)` giữ skills trong RAM, tự refresh từ MinIO mỗi `SKILLS_CACHE_TTL` (mặc định 300s) khi `list_all()`/`get()` được gọi. Dùng `time.monotonic()` + `threading.Lock` (double-check) chống refresh đồng thời. Sửa skill trên MinIO → hiệu lực sau TTL, KHÔNG restart.
- **Degrade an toàn**: MinIO down → giữ cache cũ, vẫn cập nhật mốc thời gian để back-off (không hammer). Startup lỗi MinIO → registry rỗng, server vẫn chạy, tự thử lại sau TTL.
- **Read-only**: quản lý skill = upload/sửa `.md` qua MinIO Console / `mc`. Không có API/UI ghi.
- **File mới**: `backend/storage/minio_skills.py` (client wrapper: `list_skill_objects`, `get_skill_text`), `backend/scripts/sync_skills_to_minio.py` (ensure bucket + upload seed `skills/library/*.md`).
- **Config** (`settings.py` đọc từ env): `MINIO_ENDPOINT` (host:port, không scheme), `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_SECURE`, `MINIO_BUCKET_SKILLS`, `SKILLS_CACHE_TTL`. Đã bỏ `SKILLS_DIR`.
- **Seed**: `skills/library/*.md` giữ trong git làm nguồn version-controlled + để upload; runtime KHÔNG đọc local nữa.
- `requirements.txt` thêm `minio>=7.2.0`.
- ⚠️ Cần MinIO chạy + chạy `sync_skills_to_minio.py` 1 lần để đẩy seed lên bucket.

### 🎯 Skill System redesign — "coding agent pattern" + Progressive Disclosure ✅
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

## Cấu trúc storage/ hiện tại (user management)
```
backend/storage/
├── user_store.py       ← users (Postgres only): CRUD + bcrypt verify — NGUỒN login
├── conversation_store.py ← metadata hội thoại (SQLite dev / Postgres prod)
├── blob_store.py       ← blob tạm PDF/Word (in-memory / Redis)
├── minio_skills.py     ← MinIO client wrapper
└── agent_store.py
```

## Login flow mới
```
LoginScreen → POST /api/auth/login {username, password}
  → user_store.verify_password() (bcrypt.checkpw)
  → 200: {user_id, username, name, role}  hoặc  401
  → App.jsx setCurrentUser({id, username, name, role, avatar})
  → nếu role=admin → fetchUsers(user_id) → /api/users
```

## Cấu trúc backend/agents/ hiện tại
```
backend/agents/
├── workflow.py         ← START → llm → tools → llm → END + SqliteSaver checkpointer + delete_thread()
├── workflow_state.py   ← 5 fields: user_id, user_name, query, agent_response, messages
├── llm_node.py         ← LLM bind 8 tools, _build_system_prompt() (catalog skill), logging
├── instances.py        ← skill_registry(ttl, fetch_fn=load_skills_from_minio) + warm()
└── __init__.py

backend/skills/
├── base.py             ← Skill model tối giản (name, description, body)
├── loader.py           ← load_skills_from_minio() + _parse_skill_md (PyYAML)
├── registry.py         ← TTL cache RAM (time.monotonic + Lock), refresh từ MinIO
└── library/            ← SEED (git) để upload lên MinIO — runtime KHÔNG đọc local
    └── cv_processor.md

backend/storage/minio_skills.py  ← MinIO client wrapper (list_skill_objects, get_skill_text)
backend/scripts/sync_skills_to_minio.py  ← ensure bucket + upload seed *.md lên MinIO
```
**Nguồn skill runtime = MinIO bucket `skills`** (không phải local).

## Cấu trúc backend/tools/ hiện tại
```
backend/tools/
├── company_tools.py    ← get_company_info, get_current_datetime, calculate,
│                          get_company_employee_list, get_demo_users_list
├── cv_tools.py         ← read_cv_file, generate_cv_word_file (template_id 1|2)
│                          _pdf_store, _cv_docx_store; _build_docx_template1/2
└── skill_tools.py      ← load_skill (progressive disclosure)
```

## Lưu ý kỹ thuật quan trọng
- `/api/chat` dùng `Form(...)` + `File(None)` — **không còn là JSON endpoint**. Frontend phải gửi FormData (không set Content-Type header). **Bắt buộc kèm `conversation_id`** (thread_id cho checkpointer) — quên là 422
- **Chat nhớ lịch sử** theo `conversation_id` (checkpointer). Lượt sau cùng conversation_id thấy lại history. "Chat mới" = conversation_id mới. Gọi qua `asyncio.to_thread(chatbot.invoke, ..., config)`
- **Storage backend đổi qua env**: `DB_BACKEND=sqlite|postgres` (checkpointer + conversations), `REDIS_URL` (rỗng=in-memory blob). Default = SQLite + in-memory. Driver postgres/redis lazy import (chỉ cần `requirements-prod.txt` khi production). employees vẫn SQLite
- `_pdf_store` bị xóa sau mỗi request. `_cv_docx_store` không bao giờ xóa — memory leak lâu dài
- `cv_agent.py` phải ở `backend/` root (tránh UnicodeEncodeError Windows cp1252). Tương tự: KHÔNG dùng emoji trong `print` (loader/registry dùng `[SKILL]` ASCII)
- `_build_system_prompt()` gọi mỗi request, inject **CATALOG** (name+description) của mọi skill — KHÔNG nhồi body. LLM gọi `load_skill(name)` để lấy chi tiết
- **Skill nguồn = MinIO** (bucket `skills`), cache RAM với TTL `SKILLS_CACHE_TTL`. Sửa skill trên MinIO → hiệu lực sau TTL, KHÔNG cần restart. MinIO down → giữ cache cũ / registry rỗng, server không sập. `MINIO_ENDPOINT` là host:port (không scheme)
- CV chỉ xuất Word qua chat (HTML đã bỏ): `generate_cv_word_file(cv_json, template_id="1"|"2")` lưu bytes vào `_cv_docx_store`, trả `__docx_id__: {id}` → routes.py tạo `word_download_url`. Không còn `__html_id__`/`rich_html`/trang CV Processor
- Login frontend gọi `GET /api/user?user_id=...` (không còn `/api/agents`)

## Cấu trúc Tool & Skill System hiện tại (coding agent pattern)
```
Thêm TOOL mới:
  1. Viết @tool function trong backend/tools/*.py
  2. Import vào backend/agents/llm_node.py → thêm vào TOOLS = [...]
  3. Restart server → GET /api/tools tự hiển thị

Thêm SKILL mới (nguồn = MinIO):
  1. Soạn file .md (frontmatter name + description "khi nào dùng" + body)
  2. Upload lên bucket MinIO `skills` qua MinIO Console / mc
     (hoặc sửa seed skills/library/ rồi chạy scripts/sync_skills_to_minio.py)
  3. Sau TTL (SKILLS_CACHE_TTL) → tự vào catalog + GET /api/skills, KHÔNG cần restart

Không còn (tool):  storage/tool_store.py, storage/tools.json, POST/PUT/DELETE /api/tools, ToolModal.jsx
Không còn (skill): skills/factory.py, skills/builtin/, storage/custom_skills/*.json,
                   POST /skills/draft|publish, POST /create_skill, DELETE /delete_skill, SkillDraftModal.jsx
```

## Nhiệm vụ tiếp theo
- **JWT Authentication**: Nâng cấp từ user_id plain param sang Bearer token JWT (đăng nhập trả token, middleware verify)
- **Cleanup in-memory store**: Thêm TTL/auto-cleanup cho `_cv_docx_store` để tránh memory leak
