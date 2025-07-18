from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT, BOOLEAN, TIMESTAMP as PGTIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class Call(Base):
    __tablename__ = "calls"
    __table_args__ = {"schema": "public"}

    call_thread_id = Column(UUID(as_uuid=True), nullable=True)
    call_id = Column(String(255), primary_key=True, nullable=False)
    is_followup = Column(Boolean, default=False, nullable=False)
    followup_to_call_id = Column(String(255), nullable=True)
    pathway_id = Column(String, nullable=True)
    batch_id = Column(String(255), nullable=True)
    emotion = Column(String(20), nullable=True)
    from_phone = Column(String(50), nullable=True)
    to_phone = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    status = Column(String(50), nullable=True)
    scheduled_call_datetime = Column(TIMESTAMP(timezone=True), nullable=True)
    timezone = Column(String, nullable=True)
    is_call_scheduled = Column(Boolean, nullable=False, server_default='false')
    summary = Column(Text, nullable=True)
    call_transcript = Column(Text, nullable=True)
    embedding = Column(Vector(1024), nullable=True)  
