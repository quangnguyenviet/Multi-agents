# Active Context

## Cấu trúc file quan trọng
```
backend/
├── alembic/      env.py · versions/0001_initial.py
├── alembic.ini
├── scripts/      sync_skills_to_minio.py
└── app/
    ├── main.py
    ├── core/         config.py (settings: LLM, MinIO, DB, Redis)
    ├── db/           session.py (SQLAlchemy engine + SessionLocal)
    │                 models/ base.py · user.py · conversation.py
    ├── schemas/      auth.py · user.py · chat.py
    ├── repositories/ user_repo.py · conversation_repo.py · blob_store.py · minio_skills.py
    ├── services/     cv_service.py  ← CV extraction logic
    ├── skills/       base.py · loader.py · registry.py · library/(seed .md)
    ├── tools/        company_tools.py · cv_tools.py · skill_tools.py
    ├── agents/       workflow.py · workflow_state.py · llm_node.py · instances.py
    └── api/          router.py
                      v1/ auth.py · users.py · chat.py · conversations.py · skills.py · tools.py · cv.py
```

## ⚠️ Technical Gotchas
- `bcrypt>=4.0` không tương thích passlib — dùng `bcrypt.hashpw/checkpw` trực tiếp
- `POST /api/chat` bắt buộc kèm `conversation_id` (Form field) — thiếu → 422
- `_cv_docx_store` không có TTL → memory leak dài hạn (chưa fix)
- `MINIO_ENDPOINT` = `host:port` (không có scheme)
- SQLAlchemy + psycopg3: `DATABASE_URL` tự convert `postgresql://` → `postgresql+psycopg://` trong `app/db/session.py`
- Alembic quản lý schema. Lần đầu deploy: `alembic upgrade head`. Bảng đã có sẵn: `alembic stamp head`
- `app/main.py` nằm trong `backend/app/` → `base_dir = dirname(dirname(dirname(__file__)))` để trỏ đúng project root
- Chạy uvicorn từ `backend/`: `python -m uvicorn app.main:app --reload`

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
