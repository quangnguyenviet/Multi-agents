import io
import json
import unicodedata
import uuid

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from langchain_core.tools import tool

from cv_agent import extract_cv_data

_pdf_store: dict = {}       # {file_id: bytes}
_cv_docx_store: dict = {}   # {docx_id: bytes}


@tool
def read_cv_file(file_id: str) -> str:
    """Đọc và trích xuất thông tin từ file CV PDF đã được upload bởi người dùng.
    Trả về chuỗi JSON chứa: personal_info, summary, summary_points, experience,
    education, skills (gồm tech_stack phân nhóm), languages, certifications, projects.
    Dùng file_id được cung cấp trong context."""
    pdf_bytes = _pdf_store.get(file_id)
    if not pdf_bytes:
        return f"Lỗi: Không tìm thấy file với ID '{file_id}'."
    cv_data = extract_cv_data(pdf_bytes)
    return json.dumps(cv_data, ensure_ascii=False, indent=2)


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


def _strip_accents(s: str) -> str:
    """Bỏ dấu tiếng Việt + lowercase để so khớp bền vững (kha ↔ khá)."""
    nfd = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower()


def _date_range(a, b) -> str:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return ""
    return f"{a} - {b}".strip(" -")


# ════════════════════════════════════════════════════════════════════════════
# MẪU 1 — Bản Lý Lịch Chuyên Môn của nhân sự chủ chốt
# ════════════════════════════════════════════════════════════════════════════
def _build_docx_template1(cv_data: dict) -> Document:
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

    tbl = doc.add_table(rows=0, cols=3)
    tbl.style = "Table Grid"
    tbl.allow_autofit = False

    def _set_w(row):
        row.cells[0].width = W0
        row.cells[1].width = W1
        row.cells[2].width = W2

    def _full_row(text="", bold=False, centered=False, size=10, color=None):
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

    _full_row("BẢN LÝ LỊCH CHUYÊN MÔN CỦA NHÂN SỰ CHỦ CHỐT",
              bold=True, centered=True, size=13, color=_C_NAVY)

    pos = (experience[0].get("position") or "") if experience else ""
    _full_row(f"Vị trí: {pos}", bold=True, centered=True, size=11, color=_C_ACCENT)

    # ── Thông tin nhân sự (3 cột) ──
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

    # ── Trình độ chuyên môn ──
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

    if experience:
        _full_row("Kinh nghiệm chuyên môn",
                  bold=True, centered=False, size=11, color=_C_NAVY)

    for exp in experience:
        row = tbl.add_row()
        _set_w(row)
        dc = row.cells[0]
        ic = row.cells[1].merge(row.cells[2])

        dc.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        dp = dc.paragraphs[0]
        dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        dr = dp.add_run(f"{exp.get('start_date', '')} - {exp.get('end_date', '')}")
        dr.font.size = Pt(9.5); dr.font.color.rgb = _C_DARK

        p1 = ic.paragraphs[0]
        _lv(p1, "Tên Dự án: ", exp.get("company") or "")
        _para_bottom_border(p1)

        p2 = ic.add_paragraph()
        _lv(p2, "Vị trí công việc: ", exp.get("position") or "")
        _para_bottom_border(p2)

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

    if languages:
        _full_row("Ngoại ngữ", bold=True, size=11, color=_C_NAVY)
        for lang in languages:
            cell = _full_row()
            cell.paragraphs[0].add_run(
                f"{lang.get('language') or ''}: {lang.get('level') or ''}"
            ).font.size = Pt(10)

    if certs:
        _full_row("Chứng chỉ", bold=True, size=11, color=_C_NAVY)
        for cert in certs:
            parts = [x for x in [cert.get("name"), cert.get("issuer"), cert.get("date")] if x]
            cell = _full_row()
            cell.paragraphs[0].add_run("  |  ".join(parts)).font.size = Pt(10)

    return doc


# ════════════════════════════════════════════════════════════════════════════
# MẪU 2 — Hồ sơ năng lực chi tiết (theo dự án)
# ════════════════════════════════════════════════════════════════════════════
_W2_LABEL, _W2_VALUE = Cm(4.5), Cm(12.5)


def _t2_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True; r.font.size = Pt(12); r.font.color.rgb = _C_NAVY
    _para_bottom_border(p)
    return p


def _t2_kv(tbl, label: str, value: str):
    """Hàng 2 cột: nhãn (bold navy) | giá trị."""
    row = tbl.add_row()
    c0, c1 = row.cells
    c0.width = _W2_LABEL; c1.width = _W2_VALUE
    r = c0.paragraphs[0].add_run(label)
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = _C_NAVY
    vr = c1.paragraphs[0].add_run(value or "")
    vr.font.size = Pt(10); vr.font.color.rgb = _C_DARK
    return row


def _t2_kv_multiline(tbl, label: str, lines: list):
    """Hàng 2 cột với cột giá trị nhiều dòng."""
    row = tbl.add_row()
    c0, c1 = row.cells
    c0.width = _W2_LABEL; c1.width = _W2_VALUE
    r = c0.paragraphs[0].add_run(label)
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = _C_NAVY
    first = True
    for ln in lines:
        p = c1.paragraphs[0] if first else c1.add_paragraph()
        run = p.add_run(ln)
        run.font.size = Pt(9.5); run.font.color.rgb = _C_DARK
        first = False
    return row


def _t2_language_row(tbl, lang: dict):
    """4 cột: [ngôn ngữ] [Thành thạo] [Khá] [Trung bình] — đánh dấu (x) theo level."""
    name = lang.get("language") or ""
    level = _strip_accents(lang.get("level") or "")
    levels = ["Thành thạo", "Khá", "Trung bình"]

    idx = None
    if any(k in level for k in ["thanh thao", "fluent", "native", "ban ngu", "tot", "cao", "proficient", "advanced"]):
        idx = 0
    elif any(k in level for k in ["kha", "good", "upper", "intermediate"]):
        idx = 1
    elif any(k in level for k in ["trung binh", "basic", "average", "co ban", "beginner", "elementary"]):
        idx = 2

    row = tbl.add_row()
    cells = row.cells
    cells[0].paragraphs[0].add_run(name).font.size = Pt(10)
    for i, lv in enumerate(levels):
        txt = lv + (" (x)" if i == idx else "")
        cells[i + 1].paragraphs[0].add_run(txt).font.size = Pt(9.5)
    if idx is None and lang.get("level"):
        cells[1].paragraphs[0].add_run(f"  [{lang['level']}]").font.size = Pt(9)
    return row


def _build_docx_template2(cv_data: dict) -> Document:
    doc = Document()
    for sec in doc.sections:
        sec.top_margin    = Cm(1.5)
        sec.bottom_margin = Cm(1.5)
        sec.left_margin   = Cm(2.0)
        sec.right_margin  = Cm(2.0)

    pi             = cv_data.get("personal_info") or {}
    summary        = cv_data.get("summary") or ""
    summary_points = cv_data.get("summary_points") or []
    experience     = cv_data.get("experience") or []
    education      = cv_data.get("education") or []
    skills         = cv_data.get("skills") or {}
    tech_stack     = skills.get("tech_stack") or {}
    languages      = cv_data.get("languages") or []

    position = (experience[0].get("position") or "") if experience else ""

    # ── HỌ VÀ TÊN / VỊ TRÍ ──
    info = doc.add_table(rows=0, cols=2)
    info.style = "Table Grid"
    _t2_kv(info, "HỌ VÀ TÊN", pi.get("full_name") or "")
    _t2_kv(info, "VỊ TRÍ", position)
    doc.add_paragraph()

    # ── TỔNG QUAN ──
    points = summary_points or [s.strip() for s in summary.splitlines() if s.strip()]
    if points:
        _t2_heading(doc, "TỔNG QUAN")
        for pt in points:
            bp = doc.add_paragraph(f"•  {pt}")
            bp.paragraph_format.left_indent = Inches(0.1)
            for r in bp.runs:
                r.font.size = Pt(10); r.font.color.rgb = _C_DARK

    # ── HỌC VẤN ──
    if education:
        _t2_heading(doc, "HỌC VẤN")
        edu_tbl = doc.add_table(rows=0, cols=2)
        edu_tbl.style = "Table Grid"
        for edu in education:
            period = _date_range(edu.get("start_date"), edu.get("end_date"))
            lines = []
            major = " ".join(x for x in [edu.get("field"), edu.get("degree")] if x)
            if major:
                lines.append(major)
            if edu.get("institution"):
                lines.append(edu["institution"])
            _t2_kv_multiline(edu_tbl, period or "—", lines or [""])

    # ── NGÔN NGỮ ──
    if languages:
        _t2_heading(doc, "NGÔN NGỮ")
        lang_tbl = doc.add_table(rows=0, cols=4)
        lang_tbl.style = "Table Grid"
        for lang in languages:
            _t2_language_row(lang_tbl, lang)

    # ── CÔNG NGHỆ (phân nhóm) ──
    groups = [
        ("Hệ điều hành", tech_stack.get("operating_systems")),
        ("Công nghệ chính", tech_stack.get("core") or skills.get("technical")),
        ("Cơ sở dữ liệu", tech_stack.get("databases")),
        ("Công cụ", tech_stack.get("tools")),
        ("Phương pháp", tech_stack.get("methodologies")),
    ]
    if any(vals for _, vals in groups):
        _t2_heading(doc, "CÔNG NGHỆ")
        tech_tbl = doc.add_table(rows=0, cols=2)
        tech_tbl.style = "Table Grid"
        for label, vals in groups:
            if vals:
                _t2_kv(tech_tbl, label, ", ".join(vals))

    # ── KINH NGHIỆM LÀM VIỆC ──
    if experience:
        _t2_heading(doc, f"KINH NGHIỆM LÀM VIỆC ({len(experience)} dự án)")
        for i, exp in enumerate(experience, 1):
            etbl = doc.add_table(rows=0, cols=2)
            etbl.style = "Table Grid"
            _t2_kv(etbl, f"Dự án {i}", exp.get("company") or "")
            period = _date_range(exp.get("start_date"), exp.get("end_date"))
            if period:
                _t2_kv(etbl, "Thời gian", period)
            if exp.get("position"):
                _t2_kv(etbl, "Vị trí", exp["position"])
            if exp.get("team_size"):
                _t2_kv(etbl, "Quy mô dự án", str(exp["team_size"]))
            if exp.get("overview"):
                _t2_kv(etbl, "Mô tả", exp["overview"])
            tasks = exp.get("description") or []
            if tasks:
                _t2_kv_multiline(etbl, "Nhiệm vụ", [f"•  {t}" for t in tasks])
            if exp.get("technologies"):
                _t2_kv(etbl, "Công nghệ", exp["technologies"])
            doc.add_paragraph()

    return doc


@tool
def generate_cv_word_file(cv_json: str, template_id: str = "1") -> str:
    """Tạo file CV định dạng Word (.docx) từ dữ liệu CV dạng JSON, theo 1 trong 2 mẫu chuẩn.

    template_id:
      "1" = Bản Lý Lịch Chuyên Môn của nhân sự chủ chốt (bảng gọn, kinh nghiệm dạng thời gian | nội dung).
      "2" = Hồ sơ năng lực chi tiết (TỔNG QUAN, CÔNG NGHỆ phân nhóm, từng dự án ghi Quy mô / Mô tả / Nhiệm vụ / Công nghệ).

    Dùng khi người dùng yêu cầu xuất CV ra Word/.docx. Truyền template_id đúng theo mẫu người dùng chọn."""
    try:
        cv_data = json.loads(cv_json)
    except json.JSONDecodeError as e:
        return f"Lỗi JSON không hợp lệ: {e}"

    builder = _build_docx_template2 if str(template_id).strip() == "2" else _build_docx_template1
    doc = builder(cv_data)

    buf = io.BytesIO()
    doc.save(buf)
    docx_id = uuid.uuid4().hex[:8]
    _cv_docx_store[docx_id] = buf.getvalue()
    return f"File Word đã tạo thành công. __docx_id__: {docx_id}"
