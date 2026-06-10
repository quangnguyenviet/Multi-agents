from app.repositories.blob_store import make_blob_store

_stores = {
    "docx": make_blob_store("cv_docx"),
}


def get_artifact(artifact_type: str, artifact_id: str) -> bytes | None:
    store = _stores.get(artifact_type)
    return store.get(artifact_id) if store else None
