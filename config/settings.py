# system settings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = "llama-3.3-70b-versatile"
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    
    # Skill Configuration
    SKILLS_DIR = "./storage/custom_skills"
    BUILTIN_SKILLS_DIR = "./skills/builtin"
    ALLOW_USER_CREATE_SKILLS = True
    MAX_SKILLS_PER_USER = 20
    
    # Security
    ENABLE_SKILL_AUDIT = True
    SKILL_EXECUTION_LOG = "./logs/skill_executions.log"
    
    # Cache
    CACHE_TTL = 300  # 5 minutes

settings = Settings()