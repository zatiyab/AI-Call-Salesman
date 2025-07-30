from pydantic import BaseModel, field_validator,  model_validator, ConfigDict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from datetime import datetime,timezone,timedelta
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
    pathway_id: Optional[str] =None
    task: Optional[str] = None
    record: Optional[bool] = False
    webhook: Optional[str] = "https://bb109896dc71.ngrok-free.app/bland/postcall"
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
    webhook: Optional[str] = "https://bb109896dc71.ngrok-free.app/bland/postcall"

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


class BatchCallItemRequest(BaseModel):
    ivr_mode: Optional[bool] = True
    voice_id: Optional[int] = 0
    reduce_latency: Optional[bool] = True
    request_data: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    to_phone: str


class GlobalBatch(BaseModel):
    start_time:Optional[datetime] = datetime.now(timezone.utc) +timedelta(minutes=30),
    task:Optional[str]="You are a professional, warm, and articulate AI sales assistant named John, calling on behalf of {{business_name}}.\n\nContext:\n{{business_description}}\n\nTask Objective:\n{{task_description}}\n\nCustomer Info:\nName: {{customer_name}}\nEmail: {{cust_email}}\n\nGoal:\nConduct a friendly, human-like phone conversation with {{customer_name}}. Present the business offering in a helpful way, and if interested, offer to send information to {{cust_email}}. If the customer is busy or unavailable, politely ask for a better time to call back and confirm availability.\n\nGuidelines:\n- Speak slowly, clearly, and warmly.\n- Begin by introducing yourself as John, the AI assistant calling on behalf of {{business_name}}.\n- Ask if you’re speaking with {{customer_name}}.\n- Be brief but engaging when explaining the service — no long monologues.\n- Pause after each key sentence to let the customer respond.\n- Always check if they’re available to talk before continuing.\n- Ask if they’d like to receive more information via email.\n- If they’re not interested or unavailable, be respectful and offer to follow up later.\n- End the conversation politely and thank them for their time.\n\nExample Flow:\nYou: Hi, is this {{customer_name}}?\n\nCustomer: Yes, speaking.\n\nYou: Great! I'm John, an AI assistant calling on behalf of {{business_name}}. We help people like you by [brief value proposition from {{business_description}}]. Is this a good time to talk?\n\n[Wait for response.]\n\nYou: No worries if you're busy. Would you prefer I call at another time? Or I can email you more information at {{cust_email}} if that’s easier.\n\n[Adjust based on customer response.]\n\nYou: Thank you, {{customer_name}}! I appreciate your time. Have a wonderful day."
    record:Optional[bool] = True
    webhook:Optional[str] ="https://bb109896dc71.ngrok-free.app/bland/postcall" 

class BatchCallRequest(BaseModel):
    call_objects: List[BatchCallItemRequest]
    global_keyword:GlobalBatch=GlobalBatch()


class PromptBusiness(BaseModel):
    business_desc:str
    business_name:str
    product_desc:str
    business_urls:Optional[str]
    business_files:Optional[str]


class TTSRequest(BaseModel):
    text:str
    ai_name:Optional[str] = "Maeve"