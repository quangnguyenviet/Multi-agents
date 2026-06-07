# Skill model — file Markdown là source of truth (coding agent pattern)
from pydantic import BaseModel


class Skill(BaseModel):
    """Một skill = hướng dẫn dạng Markdown.

    - name/description: metadata được nạp sẵn vào catalog system prompt.
    - body: nội dung hướng dẫn đầy đủ, LLM nạp on-demand qua tool load_skill.
    """
    name: str
    description: str
    body: str
