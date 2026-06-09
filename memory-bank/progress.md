# Progress

## Các mốc đã hoàn thành
- [x] **Phase 1 (foundation)**: UI Dashboard, JSON skills, SQLite, ReactJS/Vite, 9Router LLM, Tool Registry read-only, Single LLM Node, ToolNode LangGraph.
- [x] **CV Processor qua chat**: PDF → pdfplumber → LLM JSON → Word (.docx), endpoint download.
- [x] **Skill → coding agent pattern + Progressive Disclosure**: Skill = file `.md`, CATALOG inject, `load_skill` on-demand tool, SkillManager read-only.
- [x] **Skill storage → MinIO + TTL cache**: MinIO bucket `skills`, TTL 300s, sửa skill không cần restart, `sync_skills_to_minio.py`.
- [x] **Storage backend cấu hình được**: `DB_BACKEND` (SQLite|Postgres), `REDIS_URL`, `blob_store.py`. Default = SQLite + in-memory.
- [x] **Chat nhớ lịch sử**: SqliteSaver checkpointer per `conversation_id`, `asyncio.to_thread` invoke.
- [x] **UI chọn cuộc hội thoại cũ**: `conversation_store`, sidebar list/load/delete, `delete_thread`.
- [x] **CV Processor — 2 mẫu Word + dịch**: `template_id="1"|"2"`, schema mở rộng (summary_points, team_size, tech_stack). Bỏ HTML + trang CV riêng.
- [x] **User Management — đăng nhập thật + CRUD**: `user_store` Postgres, bcrypt, `LoginScreen` form, `UserManager` CRUD admin.
- [x] **CV follow-up fix**: `_cv_json_store` cache JSON sau lần đọc đầu → follow-up message không cần upload lại.
- [x] **Refactor cấu trúc chuẩn FastAPI**: `config/` → `core/`, `api/models.py` → `api/schemas.py`, `cv_agent.py` → `agents/cv_agent.py`, tạo `services/`.
- [x] **Migrate sang SQLAlchemy + Alembic**: `models/` (User, Conversation), `core/database.py` (engine + SessionLocal), `alembic/` migrations, xóa raw SQL khỏi stores.
- [x] **Dọn dẹp SQLite + demo tools**: Xóa `data/database.py`, `company.db`, `checkpoints.db`, `conversations.db`, `data/` folder. Xóa `get_company_employee_list`, `get_demo_users_list`, `agent_store`, `agents.json`, `company_info.json`.
- [x] **Refactor sang chuẩn FastAPI đầy đủ**: Bọc toàn bộ vào `app/` package. Tách `routes.py` thành `api/v1/` (auth, users, chat, conversations, skills, tools, cv). `storage/` → `repositories/`. `core/settings.py` → `core/config.py`. `core/database.py` → `db/session.py`. `models/` → `db/models/`. `api/schemas.py` → `schemas/`. `services/cv_agent.py` → `services/cv_service.py`. Lệnh chạy: `python -m uvicorn app.main:app --reload`.
