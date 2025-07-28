from app.core.database import logger
from fastapi import Request, HTTPException
import requests
import logging
from app.core.config import settings
from app.core.database import conn, cur

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.call_data_schemas import (
    CallCreate,
    CallRead, 
    CallBase
    )
from app.schemas.requests_model import (
    SendCallRequest, 
    SendScheduledCallRequest
)
from app.crud.db_call import (
    create_call, 
    get_all_calls,
    get_call_by_id,
    get_scheduled_call,
    get_call_thread_id
    )
from app.services.utils import llm_generate_data,format_datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import requests
from datetime import datetime
import pytz
# from app.services.scheduler import (
#     schedule_call,
#     scheduler    
#     )


# async def call_scheduler(db):
#     calls = get_scheduled_call(db)
#     calls_serialized = [SendScheduledCallRequest.model_validate(call) for call in calls]
#     try:
#         for call in calls_serialized:
#             schedule_call(call.model_dump())
#         return {"message":"Calls scheduled"}
    
#     except Exception as e:
#         logger.error(f"Error in call scheduler: {e}")


async def create_single_call(request):
    """Send a single AI phone call"""
   
    try:
        url = "https://api.bland.ai/v1/calls"
        bland_api_key = settings.BLAND_API_KEY

        if not bland_api_key:
            raise HTTPException(status_code=500, detail="BLAND_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {bland_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "phone_number": request.to_phone,
            "ivr_mode":request.ivr_mode,
            "voice_id":request.voice_id,
            'reduce_latency':request.reduce_latency,
            "request_data":request.request_data,
            "record":request.record,
            "webhook":request.webhook,
            "metadata":request.request_data
        }

        # Optional fields
        if request.pathway_id != None:
            payload['pathway_id'] = request.pathway_id
        if request.start_time:
            payload["start_time"] = request.start_time
        if request.request_data :
            payload["request_data"] = request.request_data
        if request.metadata:
            payload["metadata"] = request.metadata
        if request.task:
            payload["task"] = request.task


        logger.info(f"📞 Sending call to {request.to_phone}")
        logger.info(f"Giving call payload {payload}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        logger.info(f"✅ Call sent successfully: {result}")

        return result

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"❌ HTTP error: {http_err}")
        error_detail = f"HTTP error occurred: {http_err}"
        if hasattr(http_err, 'response') and http_err.response:
            error_detail += f" - {http_err.response.text}"
        raise HTTPException(status_code=400, detail=error_detail)

    except requests.exceptions.Timeout:
        logger.error("❌ Request timeout")
        raise HTTPException(status_code=408, detail="Request timeout")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send call")

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_batch_call(request):
    """Send batch AI phone calls"""
    try:
        url = "https://api.bland.ai/v2/batches/create"
        bland_api_key = settings.BLAND_API_KEY
        
        if not bland_api_key:
            raise HTTPException(status_code=500, detail="BLAND_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {bland_api_key}",
            "Content-Type": "application/json"
        }

        global_payload = {
            "pathway_id": request.pathway_id
        }
        
        # Add optional global fields only if they have values
        if request.task:
            global_payload["task"] = request.task
        if request.record is not None:
            global_payload["record"] = request.record
        if request.webhook:
            global_payload["webhook"] = request.webhook

        payload = {
            "global": global_payload,
            "call_objects": [
                {
                    "phone_number": call.phone_number,
                    # "metadata": call.metadata or {}
                }
                for call in request.calls
            ]
        }

        logger.info(f"📞 Sending batch of {len(request.calls)} calls")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"✅ Batch sent successfully: {result}")
        
        return result

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"❌ HTTP error: {http_err}")
        error_detail = f"HTTP error occurred: {http_err}"
        if hasattr(http_err, 'response') and http_err.response:
            error_detail += f" - {http_err.response.text}"
        raise HTTPException(status_code=400, detail=error_detail)
    
    except requests.exceptions.Timeout:
        logger.error("❌ Request timeout")
        raise HTTPException(status_code=408, detail="Request timeout")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send batch")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def stop_active_call_from_id(call_id):
    bland_api_key = settings.BLAND_API_KEY
    headers = {
        "Authorization": f"Bearer {bland_api_key}",
        "Content-Type": "application/json"
        }
    url = f"https://api.bland.ai/v1/calls/{call_id}/stop"
    response = requests.post(url=url,headers=headers)
    response = response.json()
    return {"status":response["status"]}


def stop_all_calls():   
    bland_api_key = settings.BLAND_API_KEY
    headers = {
        "Authorization": f"Bearer {bland_api_key}",
        "Content-Type": "application/json"
        }
    url = f"https://us.api.bland.ai/v1/calls/active/stop"
    response = requests.post(url=url,headers=headers)
    response = response.json()
    return {"status":response["status"],
            "call":response["num_calls"]}
