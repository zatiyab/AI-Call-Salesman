import os
from dotenv import load_dotenv
import cohere


load_dotenv()
llm = cohere.Client("BCxkxzdkBAiA9Ey0mS7csgHSRxaV2YHcYu6mtTrg") 
class Settings:
    BLAND_API_KEY: str = os.getenv("BLAND_API_KEY")
    DB_URL: str = os.getenv("DB_URL")
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

settings = Settings()