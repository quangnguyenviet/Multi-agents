# Evo Agent

Enterprise chatbot: FastAPI + LangGraph ReAct + PostgreSQL + MinIO + ReactJS/Vite.

---

## Cấu Trúc Dự Án

```text
├── backend/
│   └── app/
│       ├── core/config.py          # Settings: LLM, MinIO, DB, Redis
│       ├── db/                     # SQLAlchemy engine + models
│       ├── schemas/                # auth · user · chat
│       ├── repositories/           # user_repo · conversation_repo · blob_store · minio_skills
│       ├── services/cv_service.py
│       ├── skills/                 # base · loader · registry · library (seed .md)
│       ├── tools/                  # company_tools · cv_tools · skill_tools
│       ├── agents/                 # workflow · llm_node · instances · workflow_state
│       └── api/v1/                 # auth · users · chat · conversations · skills · tools · cv
│
├── frontend/
│   └── src/
│
└── README.md
```

---

## Khởi Chạy

### Backend

```powershell
cd backend
pip install -r requirements.txt
$env:PYTHONIOENCODING="utf-8"; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev   # port 3000, proxies /api → 8000
```

---

## Cấu Hình Môi Trường

Tạo tệp `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/skillstudio
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
LLM_BASE_URL=http://172.31.2.23:20128/v1
LLM_API_KEY=any
LLM_MODEL=evotek_flash
```

Trước lần chạy đầu tiên, chạy migration:

```powershell
cd backend
alembic upgrade head
```
