# Admin builtin skills
from skills.base import Skill, SkillType, Permission

server_metrics_skill = Skill(
    id="server_metrics",
    name="server_metrics_query",
    version="1.0.0",
    description="Kiểm tra thông số tải CPU, RAM và dung lượng ổ cứng của hệ thống máy chủ chính",
    skill_type=SkillType.QUERY,
    parameters=[],
    system_prompt="""
Bạn là skill kiểm tra thông số và trạng thái sức khỏe của máy chủ.
Nhiệm vụ: Tổng hợp thông số tải CPU, dung lượng RAM đang dùng, dung lượng trống ổ cứng NVMe SSD RAID-10 từ context và trình bày dưới dạng bảng Markdown chuyên nghiệp để báo cáo cho SysAdmin.
""",
    permission=Permission(required_roles=["admin"]),
    examples=["Xem CPU và RAM hệ thống", "Dung lượng ổ cứng còn trống bao nhiêu", "Trạng thái máy chủ hiện tại"],
    metadata={"keywords": ["cpu", "ram", "máy chủ", "server", "ổ cứng", "ssd"]}
)

all_admin_skills = [server_metrics_skill]
