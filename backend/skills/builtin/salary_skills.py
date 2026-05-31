# Salary builtin skills
from skills.base import Skill, SkillType, Parameter, Permission

# Skill 1: Xem lương cá nhân
self_salary_skill = Skill(
    id="self_salary",
    name="self_salary_query",
    version="1.0.0",
    description="Cho phép nhân viên xem lương của chính mình",
    skill_type=SkillType.QUERY,
    parameters=[],
    system_prompt="""
Bạn là skill tra cứu lương cá nhân.
Nhiệm vụ: Trả lời câu hỏi về lương của chính người dùng đang hỏi.

Dữ liệu lương sẽ được cung cấp từ hệ thống. Hãy trình bày một cách thân thiện.
""",
    permission=Permission(required_roles=["employee", "accountant", "admin"]),
    examples=["Lương tháng này của tôi bao nhiêu?", "Em muốn xem bảng lương của em"],
    metadata={"keywords": ["lương", "lương của tôi", "bảng lương", "tiền lương", "salary"]}
)

# Skill 2: Tính thưởng
bonus_calculator_skill = Skill(
    id="bonus_calculator",
    name="bonus_calculator",
    version="1.0.0",
    description="Tính thưởng cho nhân viên dựa trên lương và KPI",
    skill_type=SkillType.TRANSFORM,
    parameters=[
        Parameter(name="base_salary", type="number", required=True, description="Lương cơ bản"),
        Parameter(name="kpi_score", type="number", required=True, description="Điểm KPI 0-100")
    ],
    system_prompt="""
Bạn là skill tính thưởng cho nhân viên.
Công thức tính thưởng:
- Thưởng cơ bản = lương_cơ_bản * 0.5 * (kpi_score / 100)
- Nếu kpi_score >= 90: thưởng thêm 1,000,000 VND
- Nếu kpi_score >= 120: thưởng thêm 2,000,000 VND
- Tổng thưởng = thưởng_cơ_bản + thưởng_thêm

Hãy trình bày kết quả chi tiết, dễ hiểu.
""",
    permission=Permission(required_roles=["accountant", "admin"]),
    examples=["Tính thưởng cho nhân viên A lương 10tr KPI 95", "Thưởng Tết của tôi là bao nhiêu?"],
    metadata={"keywords": ["thưởng", "bonus", "kpi", "tính thưởng"]}
)

# Skill 3: Báo cáo lương tổng hợp
salary_report_skill = Skill(
    id="salary_report",
    name="salary_report",
    version="1.0.0",
    description="Tạo báo cáo lương tổng hợp cho toàn công ty",
    skill_type=SkillType.QUERY,
    parameters=[],
    system_prompt="""
Bạn là skill tạo báo cáo lương.
Nhiệm vụ: Tổng hợp và trình bày bảng lương toàn công ty một cách trực quan.
Sử dụng markdown để tạo bảng, highlight các thông tin quan trọng.
""",
    permission=Permission(required_roles=["accountant", "admin"]),
    examples=["Cho tôi xem bảng lương tháng này", "Báo cáo lương tổng hợp"],
    metadata={"keywords": ["báo cáo lương", "tổng hợp lương", "bảng lương"]}
)

all_salary_skills = [self_salary_skill, bonus_calculator_skill, salary_report_skill]