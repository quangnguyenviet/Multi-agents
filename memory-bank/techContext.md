# Technical Context

## Công nghệ sử dụng
- **Backend Core**: Python 3.10+, FastAPI, Uvicorn.
- **Orchestration**: LangGraph (StateGraph, conditional edges).
- **AI Integration**: LangChain (`langchain_openai`), ChatOpenAI qua **9Router** proxy (endpoint nội bộ `http://172.31.2.23:20128/v1`, model `evotek_flash`).
- **Document Generation**: `python-docx` — tạo file Word (.docx) cho CV 2 mẫu (song ngữ vi/en).
- **Database**: PostgreSQL — SQLAlchemy 2.x ORM + Alembic migrations. Driver: psycopg3 (`psycopg[binary]`).
- **Object Storage**: MinIO — lưu skill `.md` files. Client: `minio` Python SDK.
- **Blob Cache**: Redis (TTL) hoặc in-memory dict — `app/repositories/blob_store.py`.
- **Frontend Framework**: ReactJS (Vite, HSL CSS variables, Vanilla CSS).

## Cấu trúc thư mục
```
backend/
├── alembic/     env.py · versions/
├── alembic.ini
├── scripts/     sync_skills_to_minio.py
└── app/
    ├── main.py
    ├── core/        config.py
    ├── db/          session.py · models/(base, user, conversation)
    ├── schemas/     auth.py · user.py · chat.py
    ├── repositories/ user_repo · conversation_repo · blob_store · minio_skills
    ├── services/    cv_service.py
    ├── skills/      base · loader · registry · library/
    ├── tools/       company_tools · cv_tools · skill_tools
    ├── agents/      workflow · llm_node · instances · workflow_state
    └── api/         router.py · v1/(auth, users, chat, conversations, skills, tools, cv)
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
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend; npm run dev    # port 3000, proxy /api → 8000
```

### Prod (1 server port 8000)
```powershell
cd frontend; npm run build
cd ..\backend
alembic upgrade head        # apply migrations
$env:PYTHONIOENCODING="utf-8"; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Alembic workflow
```powershell
cd backend
alembic upgrade head                               # apply tất cả pending migrations
alembic revision --autogenerate -m "add column X" # tạo migration mới từ model changes
alembic stamp head                                 # đánh dấu đã apply (nếu bảng đã có sẵn)
alembic downgrade -1                               # rollback 1 bước
```
