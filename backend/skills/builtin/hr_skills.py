# HR builtin skills
from skills.base import Skill, SkillType, Permission

hr_policy_query_skill = Skill(
    id="hr_policy_query",
    name="hr_policy_query",
    version="1.0.0",
    description="Tra cứu các quy định, nội quy và chính sách nhân sự của công ty",
    skill_type=SkillType.QUERY,
    parameters=[],
    system_prompt="""
Bạn là skill tra cứu chính sách nhân sự (HR).
Nhiệm vụ: Trả lời các thắc mắc của nhân viên về quy định thời gian làm việc, số ngày nghỉ phép năm, bảo hiểm xã hội, lễ tết và trang phục dựa theo tài liệu HR được cung cấp trong context.
Hãy trả lời thân thiện, lịch sự và chuyên nghiệp.
""",
    permission=Permission(required_roles=["employee", "accountant", "admin"]),
    examples=["Quy định nghỉ phép năm thế nào?", "Thời gian làm việc của công ty", "Đóng bảo hiểm thế nào"],
    metadata={"keywords": ["nghỉ phép", "trang phục", "bảo hiểm", "giờ làm", "phép năm"]}
)

all_hr_skills = [hr_policy_query_skill]
