from app.crud.db_call import (
    get_all_calls,
    get_call_by_id
    )
from app.crud.get_data import (
    campaigns_by_userID,
    get_number_of_calls_from_campaignID,
    get_contacts_from_campaign_id
)
from app.schemas.read_table_models import (
    CampaignRead,
    CampaignScreenTable,
    ContactScreenTable
)
from app.core.database import logger
from app.schemas.call_data_schemas import CallRead
from fastapi import HTTPException
import requests
from app.core.config import settings
from fastapi import HTTPException

async def get_call_from_id(call_id, db):
    call = get_call_by_id(db=db, call_id=call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    data = CallRead.model_validate(call)
    return {"call": data}


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


async def campaigns_of_userID(user_id,db):
    campaigns = campaigns_by_userID(user_id,db)
    campaigns = [(CampaignRead.model_validate(campaign)).model_dump() for campaign in campaigns]
    print(campaigns)
    for campaign in campaigns:
        campaign["campaign_thread_id"] = str(campaign["campaign_thread_id"])
        campaign['connected_contacts'] = (get_number_of_calls_from_campaignID(campaign['campaign_thread_id'],db=db))[0]
    campaigns =[(CampaignScreenTable.model_validate(campaign)).model_dump() for campaign in campaigns]
    return {'campaigns':campaigns}



async def contacts_of_campaigns(campaign_thread_id,db):
    contacts =  get_contacts_from_campaign_id(campaign_thread_id,db)
    print(contacts)
    for i in contacts:
        print(i.name)
    contacts = [(ContactScreenTable.model_validate(contact)).model_dump() for contact in contacts]
    print(contacts)
    return {'contacts':contacts}




