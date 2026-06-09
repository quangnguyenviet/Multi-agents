import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.tools.cv_tools import _cv_docx_store

router = APIRouter()


@router.get("/cv/download-word/{docx_id}")
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
