import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import router from api/routes.py
from api.routes import router as api_router
from api.cv_routes import cv_router

app = FastAPI(title="Evo Agents Multi-Agent RBAC Studio")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include business routes under /api
app.include_router(api_router, prefix="/api")
app.include_router(cv_router, prefix="/api")

# Resolve absolute paths to frontend build assets
# server.py is in backend/, frontend is a sibling of backend/
base_dir = os.path.dirname(os.path.dirname(__file__))
dist_dir = os.path.join(base_dir, "frontend", "dist")

if os.path.exists(dist_dir):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve static index.html at root
@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        # 1. Try serving React compiled production app
        react_index = os.path.join(dist_dir, "index.html")
        if os.path.exists(react_index):
            with open(react_index, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        
        # 2. Fallback to HTML/JS prototype dashboard in static/
        static_dir = os.path.join(base_dir, "static")
        index_file = os.path.join(static_dir, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể đọc file index.html: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
