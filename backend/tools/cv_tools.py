import json
import os
import uuid

from jinja2 import Environment, FileSystemLoader
from langchain_core.tools import tool

from cv_agent import extract_cv_data

_pdf_store: dict = {}      # {file_id: bytes}
_cv_html_store: dict = {}  # {cv_id: html_string}

_jinja_env = Environment(
    loader=FileSystemLoader(
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    )
)


@tool
def read_cv_file(file_id: str) -> str:
    """Đọc và trích xuất thông tin từ file CV PDF đã được upload bởi người dùng.
    Trả về chuỗi JSON chứa: personal_info, summary, experience, education, skills,
    languages, certifications, projects. Dùng file_id được cung cấp trong context.
    languages, certifications, projects. Dùng file_id được cung cấp trong context."""
    pdf_bytes = _pdf_store.get(file_id)
    if not pdf_bytes:
        return f"Lỗi: Không tìm thấy file với ID '{file_id}'."
    cv_data = extract_cv_data(pdf_bytes)
    return json.dumps(cv_data, ensure_ascii=False, indent=2)


@tool
def generate_cv_file(cv_json: str) -> str:
    """Tạo file CV HTML đẹp từ dữ liệu CV dạng JSON (lấy từ read_cv_file hoặc từ thông tin người dùng cung cấp).
    Áp dụng template 2 cột chuyên nghiệp. Trả về cv_id để hệ thống lấy file HTML."""
    try:
        cv_data = json.loads(cv_json)
    except json.JSONDecodeError as e:
        return f"Lỗi JSON không hợp lệ: {e}"

    tmpl = _jinja_env.get_template("cv_template.html")
    cv_html = tmpl.render(cv=cv_data)

    cv_id = uuid.uuid4().hex[:8]
    _cv_html_store[cv_id] = cv_html
    return f"CV đã được tạo thành công. cv_id: {cv_id}"
