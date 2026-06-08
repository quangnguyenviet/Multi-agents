# Active Context

## Cấu trúc file quan trọng
```
backend/
├── agents/   workflow.py · workflow_state.py · llm_node.py · instances.py
├── skills/   base.py · loader.py · registry.py · library/(seed .md)
├── tools/    company_tools.py · cv_tools.py · skill_tools.py
├── storage/  user_store.py · conversation_store.py · blob_store.py · minio_skills.py
├── api/      routes.py · cv_routes.py
├── scripts/  sync_skills_to_minio.py
└── cv_agent.py  ← PHẢI ở backend/ root
```

## ⚠️ Technical Gotchas
- `bcrypt>=4.0` không tương thích passlib — dùng `bcrypt.hashpw/checkpw` trực tiếp
- `psycopg3 Connection` không có `.executemany()` trực tiếp — dùng `conn.cursor().executemany()`
- `user_store` Postgres only — không có SQLite fallback (khác conversation_store)
- `POST /api/chat` bắt buộc kèm `conversation_id` (Form field) — thiếu → 422
- `cv_agent.py` + loader/registry: dùng ASCII `[SKILL]` thay emoji để tránh UnicodeEncodeError cp1252 Windows
- `_cv_docx_store` không có TTL → memory leak dài hạn (chưa fix)
- `langgraph-checkpoint-sqlite>=2,<3` (bản 3.x lỗi serialize Message)
- `MINIO_ENDPOINT` = `host:port` (không có scheme)

## Nhiệm vụ tiếp theo
- JWT Authentication (thay user_id plain param)
- TTL / auto-cleanup cho `_cv_docx_store`
