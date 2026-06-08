# Hướng dẫn nhanh — Lệnh chạy & debug

Tập hợp các lệnh mẫu để chạy dự án ở môi trường phát triển (backend + frontend) và cách debug bằng VS Code.

## Chạy backend (FastAPI)

- Cài dependencies (từ thư mục gốc):

```bash
cd backend
pip install -r requirements.txt
```

- Chạy server dev (uvicorn, hot-reload):

```bash
cd backend
python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

- Chạy CLI tương tác (tùy chọn):

```bash
cd backend
python main.py
```

## Chạy frontend (vite / React)

- Cài dependencies và chạy dev server:

```bash
cd frontend
npm install
npm run dev
```

- Build production (tạo `dist` để backend phục vụ):

```bash
cd frontend
npm run build
```

Sau khi build, thư mục `frontend/dist` sẽ được server FastAPI phục vụ tự động nếu tồn tại.

## MinIO — lưu trữ Skill (docker-compose)

Skill được lưu trên MinIO (bucket `skills`, mỗi object `.md` là 1 skill). File `docker-compose.yml` ở gốc repo dựng MinIO + tự tạo bucket + upload seed `backend/skills/library/*.md`.

- Khởi động MinIO (chạy nền, tự tạo bucket & upload seed):

```bash
docker compose up -d
```

- Mở MinIO Console: http://localhost:9001 (đăng nhập `minioadmin` / `minioadmin`). S3 API ở cổng `9000` — khớp `MINIO_ENDPOINT=localhost:9000` trong `backend/.env`.

- Xem log (kiểm tra bucket & seed đã upload):

```bash
docker compose logs minio-init
```

- Đẩy lại seed sau khi sửa file `.md` trong `backend/skills/library/` (cách 1 — chạy lại init):

```bash
docker compose up minio-init
```

- Hoặc đẩy seed bằng script Python (cách 2 — cần `pip install minio`):

```bash
cd backend
python scripts/sync_skills_to_minio.py
```

- Dừng MinIO (giữ dữ liệu trong volume `minio_data`):

```bash
docker compose down
```

- Xóa luôn dữ liệu (reset sạch bucket):

```bash
docker compose down -v
```

- Kiểm tra cấu hình compose hợp lệ (không cần daemon):

```bash
docker compose config -q
```

> Skill refresh theo TTL (`SKILLS_CACHE_TTL`, mặc định 300s): sửa/upload `.md` lên MinIO sẽ có hiệu lực sau TTL, **không cần restart backend**. Nếu MinIO chưa chạy, backend vẫn khởi động bình thường (registry rỗng, tự thử lại sau TTL).

## Storage backend (dev SQLite ↔ production Postgres/Redis)

Mặc định (không set env): **SQLite** cho lịch sử chat + hội thoại, **in-memory** cho file tạm (PDF/Word). Đủ cho dev/1 máy.

Production — bật Postgres + Redis:

```bash
# 1. Cài driver production
cd backend
pip install -r requirements.txt -r requirements-prod.txt

# 2. Chạy Postgres + Redis (profile prod, không tự chạy ở dev)
docker compose --profile prod up -d        # kèm cả MinIO

# 3. Đặt env trong backend/.env rồi chạy server
#    DB_BACKEND=postgres
#    DATABASE_URL=postgresql://evo:evo@localhost:5432/evo
#    REDIS_URL=redis://localhost:6379/0
```

- Backend tự `setup()` bảng checkpoint (Postgres) + bảng `conversations` lúc khởi động.
- File Word/PDF tạm lưu Redis kèm TTL (`BLOB_TTL`, mặc định 3600s) → share giữa worker, không rò rỉ bộ nhớ.
- Có thể chạy nhiều worker: `python -m uvicorn server:app --workers 2 --port 8000`.

## Debug backend trong VS Code

- Mở workspace trong VS Code, chọn Run & Debug, chọn cấu hình `Python: Uvicorn (server:app)` rồi nhấn F5.
- Cấu hình debug đã nằm sẵn tại `.vscode/launch.json` và chạy `uvicorn server:app --reload` từ thư mục `backend`.

## Chạy server thủ công (Windows PowerShell ví dụ)

```powershell
# tạo và kích hoạt virtualenv (tuỳ chọn)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# chạy uvicorn
cd backend
python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

## Ghi chú nhanh
- Nếu gặp lỗi import khi chạy debug trong VS Code, đảm bảo `PYTHONPATH` hoặc `cwd` trỏ tới `backend` (launch config đã thiết lập `cwd` là `${workspaceFolder}/backend`).
- Frontend dev server mặc định chạy trên một port khác (vite); để tích hợp, build frontend rồi cho backend phục vụ `dist`.

## Codegraph — Tra cứu code bằng Claude Code (MCP)

Codegraph là knowledge graph được index sẵn toàn bộ symbol trong workspace. Dùng trong hội thoại với Claude Code để tra cứu code nhanh, không cần grep thủ công.

### Các lệnh tra cứu (hỏi Claude bằng ngôn ngữ tự nhiên)

| Mục đích | Câu hỏi mẫu |
|----------|------------|
| Tìm symbol theo tên | "Tìm symbol `llm_node` ở đâu?" |
| Hiểu một tính năng / khu vực | "Giải thích cách hoạt động của chat flow?" |
| Trace luồng từ A đến B | "Trace từ `POST /api/chat` đến khi LLM trả response" |
| Xem source của một hàm | "Cho xem code của `_build_system_prompt`" |
| Xem nhiều symbol liên quan | "Cho xem các hàm trong `cv_tools.py`" |
| Xem file trong thư mục | "Liệt kê các file trong `backend/agents/`" |
| Kiểm tra index | "Index codegraph có sẵn chưa?" |

### Công cụ MCP tương ứng (Claude tự chọn)

```
codegraph_search   — tìm symbol theo tên
codegraph_context  — hiểu tổng quan một tính năng (dùng đầu tiên)
codegraph_trace    — trace call path từ điểm A → điểm B
codegraph_node     — xem source / signature của một symbol cụ thể
codegraph_explore  — xem nhiều symbol liên quan cùng lúc
codegraph_files    — liệt kê file trong thư mục
codegraph_status   — kiểm tra trạng thái và kích thước index
```

### Lưu ý
- Index lag khoảng ~1 giây sau khi lưu file — nếu vừa thêm code mới, đợi vài giây rồi hỏi.
- Dùng codegraph **trước khi** sửa code, không dùng trong lúc đang sửa.
- Ưu tiên codegraph hơn grep/read thủ công để tiết kiệm context window.
