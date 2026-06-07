import io
import json
import os
import uuid

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from jinja2 import Environment, FileSystemLoader
from langchain_core.tools import tool

from cv_agent import extract_cv_data

_pdf_store: dict = {}       # {file_id: bytes}
_cv_html_store: dict = {}   # {cv_id: html_string}
_cv_docx_store: dict = {}   # {docx_id: bytes}

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
    return f"Tài liệu HTML đã được tạo thành công. __html_id__: {cv_id}"


# ── Color palette ─────────────────────────────────────────────────────────────
_C_NAVY   = RGBColor(0x0f, 0x34, 0x60)
_C_ACCENT = RGBColor(0x5c, 0x6b, 0xc0)
_C_DARK   = RGBColor(0x1a, 0x1a, 0x2e)


def _lv(para, label: str, value: str):
    """Label (bold navy) + value trong cùng paragraph."""
    lr = para.add_run(label)
    lr.bold = True; lr.font.size = Pt(10); lr.font.color.rgb = _C_NAVY
    vr = para.add_run(value or "")
    vr.font.size = Pt(10); vr.font.color.rgb = _C_DARK


def _para_bottom_border(para):
    """Thêm đường kẻ ngang mỏng phía dưới paragraph (dùng trong cell)."""
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "4")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "AAAAAA")
    pBdr.append(bot)
    pPr.append(pBdr)


@tool
def generate_cv_word_file(cv_json: str) -> str:
    """Tạo file CV định dạng Word (.docx) theo mẫu Bản Lý Lịch Chuyên Môn Việt Nam.
    Bố cục gồm: tiêu đề, vị trí hiện tại, thông tin cá nhân, trình độ học vấn,
    kinh nghiệm chuyên môn dạng bảng 2 cột (ngày | chi tiết dự án).
    Dùng khi người dùng yêu cầu xuất CV ra file Word hoặc .docx."""
    try:
        cv_data = json.loads(cv_json)
    except json.JSONDecodeError as e:
        return f"Lỗi JSON không hợp lệ: {e}"

    doc = Document()
    for sec in doc.sections:
        sec.top_margin    = Cm(1.5)
        sec.bottom_margin = Cm(1.5)
        sec.left_margin   = Cm(2.0)
        sec.right_margin  = Cm(2.0)

    pi         = cv_data.get("personal_info") or {}
    education  = cv_data.get("education") or []
    experience = cv_data.get("experience") or []
    skills     = cv_data.get("skills") or {}
    languages  = cv_data.get("languages") or []
    certs      = cv_data.get("certifications") or []

    # Chiều rộng 3 cột: 3.8 + 9.0 + 4.2 = 17.0 cm (A4 trừ margin 2cm mỗi bên)
    W0, W1, W2 = Cm(3.8), Cm(9.0), Cm(4.2)

    # ── Một bảng duy nhất bao toàn bộ nội dung ───────────────────────────────
    tbl = doc.add_table(rows=0, cols=3)
    tbl.style = "Table Grid"
    tbl.allow_autofit = False

    def _set_w(row):
        row.cells[0].width = W0
        row.cells[1].width = W1
        row.cells[2].width = W2

    def _full_row(text="", bold=False, centered=False, size=10, color=None):
        """Row merge toàn bộ 3 cột → 1 ô rộng."""
        row = tbl.add_row()
        _set_w(row)
        cell = row.cells[0].merge(row.cells[2])
        p = cell.paragraphs[0]
        if centered:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if text:
            r = p.add_run(text)
            r.bold = bold
            r.font.size = Pt(size)
            if color:
                r.font.color.rgb = color
        return cell

    # ── Tiêu đề ───────────────────────────────────────────────────────────────
    _full_row("BẢN LÝ LỊCH CHUYÊN MÔN CỦA NHÂN SỰ CHỦ CHỐT",
              bold=True, centered=True, size=13, color=_C_NAVY)

    # ── Vị trí ────────────────────────────────────────────────────────────────
    pos = (experience[0].get("position") or "") if experience else ""
    _full_row(f"Vị trí: {pos}", bold=True, centered=True, size=11, color=_C_ACCENT)

    # ── Thông tin nhân sự (3 cột) ─────────────────────────────────────────────
    row = tbl.add_row()
    _set_w(row)
    c0, c1, c2 = row.cells

    r0 = c0.paragraphs[0].add_run("Thông tin nhân sự")
    r0.bold = True; r0.font.size = Pt(10); r0.font.color.rgb = _C_NAVY
    c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    c1.paragraphs[0].add_run(f"Tên: {pi.get('full_name') or ''}").font.size = Pt(10)
    for key, label in [("email", "Email"), ("phone", "Điện thoại"), ("linkedin", "LinkedIn")]:
        if pi.get(key):
            c1.add_paragraph(f"{label}: {pi[key]}").runs[0].font.size = Pt(10)

    c2.paragraphs[0].add_run(f"Ngày sinh: {pi.get('date_of_birth') or ''}").font.size = Pt(10)
    for key, label in [("address", "Địa chỉ"), ("gender", "Giới tính")]:
        if pi.get(key):
            c2.add_paragraph(f"{label}: {pi[key]}").runs[0].font.size = Pt(10)

    # ── Trình độ chuyên môn ───────────────────────────────────────────────────
    if education:
        edu = education[0]
        cell = _full_row()
        p = cell.paragraphs[0]
        lr = p.add_run("Trình độ chuyên môn: ")
        lr.bold = True; lr.font.size = Pt(10); lr.font.color.rgb = _C_NAVY
        parts = [x for x in [edu.get("degree"), edu.get("field")] if x]
        edu_text = " ".join(parts)
        if edu.get("institution"):
            edu_text += (" - " if edu_text else "") + edu["institution"]
        if edu.get("gpa"):
            edu_text += f" (GPA: {edu['gpa']})"
        p.add_run(edu_text).font.size = Pt(10)

    # ── Heading "Kinh nghiệm chuyên môn" ─────────────────────────────────────
    if experience:
        _full_row("Kinh nghiệm chuyên môn",
                  bold=True, centered=False, size=11, color=_C_NAVY)

    # ── Các entry kinh nghiệm (cột trái: ngày | cột phải: nội dung) ──────────
    for exp in experience:
        row = tbl.add_row()
        _set_w(row)
        dc = row.cells[0]
        ic = row.cells[1].merge(row.cells[2])

        # Cột trái: khoảng thời gian, căn giữa dọc + ngang
        dc.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        dp = dc.paragraphs[0]
        dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        dr = dp.add_run(f"{exp.get('start_date', '')} - {exp.get('end_date', '')}")
        dr.font.size = Pt(9.5); dr.font.color.rgb = _C_DARK

        # Cột phải: Tên Dự án (+ border dưới)
        p1 = ic.paragraphs[0]
        _lv(p1, "Tên Dự án: ", exp.get("company") or "")
        _para_bottom_border(p1)

        # Vị trí công việc (+ border dưới)
        p2 = ic.add_paragraph()
        _lv(p2, "Vị trí công việc: ", exp.get("position") or "")
        _para_bottom_border(p2)

        # Công việc thực hiện
        p3 = ic.add_paragraph()
        tr = p3.add_run("Công việc thực hiện:")
        tr.bold = True; tr.font.size = Pt(10); tr.font.color.rgb = _C_NAVY

        for bullet in (exp.get("description") or []):
            bp = ic.add_paragraph(f"•  {bullet}")
            bp.paragraph_format.left_indent = Inches(0.15)
            for br in bp.runs:
                br.font.size = Pt(9.5); br.font.color.rgb = _C_DARK

        if exp.get("technologies"):
            _lv(ic.add_paragraph(), "Công nghệ sử dụng: ", exp["technologies"])

    # ── Kỹ năng ───────────────────────────────────────────────────────────────
    tech = skills.get("technical") or []
    soft = skills.get("soft") or []
    if tech or soft:
        _full_row("Kỹ năng", bold=True, size=11, color=_C_NAVY)
        if tech:
            cell = _full_row()
            _lv(cell.paragraphs[0], "Kỹ thuật: ", "  ·  ".join(tech))
        if soft:
            cell = _full_row()
            _lv(cell.paragraphs[0], "Kỹ năng mềm: ", "  ·  ".join(soft))

    # ── Ngoại ngữ ────────────────────────────────────────────────────────────
    if languages:
        _full_row("Ngoại ngữ", bold=True, size=11, color=_C_NAVY)
        for lang in languages:
            cell = _full_row()
            cell.paragraphs[0].add_run(
                f"{lang.get('language') or ''}: {lang.get('level') or ''}"
            ).font.size = Pt(10)

    # ── Chứng chỉ ────────────────────────────────────────────────────────────
    if certs:
        _full_row("Chứng chỉ", bold=True, size=11, color=_C_NAVY)
        for cert in certs:
            parts = [x for x in [cert.get("name"), cert.get("issuer"), cert.get("date")] if x]
            cell = _full_row()
            cell.paragraphs[0].add_run("  |  ".join(parts)).font.size = Pt(10)

    # ── Lưu ──────────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc.save(buf)
    docx_id = uuid.uuid4().hex[:8]
    _cv_docx_store[docx_id] = buf.getvalue()
    return f"File Word đã tạo thành công. __docx_id__: {docx_id}"
