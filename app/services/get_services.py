from app.crud.db_call import (get_all_calls,get_call_by_id)
from app.core.database import logger
from app.schemas.call_data_schemas import CallRead
from fastapi import HTTPException
import requests
from app.core.config import settings

# @router.get("/calls/{call_id}", response_model=CallRead)
async def get_call_from_id(call_id, db):
    call = get_call_by_id(db=db,call_id=call_id)
    data = CallRead.model_validate(call) 
    return {"call":data}



async def get_calls_from_db(limit, skip,db):
    """Get all calls from database"""
    try:
        calls = get_all_calls(db)
        calls_serialized = [CallRead.model_validate(call) for call in calls]
        
        return {"calls": calls_serialized, "count": len(calls_serialized)}
    
    
    except Exception as e:
        logger.error(f"❌ Error fetching calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")
    

def get_call_recording_by_id(call_id):
    bland_api_key = settings.BLAND_API_KEY
    headers = {
        "Authorization": f"Bearer {bland_api_key}",
        "Content-Type": "application/json"
        }

    response = requests.get(f"https://api.bland.ai/v1/recordings/{call_id}",headers=headers)
    return response["data"]



def get_call_recording_from_id(call_id):
    bland_api_key = settings.BLAND_API_KEY
    headers = {
        "authorization": f" {bland_api_key}"
        }
    response = requests.get(f"https://api.bland.ai/v1/recordings/{call_id}",headers=headers)
    print(response.data)
    return response.data