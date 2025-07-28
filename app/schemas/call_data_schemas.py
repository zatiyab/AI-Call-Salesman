from pydantic import BaseModel, field_validator,  model_validator, ConfigDict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from datetime import datetime
from uuid import UUID

embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")


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
    call_thread_id: UUID
    followup_to_call_id: Optional[str] = None
    is_followup: bool = False
    pathway_id: Optional[str] = "https://e60889698168.ngrok-free.app/bland/postcall"
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
