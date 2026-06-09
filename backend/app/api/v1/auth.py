from fastapi import APIRouter, HTTPException, Query
from app.repositories import user_repo
from app.schemas.auth import LoginRequest

router = APIRouter()


@router.post("/auth/login")
async def login(req: LoginRequest):
    """Đăng nhập bằng username + password. Trả user info nếu đúng."""
    user = user_repo.verify_password(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    return {"user_id": user["id"], "username": user["username"], "name": user["name"], "role": user["role"]}


@router.get("/user")
async def get_user(user_id: str = Query(...)):
    """Lấy thông tin user theo id."""
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"user_id": user["id"], "name": user["name"], "role": user["role"]}
