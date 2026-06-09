# Hướng Dẫn Vận Hành Hệ Thống Multi-Agent Skill Studio

Dự án đã được tái cấu trúc tách biệt hoàn toàn giữa **Frontend (ReactJS SPA)** và **Backend (FastAPI + LangGraph + Skill Studio)** để tạo ra một cấu trúc thư mục rõ ràng, chuyên nghiệp và chuẩn công nghiệp.

---

## 1. Cấu Trúc Dự Án (Project Structure)

```text
demo_langGraph/
├── backend/                    # TOÀN BỘ PHẦN BACKEND (FastAPI + LangGraph)
│   ├── server.py               # API Server khởi chạy FastAPI
│   ├── config/                 # Cài đặt hệ thống & RBAC Permission Mapping
│   ├── data/                   # SQLite database (company.db) và data access layer
│   ├── api/                    # FastAPI routes và request schemas
│   ├── agents/                 # Module đa tác nhân LangGraph (các nodes & workflow)
│   ├── tools/                  # Các tool tích hợp hệ thống cho tác nhân
│   ├── skills/                 # Lõi động cơ của Skill System
│   └── storage/                # Lưu trữ custom skills động dạng JSON
│
├── frontend/                   # TOÀN BỘ PHẦN FRONTEND (ReactJS SPA + Vite)
│   ├── src/                    # Mã nguồn giao diện React
│   ├── public/                 # Các file asset tĩnh
│   ├── package.json            # Các thư viện frontend phụ thuộc
│   └── ...
│
└── README.md                   # Tài liệu hướng dẫn vận hành tổng quan này
```

---

## 2. Hướng Dẫn Khởi Chạy

### Khởi chạy Backend (Python FastAPI)

1. Mở terminal mới, di chuyển vào thư mục `backend/`:
   ```bash
   cd backend
   ```

2. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```

3. Cấu hình tệp tin `.env` trong thư mục `backend/`:
   Tạo tệp `.env` tại `backend/.env` với nội dung:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   LLM_BASE_URL=https://api.groq.com/openai/v1
   LLM_MODEL=llama-3.3-70b-versatile
   SKILLS_DIR=./storage/custom_skills
   ```
   *(Thay thế `gsk_your_groq_api_key_here` bằng khóa API Groq của bạn)*

4. Khởi chạy Server FastAPI:
   ```powershell
   # Dành cho Windows PowerShell
   $env:PYTHONIOENCODING="utf-8"; python server.py
   ```
   Server API sẽ chạy tại: **`http://127.0.0.1:8000`**

5. (Tùy chọn) Chạy thử bản CLI Tương Tác dòng lệnh:
   ```powershell
   $env:PYTHONIOENCODING="utf-8"; python main.py
   ```

---

### Khởi chạy Giao diện Frontend (ReactJS)

1. Mở terminal mới, di chuyển vào thư mục `frontend/`:
   ```bash
   cd frontend
   ```

2. Cài đặt các thư viện phụ thuộc của Node:
   ```bash
   npm install
   ```

3. Khởi chạy máy chủ phát triển (Dev server):
   ```bash
   npm run dev
   ```
   Trình duyệt của bạn sẽ tự động mở hoặc truy cập địa chỉ: **`http://localhost:5173`**

---

## 3. Tài Khoản Giả Lập Để Thử Nghiệm Quyền (RBAC)

Khi thử nghiệm trên Web hoặc CLI, hãy sử dụng các mã tài khoản sau:

| User ID | Tên nhân viên | Vai trò (Role) | Quyền hạn nổi bật |
| :--- | :--- | :--- | :--- |
| **`adm_001`** | Nguyen Admin | **Admin** | Đầy đủ quyền quản trị, tạo & xóa skill, xem toàn bộ lương và tài nguyên máy chủ Dell PowerEdge. |
| **`acc_001`** | Le Van C | **Accountant** | Có quyền xem bảng lương toàn công ty nhưng bị chặn xem tài nguyên máy chủ của Admin. |
| **`emp_001`** | Nguyen Van A | **Employee** | Nhân viên thường, chỉ được phép xem lương của chính mình, bị chặn xem lương người khác và tài nguyên máy chủ. |
| **`emp_002`** | Tran Thi B | **Employee** | Tương tự Nguyen Van A. |
