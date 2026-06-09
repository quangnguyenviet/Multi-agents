import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Configuration
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

    # Skill Configuration — nguồn lưu trữ là MinIO (object storage), mỗi object .md là 1 skill
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")  # host:port, KHÔNG kèm scheme
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_SKILLS = os.getenv("MINIO_BUCKET_SKILLS", "skills")
    SKILLS_CACHE_TTL = int(os.getenv("SKILLS_CACHE_TTL", "300"))

    DATABASE_URL = os.getenv("DATABASE_URL", "")
    REDIS_URL = os.getenv("REDIS_URL", "")
    BLOB_TTL = int(os.getenv("BLOB_TTL", "3600"))

settings = Settings()
