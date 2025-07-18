from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT, BOOLEAN, TIMESTAMP as PGTIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Call(Base):
    __tablename__ = "calls"
    __table_args__ = {"schema": "public"}

    call_id = Column(String(255), primary_key=True, nullable=False)
    emotion = Column(String(20), nullable=True)
    from_phone = Column(String(50), nullable=True)
    to_phone = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now())
    completed = Column(Boolean, nullable=True)
    summary = Column(Text, nullable=True)
    call_transcript = Column(Text, nullable=True)
    embedding = Column(Vector(1024), nullable=True)  # Adjust dim if needed
