# Technical Context

## Công nghệ sử dụng
- **Backend Core**: Python 3.10+, FastAPI, Uvicorn.
- **Orchestration**: LangGraph (StateGraph, conditional edges).
- **AI Integration**: LangChain (`langchain_openai`), ChatOpenAI qua **9Router** proxy (endpoint nội bộ `http://172.31.2.23:20128/v1`, model `evotek_flash`).
- **Document Generation**: `python-docx` — tạo file Word (.docx) cho CV 2 mẫu (song ngữ vi/en).
- **Database**: PostgreSQL — SQLAlchemy 2.x ORM + Alembic migrations. Driver: psycopg3 (`psycopg[binary]`).
- **Object Storage**: MinIO — lưu skill `.md` files. Client: `minio` Python SDK.
- **Blob Cache**: Redis (TTL) hoặc in-memory dict — `blob_store.py`.
- **Frontend Framework**: ReactJS (Vite, HSL CSS variables, Vanilla CSS).

## Cấu trúc thư mục
```
backend/
├── core/        settings.py · database.py
├── models/      base.py · user.py · conversation.py
├── alembic/     env.py · versions/
├── api/         routes.py · cv_routes.py · schemas.py
├── agents/      workflow.py · llm_node.py · ...
├── services/    cv_agent.py
├── tools/       company_tools.py · cv_tools.py · skill_tools.py
├── skills/      base.py · loader.py · registry.py · library/
├── storage/     user_store.py · conversation_store.py · blob_store.py · ...
├── data/        database.py (company demo data — SQLite, chỉ dùng test)
├── scripts/     sync_skills_to_minio.py
└── server.py
```

## Môi trường & Khởi chạy

### File `.env` cấu hình
```
LLM_API_KEY=...
LLM_BASE_URL=http://172.31.2.23:20128/v1
LLM_MODEL=evotek_flash
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=                 # để trống = in-memory blob store
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Dev (hot-reload, 2 terminal)
```powershell
# Terminal 1 — Backend
$env:PYTHONIOENCODING="utf-8"
cd backend
python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend; npm run dev    # port 3000, proxy /api → 8000
```

### Prod (1 server port 8000)
```powershell
cd frontend; npm run build
cd ..\backend
alembic upgrade head        # apply migrations (lần đầu hoặc khi có migration mới)
$env:PYTHONIOENCODING="utf-8"; python server.py
```

### Alembic workflow
```powershell
cd backend
alembic upgrade head                               # apply tất cả pending migrations
alembic revision --autogenerate -m "add column X" # tạo migration mới từ model changes
alembic stamp head                                 # đánh dấu đã apply (nếu bảng đã có sẵn)
alembic downgrade -1                               # rollback 1 bước
```
