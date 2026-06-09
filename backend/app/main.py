import logging
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)

from app.api.router import api_router
from app.repositories import user_repo

app = FastAPI(title="Evo Agents Multi-Agent RBAC Studio")

try:
    user_repo.seed_default_users()
except Exception as _e:
    logging.warning(f"[DB] Khong the seed users: {_e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# app/main.py nằm trong backend/app/ → dirname x3 = project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dist_dir = os.path.join(base_dir, "frontend", "dist")

if os.path.exists(dist_dir):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        react_index = os.path.join(dist_dir, "index.html")
        if os.path.exists(react_index):
            with open(react_index, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())

        static_dir = os.path.join(base_dir, "static")
        index_file = os.path.join(static_dir, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể đọc file index.html: {e}")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
