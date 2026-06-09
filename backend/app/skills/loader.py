import yaml
from app.skills.base import Skill
from app.repositories.minio_skills import list_skill_objects, get_skill_text


def _parse_skill_md(text: str) -> Skill | None:
    """Tách frontmatter YAML (giữa hai dòng ---) và body markdown."""
    if not text.lstrip().startswith("---"):
        return None

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


def load_skills_from_minio() -> list[Skill]:
    """Tải toàn bộ skill (.md) từ bucket MinIO, parse thành list[Skill]."""
    skills: list[Skill] = []
    for obj in list_skill_objects():
        try:
            skill = _parse_skill_md(get_skill_text(obj))
            if skill is None:
                print(f"[SKILL] Skip {obj}: thieu frontmatter name/description")
                continue
            skills.append(skill)
            print(f"[SKILL] Loaded: {skill.name} from {obj}")
        except Exception as e:
            print(f"[SKILL] Error loading {obj}: {e}")
    return skills
