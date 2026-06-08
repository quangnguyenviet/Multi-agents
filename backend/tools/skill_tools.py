# Tool nạp skill on-demand (progressive disclosure)
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def load_skill(skill_name: str) -> str:
    """Nạp hướng dẫn chi tiết của một skill theo tên. Gọi tool này TRƯỚC khi
    thực hiện một tác vụ khớp với mô tả skill trong danh sách 'SKILLS KHẢ DỤNG',
    để lấy quy trình đầy đủ rồi làm theo."""
    from agents.instances import skill_registry

    skill = skill_registry.get(skill_name)
    if not skill:
        available = ", ".join(s.name for s in skill_registry.list_all()) or "(không có)"
        logger.warning("[SKILL] Not found: '%s' | available: %s", skill_name, available)
        return f"Không tìm thấy skill '{skill_name}'. Các skill khả dụng: {available}."

    logger.info("[SKILL] Loaded: '%s'", skill_name)
    return skill.body
