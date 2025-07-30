from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CreateCampaign(BaseModel):
  campaign_name :str
  batch_id :str
  start_date :datetime
  end_date:datetime
  task :str
  agent_name :str
  created_at :Optional[datetime]
  campaign_thread_id :UUID
  agent_voice: str
  language:str
  agent_role :str
  voicemail_message:str
  call_recording:bool
  voicemail_setting:bool

class CreateContact(BaseModel):
  contact_name:str = Field(alias ="name")
  email:str
  phone_number:str
  company_name:Optional[str] = None
  tags:Optional[str] = None
  user_id:Optional[int] = None