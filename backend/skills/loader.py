# skill loader
import os
import json
from config.settings import settings
from skills.base import Skill
from skills.registry import SkillRegistry

class SkillLoader:
    """Tự động quét và nạp các Custom Skills đã được lưu dưới dạng file JSON"""
    
    @staticmethod
    def load_custom_skills(registry: SkillRegistry):
        custom_dir = settings.SKILLS_DIR
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir, exist_ok=True)
            return

        for filename in os.listdir(custom_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(custom_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Parse dữ liệu JSON thành đối tượng Pydantic Skill
                    skill = Skill(**data)
                    
                    registry.register(skill, [])
                    print(f"📦 Loaded custom skill: {skill.name} from {filename}")
                except Exception as e:
                    print(f"⚠️ Error loading custom skill {filename}: {e}")
