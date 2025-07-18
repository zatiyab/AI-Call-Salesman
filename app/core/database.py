from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from app.core.config import settings
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 👈 This is crucial

# If there's no handler yet, add one
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


conn = None
cur = None
# database.py

DATABASE_URL = settings.DB_URL  # or use PostgreSQL, etc.
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def connect_to_db():
    global conn, cur
    try:    
        conn = psycopg2.connect(settings.DB_URL)
        cur = conn.cursor()
        logger.info("✅ Connected to PostgreSQL DB")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        raise
