import io
from langchain_core.tools import tool
from app.repositories.blob_store import make_blob_store

_upload_store = make_blob_store("uploaded_files")


@tool
def read_file_content(file_id: str) -> str:
    """Đọc và trả về nội dung văn bản thô từ file đã được người dùng upload.
    Dùng tool này TRƯỚC để hiểu file là gì (CV, báo cáo, hợp đồng, v.v.),
    sau đó quyết định xử lý phù hợp. Hỗ trợ: PDF, TXT và các file văn bản."""
    file_bytes = _upload_store.get(file_id)
    if not file_bytes:
        return f"Lỗi: Không tìm thấy file với ID '{file_id}'."

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
        text = "\n".join(pages).strip()
        if text:
            return text[:8000]
    except Exception:
        pass

    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return file_bytes.decode(enc)[:8000]
        except Exception:
            continue

    return (
        "Không thể đọc nội dung file. "
        "File có thể là ảnh scan, file nhị phân, hoặc định dạng không được hỗ trợ (xlsx, docx, v.v.)."
    )
