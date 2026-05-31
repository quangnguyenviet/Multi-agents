# backend/agents/instances.py
from skills.registry import SkillRegistry
from skills.factory import SkillFactory
from skills.loader import SkillLoader
from .base_agent import BaseAgent

# Import SQLite database and HTTP helper tools
from tools.company_tools import get_company_employee_list, get_demo_users_list

# === KHỞI TẠO SKILL SYSTEM ===
skill_registry = SkillRegistry()
skill_factory = SkillFactory()

# Tạo các agent với skill support
hr_agent_with_skills = BaseAgent(
    name="HR Policies Agent",
    agent_id="hr_policies",
    skill_registry=skill_registry
)
salary_agent_with_skills = BaseAgent(
    name="Salary Management Agent",
    agent_id="salary_management",
    skill_registry=skill_registry
)
system_admin_agent_with_skills = BaseAgent(
    name="System Admin Agent",
    agent_id="system_admin",
    skill_registry=skill_registry,
    tools=[get_company_employee_list]
)
user_management_agent_with_skills = BaseAgent(
    name="User Management Agent",
    agent_id="user_management",
    skill_registry=skill_registry,
    tools=[get_demo_users_list]
)

# Đăng ký & Kích hoạt toàn bộ skills từ ổ đĩa JSON
SkillLoader.load_custom_skills(skill_registry)

# Kích hoạt toàn bộ skills cho các Agent tương ứng dựa vào metadata
for skill in skill_registry.list_all():
    agent_id = skill.metadata.get("agent_id", "salary_management")
    if agent_id == "salary_management":
        salary_agent_with_skills.enable_skill(skill.id)
    elif agent_id == "hr_policies":
        hr_agent_with_skills.enable_skill(skill.id)
    elif agent_id == "system_admin":
        system_admin_agent_with_skills.enable_skill(skill.id)
    elif agent_id == "user_management":
        user_management_agent_with_skills.enable_skill(skill.id)
