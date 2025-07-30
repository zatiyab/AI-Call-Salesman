import os
from dotenv import load_dotenv
import cohere


load_dotenv()
llm = cohere.Client("") 
class Settings:
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    BLAND_API_KEY: str = os.getenv("BLAND_API_KEY")
    DB_URL: str = os.getenv("DB_URL")
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

settings = Settings()