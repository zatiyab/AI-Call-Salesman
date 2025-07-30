from pydantic import BaseModel
from typing import Any,Dict,Optional
from datetime import datetime


class EditCampaign(BaseModel):
    name:Optional[str]
    task:Optional[str]
    start_date:Optional[str]
    end_date:Optional[str]
    voicemail:Optional[str]