from fastapi import APIRouter, HTTPException, Query
from app.repositories import user_repo
from app.schemas.user import CreateUserRequest, UpdateUserRequest

router = APIRouter()


@router.get("/users")
async def list_users(user_id: str = Query(...)):
    """Danh sách tất cả users (admin only)."""
    me = user_repo.get_by_id(user_id)
    if not me:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    if me["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem được danh sách users")
    return user_repo.list_all()


@router.post("/users")
async def create_user_endpoint(req: CreateUserRequest, admin_id: str = Query(...)):
    """Tạo user mới (admin only)."""
    me = user_repo.get_by_id(admin_id)
    if not me or me["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới tạo được user")
    try:
        return user_repo.create_user(req.username, req.password, req.name, req.role)
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail=f"Username '{req.username}' đã tồn tại")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{uid}")
async def update_user_endpoint(uid: str, req: UpdateUserRequest, admin_id: str = Query(...)):
    """Cập nhật name/role/password của user (admin only)."""
    me = user_repo.get_by_id(admin_id)
    if not me or me["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới sửa được user")
    user_repo.update_user(uid, name=req.name, role=req.role, password=req.password)
    return {"success": True}


@router.delete("/users/{uid}")
async def delete_user_endpoint(uid: str, admin_id: str = Query(...)):
    """Xóa user (admin only, không tự xóa chính mình)."""
    me = user_repo.get_by_id(admin_id)
    if not me or me["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xóa được user")
    if uid == admin_id:
        raise HTTPException(status_code=400, detail="Không thể tự xóa chính mình")
    user_repo.delete_user(uid)
    return {"success": True}
