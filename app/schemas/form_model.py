from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EditCampaignForm(BaseModel):
    business_name:Optional[str] = None
    business_description: Optional[str] = None
    business_website: Optional[str] = None
    campaign_name:Optional[str]=None
    agent_name:Optional[str]=None #Agent name to give for prompt
    agent_voice:Optional[str] = None  #voice actual payload
    language:Optional[str] = None
    agent_role:Optional[str] = None
    task:Optional[str] = None
    campaign_start_data:Optional[datetime] = None
    campaign_end_date:Optional[datetime] = None
    voicemail_message:Optional[str] = None
    call_recording: Optional[bool] = None # record = True for payload
    voicemail_setting:Optional[bool] = None #voicemail on or off