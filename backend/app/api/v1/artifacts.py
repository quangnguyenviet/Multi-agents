import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.repositories.artifact_store import get_artifact

router = APIRouter()

_MEDIA_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

_EXTENSIONS = {
    "docx": "docx",
}


@router.get("/artifacts/download/{artifact_type}/{artifact_id}")
async def download_artifact(artifact_type: str, artifact_id: str):
    data = get_artifact(artifact_type, artifact_id)
    if not data:
        raise HTTPException(status_code=404, detail="Artifact không tồn tại hoặc đã hết hạn.")
    media_type = _MEDIA_TYPES.get(artifact_type, "application/octet-stream")
    ext = _EXTENSIONS.get(artifact_type, artifact_type)
    filename = f"{artifact_id}.{ext}"
    return StreamingResponse(
        io.BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
