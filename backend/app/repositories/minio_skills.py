from minio import Minio
from app.core.config import settings

_client: Minio | None = None


def _get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    return _client


def list_skill_objects() -> list[str]:
    """Liệt kê tên các object .md trong bucket skills."""
    client = _get_client()
    return [
        obj.object_name
        for obj in client.list_objects(settings.MINIO_BUCKET_SKILLS, recursive=True)
        if obj.object_name.endswith(".md")
    ]


def get_skill_text(object_name: str) -> str:
    """Tải nội dung text (utf-8) của một object skill."""
    client = _get_client()
    resp = client.get_object(settings.MINIO_BUCKET_SKILLS, object_name)
    try:
        return resp.read().decode("utf-8")
    finally:
        resp.close()
        resp.release_conn()
