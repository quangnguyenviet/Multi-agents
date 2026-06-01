# Technical Context

## Công nghệ sử dụng
- **Backend Core**: Python 3.10+, FastAPI, Uvicorn.
- **Orchestration**: LangGraph (StateGraph, conditional edges).
- **AI Integration**: LangChain (`langchain_openai`), ChatOpenAI qua **9Router** proxy (endpoint nội bộ `http://172.31.2.23:20128/v1`, model `evotek_flash`). 9Router cung cấp token saving, format translation, và multi-tier fallback giữa các provider.
- **Frontend Framework**: ReactJS (Vite, HSL CSS variables, Vanilla CSS for maximum flexibility).
- **Lưu trữ**: SQLite database (`data/company.db`) phục vụ dữ liệu nghiệp vụ, và File-system JSON (`storage/custom_skills/`) cho cấu hình kỹ năng.

## Môi trường & Khởi chạy

### 1. File `.env` cấu hình
Chứa các biến môi trường thiết yếu: `LLM_API_KEY`, `LLM_BASE_URL` (trỏ tới 9Router endpoint) và `LLM_MODEL`.

### 2. Chạy chế độ Production (Hợp nhất 1 server cổng 8000)
Vào thư mục `frontend` build code React, sau đó khởi chạy FastAPI:
```powershell
# B1: Build React tĩnh
cd frontend
npm run build
cd ..

# B2: Chạy server FastAPI
$env:PYTHONIOENCODING="utf-8"; python server.py
```
Giao diện React sẽ chạy ngay tại **`http://127.0.0.1:8000/`**.

### 3. Chạy chế độ Development (Lập trình nóng cổng 3000 + 8000)
Chạy đồng thời 2 terminal:
- **Terminal 1 (Backend)**: `$env:PYTHONIOENCODING="utf-8"; python server.py` (cổng 8000)
- **Terminal 2 (Frontend)**: `cd frontend; npm run dev` (cổng 3000, tự động proxy `/api` về 8000).
