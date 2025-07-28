from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SalesCallResult(BaseModel):
    summary: str
    customer_reaction: str
    next_call_datetime: Optional[datetime]
    timezone: str
    is_call_scheduled: bool
    need_email: bool
    cust_email: Optional[str]
