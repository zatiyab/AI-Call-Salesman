from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class CampaignRead(BaseModel):
    campaign_id: int
    campaign_name: str
    batch_id: str
    start_date: datetime
    end_date: datetime
    task: Optional[str] = None
    agent_name: Optional[str] = None
    created_at: Optional[datetime] = None
    campaign_thread_id: Optional[UUID] = None
    agent_voice: Optional[str] = None
    language: Optional[str] = None
    agent_role: Optional[str] = None
    voicemail_message: Optional[str] = None
    call_recording: Optional[bool] = None
    voicemail_setting: Optional[bool] = None
    user_id: Optional[int] = None
    campaign_phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CampaignScreenTable(BaseModel):
    campaign_id: int
    campaign_thread_id: str
    campaign_name: str
    agent_name: str
    campaign_phone_number: str
    channels_enabled:Optional[str] = "Call"
    campaign_status:Optional[str] = "Active Campaign"
    connected_contacts:int

    model_config = ConfigDict(from_attributes=True)

class ContactScreenTable(BaseModel):
    contact_name: str = Field(alias="name")
    phone_number: str 
    company_name: Optional[str] = "EICE"
    email_address:str = Field(alias="email")
    tags: Optional[str] = "Tech"

    model_config = ConfigDict(from_attributes=True,populate_by_name=True)