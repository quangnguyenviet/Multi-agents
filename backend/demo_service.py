import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(
    title="Evo Demo Quick API Service",
    description="Backend service phục vụ thử nghiệm và demo nhanh các API cơ bản.",
    version="1.0.0"
)

# Kích hoạt CORS để gọi được từ bất kỳ frontend nào (như React cổng 3000 hoặc Live Server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Chào mừng
@app.get("/")
async def welcome():
    return {
        "status": "online",
        "message": "Chào mừng bạn đến với Evo Demo API Service!",
        "endpoints": {
            "GET /": "API Chào mừng này",
            "GET /api/test/users": "Lấy danh sách tài khoản demo nhanh",
            "POST /api/test/echo": "Gửi tin nhắn và nhận lại tin nhắn phản hồi",
            "GET /api/test/metrics": "Tra cứu hiệu năng hệ thống giả lập"
        }
    }

# 2. API Lấy danh sách Users thử nghiệm
@app.get("/api/test/users")
async def get_test_users():
    return [
        {"user_id": "demo_001", "name": "Nguyễn Văn Demo", "role": "tester", "email": "demo@evo.com"},
        {"user_id": "admin_test", "name": "Trần Quản Trị", "role": "admin", "email": "admin.test@evo.com"},
        {"user_id": "guest_001", "name": "Khách Vãng Lai", "role": "guest", "email": "guest@evo.com"}
    ]

# 3. API Echo (Gửi gì nhận nấy - Thích hợp test POST requests)
@app.post("/api/test/echo")
async def post_echo(payload: Dict[Any, Any] = Body(...)):
    return {
        "status": "success",
        "received_data": payload,
        "message": "Đã nhận thông tin thành công từ Client!"
    }

# 4. API Tra cứu Metrics hệ thống
@app.get("/api/test/metrics")
async def get_metrics():
    import random
    return {
        "cpu_usage": f"{random.randint(15, 45)}%",
        "ram_usage": f"{random.randint(25, 55)}%",
        "active_connections": random.randint(2, 10),
        "database_status": "connected",
        "server_time": "2026-05-29"
    }

if __name__ == "__main__":
    print("\n🚀 Khởi chạy Demo Service tại http://127.0.0.1:8080")
    print("Mở tài liệu API tự động Swagger tại: http://127.0.0.1:8080/docs\n")
    uvicorn.run(app, host="127.0.0.1", port=8080)
