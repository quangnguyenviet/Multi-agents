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
