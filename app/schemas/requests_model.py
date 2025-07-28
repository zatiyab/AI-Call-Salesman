from pydantic import BaseModel, field_validator,  model_validator, ConfigDict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from datetime import datetime
from uuid import UUID


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
    ivr_mode: Optional[bool] = True
    voice_id: Optional[int] = 0
    reduce_latency: Optional[bool] = True
    request_data: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    to_phone: str
    pathway_id: Optional[str] = None  # e.g. "c9b37160-0209-455d-b60c-fea93fc33d7b"
    task: Optional[str] = None
    record: Optional[bool] = True
    webhook: Optional[str] = "https://e60889698168.ngrok-free.app/bland/postcall"

    @field_validator('to_phone')
    def validate_phone_number(cls, v):
        # Basic phone number validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

    
    @field_validator("metadata", mode="before")
    def clean_metadata(cls, v):
        if isinstance(v, dict):
            return v
        return None  # fallback: ignore anything that's not a dict
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

class PromptBusiness(BaseModel):
    business_desc:str
    business_name:str
    product_desc:str
    business_urls:Optional[str]
    business_files:Optional[str]


class TTSRequest(BaseModel):
    text:str
    ai_name:Optional[str] = "Maeve"