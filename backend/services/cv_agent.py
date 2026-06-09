import io
import json
from openai import OpenAI
from core.settings import settings

CV_EXTRACTION_PROMPT = """Bạn là chuyên gia phân tích CV/Resume. Hãy đọc kỹ văn bản CV bên dưới và trích xuất thông tin thành JSON có cấu trúc.

QUAN TRỌNG:
- Chỉ trả về JSON thuần túy, không có markdown, không có giải thích.
- Nếu một trường không có trong CV, để giá trị null hoặc mảng rỗng [].
- Với experience: `description` là mảng bullet các NHIỆM VỤ/công việc đã làm; `overview` là một đoạn mô tả TỔNG QUAN dự án (nếu CV có); `team_size` là quy mô nhân sự dự án (nếu có).
- Với skills.tech_stack: phân loại công nghệ vào đúng nhóm (hệ điều hành, công nghệ chính, cơ sở dữ liệu, công cụ, phương pháp). Nếu không phân loại được, cứ để trong technical.
- summary_points: tách phần tóm tắt năng lực thành mảng bullet ngắn (nếu CV có phần tóm tắt/objective).

JSON Schema cần trả về:
{
  "personal_info": {
    "full_name": "string",
    "email": "string|null",
    "phone": "string|null",
    "address": "string|null",
    "linkedin": "string|null",
    "website": "string|null",
    "date_of_birth": "string|null",
    "gender": "string|null"
  },
  "summary": "string|null",
  "summary_points": ["string"],
  "experience": [
    {
      "company": "string",
      "position": "string",
      "start_date": "string",
      "end_date": "string",
      "team_size": "string|null",
      "overview": "string|null",
      "description": ["string"],
      "technologies": "string|null"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string|null",
      "field": "string|null",
      "start_date": "string|null",
      "end_date": "string|null",
      "gpa": "string|null"
    }
  ],
  "skills": {
    "technical": ["string"],
    "soft": ["string"],
    "tech_stack": {
      "operating_systems": ["string"],
      "core": ["string"],
      "databases": ["string"],
      "tools": ["string"],
      "methodologies": ["string"]
    }
  },
  "languages": [
    {"language": "string", "level": "string"}
  ],
  "certifications": [
    {"name": "string", "issuer": "string|null", "date": "string|null"}
  ],
  "projects": [
    {"name": "string", "description": "string", "technologies": "string|null"}
  ]
}

Văn bản CV:
{cv_text}"""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text).strip()
    except ImportError:
        raise RuntimeError("Thu vien pdfplumber chua duoc cai. Chay: pip install pdfplumber")


def extract_cv_data(pdf_bytes: bytes) -> dict:
    cv_text = extract_text_from_pdf(pdf_bytes)
    if not cv_text:
        raise ValueError("Khong the trich xuat van ban tu PDF. File co the la anh scan hoac bi bao ve.")

    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    prompt = CV_EXTRACTION_PROMPT.replace("{cv_text}", cv_text[:10000])
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    return json.loads(raw)
