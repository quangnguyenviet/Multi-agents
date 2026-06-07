# Tool nạp skill on-demand (progressive disclosure)
from langchain_core.tools import tool


@tool
def load_skill(skill_name: str) -> str:
    """Nạp hướng dẫn chi tiết của một skill theo tên. Gọi tool này TRƯỚC khi
    thực hiện một tác vụ khớp với mô tả skill trong danh sách 'SKILLS KHẢ DỤNG',
    để lấy quy trình đầy đủ rồi làm theo."""
    from agents.instances import skill_registry

    skill = skill_registry.get(skill_name)
    if not skill:
        available = ", ".join(s.name for s in skill_registry.list_all()) or "(không có)"
        return f"Không tìm thấy skill '{skill_name}'. Các skill khả dụng: {available}."
    return skill.body
