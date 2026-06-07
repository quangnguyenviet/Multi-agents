# Skill loader — quét file Markdown (.md) có frontmatter từ SKILLS_DIR
import os
import yaml
from config.settings import settings
from skills.base import Skill
from skills.registry import SkillRegistry


def _parse_skill_md(text: str) -> Skill | None:
    """Tách frontmatter YAML (giữa hai dòng ---) và body markdown."""
    if not text.lstrip().startswith("---"):
        return None

    # Bỏ phần trống đầu file rồi tách theo dấu --- đầu tiên/thứ hai
    stripped = text.lstrip("﻿").lstrip()
    parts = stripped.split("---", 2)
    if len(parts) < 3:
        return None

    front = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()

    name = front.get("name")
    description = front.get("description")
    if not name or not description:
        return None

    return Skill(name=str(name), description=str(description), body=body)


class SkillLoader:
    """Tự động quét và nạp các skill dạng Markdown từ thư mục SKILLS_DIR."""

    @staticmethod
    def load_custom_skills(registry: SkillRegistry):
        skills_dir = settings.SKILLS_DIR
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir, exist_ok=True)
            return

        for filename in os.listdir(skills_dir):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(skills_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                skill = _parse_skill_md(text)
                if skill is None:
                    print(f"[SKILL] Skip {filename}: thieu frontmatter name/description")
                    continue
                registry.register(skill)
                print(f"[SKILL] Loaded: {skill.name} from {filename}")
            except Exception as e:
                print(f"[SKILL] Error loading {filename}: {e}")
