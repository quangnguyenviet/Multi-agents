# Active Context

## Cấu trúc file quan trọng
```
backend/
├── core/         settings.py · database.py (SQLAlchemy engine + SessionLocal)
├── models/       base.py · user.py · conversation.py  ← SQLAlchemy ORM
├── alembic/      env.py · versions/0001_initial.py
├── alembic.ini
├── agents/       workflow.py · workflow_state.py · llm_node.py · instances.py
├── services/     cv_agent.py  ← CV extraction logic
├── skills/       base.py · loader.py · registry.py · library/(seed .md)
├── tools/        company_tools.py · cv_tools.py · skill_tools.py
├── storage/      user_store.py · conversation_store.py · blob_store.py · minio_skills.py · agent_store.py
├── api/          routes.py · cv_routes.py · schemas.py
├── data/         database.py (company demo data — SQLite, giữ nguyên)
├── scripts/      sync_skills_to_minio.py
└── server.py
```

## ⚠️ Technical Gotchas
- `bcrypt>=4.0` không tương thích passlib — dùng `bcrypt.hashpw/checkpw` trực tiếp
- `POST /api/chat` bắt buộc kèm `conversation_id` (Form field) — thiếu → 422
- `services/cv_agent.py` phải nằm ở `services/` (không phải `agents/`) — tránh circular import với `tools/cv_tools.py`
- `_cv_docx_store` không có TTL → memory leak dài hạn (chưa fix)
- `MINIO_ENDPOINT` = `host:port` (không có scheme)
- SQLAlchemy + psycopg3: `DATABASE_URL` tự convert `postgresql://` → `postgresql+psycopg://` trong `core/database.py`
- Alembic quản lý schema. Lần đầu deploy: `alembic upgrade head`. Bảng đã có sẵn: `alembic stamp head`
- `psycopg_pool` log `PythonFinalizationError` khi thoát `python -c` — không phải lỗi thật, bỏ qua

## CV Processor — fix follow-up message
- `_cv_json_store = make_blob_store("cv_json")` — cache JSON sau lần `read_cv_file` đầu tiên
- Follow-up message (không upload lại): LLM dùng `file_id` từ lịch sử, tool hit cache → không lỗi

## Frontend key facts
- `currentUser` persist trong `localStorage` (key `currentUser`) — reload không logout
- `/chat` render `ConversationsPage` (list) hoặc `ChatWorkspace` (room) theo state `chatView`
- `ConversationsPage` = input + danh sách lịch sử; sidebar không còn conversation list
- `handleSendMessage(text, file, overrideConvId)` — param 3 để tránh stale closure khi start new chat

## Nhiệm vụ tiếp theo
- JWT Authentication (thay user_id plain param)
- TTL / auto-cleanup cho `_cv_docx_store`
