# Evo Agent

Enterprise chatbot: FastAPI + LangGraph ReAct + PostgreSQL + MinIO + ReactJS/Vite.
LLM: 9Router internal proxy (`http://172.31.2.23:20128/v1`, model `evotek_flash`).

## Directory Structure

```
backend/app/
├── core/config.py          # Settings: LLM, MinIO, DB, Redis
├── db/session.py           # SQLAlchemy engine + SessionLocal
│   models/                 # user.py · conversation.py
├── schemas/                # auth · user · chat
├── repositories/           # user_repo · conversation_repo · blob_store · minio_skills · artifact_store
├── services/cv_service.py
├── skills/                 # base · loader · registry · library/(seed .md)
├── tools/                  # company_tools · file_tools · cv_tools · skill_tools
├── agents/                 # workflow · llm_node · instances · workflow_state
└── api/v1/                 # auth · users · chat · conversations · skills · tools · artifacts
```

## Dev Setup

```powershell
# Terminal 1 — Backend
$env:PYTHONIOENCODING="utf-8"; cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend; npm run dev   # port 3000, proxies /api → 8000
```

## Technical Gotchas

- `bcrypt>=4.0` is incompatible with passlib — use `bcrypt.hashpw/checkpw` directly
- `POST /api/chat` requires `conversation_id` as a Form field — missing → 422
- `MINIO_ENDPOINT` = `host:port` (no scheme)
- `DATABASE_URL`: `session.py` auto-converts `postgresql://` → `postgresql+psycopg://`
- Alembic: run `alembic upgrade head` before first deploy; if tables already exist → `alembic stamp head`
- Always run uvicorn from `backend/`, not the project root

## Architecture

- **LangGraph**: `START → llm →[tool_calls?]→ tools → llm → END`. Thread_id = conversation_id.
- **Skill System**: Skills are `.md` files in MinIO bucket `skills`. TTL cache 300s. LLM sees only the CATALOG (name + description), calls `load_skill(name)` on-demand for the full body.
- **Tool Registry**: `@tool` functions in `tools/`. Adding a tool requires code change + restart — no UI CRUD.
- **File Upload**: Uploaded bytes stored in Redis via `_upload_store` (prefix `uploaded_files`, TTL = `BLOB_TTL`). Cleaned up immediately after the chat turn. Accepts `.pdf`, `.txt`, `.docx`. File hint appended to query as `[Attached file: '<name>', file_id=<id>]` — LLM decides how to handle it via skill catalog.
- **Artifact System**: Tools return downloadable artifacts using the marker `__artifact__:<type>:<id>` in their result string. `chat.py` parses this and returns `artifacts: [{type, url}]` in the response. Served at `GET /api/artifacts/download/{type}/{id}`. Register new artifact types in `repositories/artifact_store.py` and `api/v1/artifacts.py`.
- **CV Processor**: PDF → JSON cache (`_cv_json_store`) → Word (.docx). 2 templates, bilingual (vi/en). Artifact stored under `_cv_docx_store` (prefix `cv_docx`).

## Adding a New Domain Tool

1. Create `tools/<domain>_tools.py` with `@tool` functions; artifacts use `__artifact__:<type>:<id>` marker
2. Add artifact store entry to `repositories/artifact_store.py` (`_stores["<type>"] = make_blob_store("<prefix>")`)
3. Add media type/extension to `api/v1/artifacts.py`
4. Register the tool in `TOOLS` list in `agents/llm_node.py`
5. Add label to `ARTIFACT_LABELS` map in `frontend/src/components/chat/MessageItem.jsx`
6. Write a skill `.md` file and upload it to MinIO

## Pending Tasks

- [ ] JWT Authentication (replace plain `user_id` param)
- [ ] TTL / auto-cleanup for `_cv_docx_store`
