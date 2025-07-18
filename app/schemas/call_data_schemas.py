from pydantic import BaseModel, field_validator,  model_validator, ConfigDict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Request schemas
class TranscriptItem(BaseModel):
    speaker: str
    text: str

class CallPayload(BaseModel):
    call_id: str
    transcript: List[TranscriptItem]
    summary: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class SendCallRequest(BaseModel):
    phone_number: str
    pathway_id: str
    variables: Optional[Dict[str, Any]] = None
    task: Optional[str] = None
    record: Optional[bool] = None
    webhook: Optional[str] = None

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        # Basic phone number validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('pathway_id')
    def validate_pathway_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Pathway ID cannot be empty')
        return v.strip()

class BatchCallRequestItem(BaseModel):
    phone_number: str
    variables: Optional[Dict[str, Any]] = None

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

class BatchCallRequest(BaseModel):
    pathway_id: str
    calls: List[BatchCallRequestItem]
    task: Optional[str] = None
    record: Optional[bool] = None
    webhook: Optional[str] = None

    @field_validator('pathway_id')
    def validate_pathway_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Pathway ID cannot be empty')
        return v.strip()

    @field_validator('calls')
    def validate_calls(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one call is required')
        if len(v) > 100:  # Reasonable limit
            raise ValueError('Too many calls in batch (max 100)')
        return v




class CallBase(BaseModel):
    emotion: Optional[str]
    from_phone: Optional[str]
    to_phone: Optional[str]
    completed: Optional[bool]
    summary: Optional[str]
    call_transcript: Optional[str]

class CallCreate(CallBase):
    call_id: str
    embedding: Optional[list[float]]=None # Convert to numpy if needed
    model_config = ConfigDict(extra='allow')

    @model_validator(mode='after')
    def generate_embedding(self) -> 'CallCreate':
        if self.call_transcript and self.embedding is None:
            self.embedding = embedder.encode(self.call_transcript).tolist()
        return self

class CallRead(CallBase):
    call_id: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
