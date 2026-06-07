# system settings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Configuration
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    
    # Skill Configuration — file Markdown (.md) là source of truth
    SKILLS_DIR = "./skills/library"

    # Cache
    CACHE_TTL = 300  # 5 minutes

settings = Settings()