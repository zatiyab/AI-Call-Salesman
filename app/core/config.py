import os
from dotenv import load_dotenv

load_dotenv()
 
class Settings:
    BLAND_API_KEY: str = os.getenv("BLAND_API_KEY")
    DB_URL: str = os.getenv("DB_URL")
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

settings = Settings()