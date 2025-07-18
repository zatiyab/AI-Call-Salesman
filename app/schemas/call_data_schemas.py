from pydantic import BaseModel, field_validator,  model_validator, ConfigDict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from datetime import datetime
from uuid import UUID

embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Request schemas
class TranscriptItem(BaseModel):
    speaker: str
    text: str

class CallPayload(BaseModel):
    call_id: str
    transcript: List[TranscriptItem]
    summary: Optional[str] = None



class SendScheduledCallRequest(BaseModel):
    call_id: Optional[str] = None
    scheduled_call_datetime: Optional[datetime]=None
    to_phone: str
    pathway_id: str = "https://e60889698168.ngrok-free.app/bland/postcall"

    task: Optional[str] = None
    record: Optional[bool] = False
    webhook: Optional[str] = "https://e60889698168.ngrok-free.app/bland/postcall"
    call_thread_id: Optional[str] = None
    is_followup: Optional[bool] = False
    followup_to_call_id: Optional[str] = None
    # @field_validator("metadata", mode="before")
    # def clean_metadata(cls, v):
    #     if isinstance(v, dict):
    #         return v
    #     return None  # fallback: ignore anything that's not a dict

    @field_validator('to_phone')
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
    model_config = ConfigDict(from_attributes=True) 


class SendCallRequest(BaseModel):
    to_phone: str
    pathway_id: str = "c9b37160-0209-455d-b60c-fea93fc33d7b"
    # metadata: Optional[Dict[str, Any]] = None
    task: Optional[str] = None
    record: Optional[bool] = False
    webhook: Optional[str] = "https://e60889698168.ngrok-free.app/bland/postcall"



    @field_validator('to_phone')
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
    model_config = ConfigDict(from_attributes=True) 

class BatchCallRequestItem(BaseModel):
    phone_number: str
    # metadata: Optional[Dict[str, Any]] = None

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
    batch_id: Optional[str] = None
    scheduled_call_datetime: Optional[str]=None
    timezone: Optional[str]=None
    is_call_scheduled: Optional[bool]=None
    emotion: Optional[str] =None
    from_phone: Optional[str]=None
    to_phone: Optional[str]=None
    status: Optional[str]=None
    summary: Optional[str]=None
    call_transcript: Optional[str]=None
    model_config = ConfigDict(from_attributes=True) 

class CallCreate(CallBase):
    # call_thread_id: UUID
    followup_to_call_id: Optional[str] = "None"
    is_followup: bool = False
    pathway_id: str = "https://e60889698168.ngrok-free.app/bland/postcall"
    batch_id: Optional[str] = "None"
    created_at:Optional[str]
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
    scheduled_call_datetime: Optional[datetime]

    model_config = ConfigDict(from_attributes=True) 
