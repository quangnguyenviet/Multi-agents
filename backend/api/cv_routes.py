import io
import os
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Any, Dict

from cv_agent import extract_cv_data
from tools.cv_tools import _cv_docx_store

cv_router = APIRouter()

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


@cv_router.post("/cv/extract")
async def extract_cv(file: UploadFile = File(...)):
    """Upload a PDF CV, extract structured data via LLM."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF.")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File quá lớn (tối đa 10MB).")

    try:
        cv_data = extract_cv_data(contents)
        return {"success": True, "data": cv_data}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        traceback.print_exc()  # In full traceback ra backend terminal
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý CV: {type(e).__name__}: {str(e)}")


class RenderRequest(BaseModel):
    cv_data: Dict[str, Any]


@cv_router.post("/cv/render", response_class=HTMLResponse)
async def render_cv(req: RenderRequest):
    """Render extracted CV data into a printable HTML template."""
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
        )
        template = env.get_template("cv_template.html")
        html = template.render(cv=req.cv_data)
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi render template: {str(e)}")


@cv_router.get("/cv/download-word/{docx_id}")
async def download_cv_word(docx_id: str):
    """Tải về file CV Word (.docx) đã được tạo bởi generate_cv_word_file tool."""
    docx_bytes = _cv_docx_store.get(docx_id)
    if not docx_bytes:
        raise HTTPException(status_code=404, detail="File không tồn tại hoặc đã hết hạn.")
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=cv_{docx_id}.docx"},
    )
