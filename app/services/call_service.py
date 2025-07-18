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
    CallBase, 
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
import cohere
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import requests
from datetime import datetime
import pytz
from app.services.scheduler import schedule_call,scheduler

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def call_scheduler(db):
    calls = get_scheduled_call(db)
    calls_serialized = [SendScheduledCallRequest.model_validate(call) for call in calls]
    try:
        for call in calls_serialized:
            schedule_call(call.model_dump())
        return {"message":"Calls scheduled"}

    except Exception as e:
        logger.error(f"Error in call scheduler: {e}")

# @router.post("/calls", response_model=CallRead)
# def create_call_route(call: CallCreate, db: Session = Depends(get_db)):
#     return create_call(db, call)

# @router.get("/calls/{call_id}", response_model=CallRead)
# def get_call_route(call_id: str, db: Session = Depends(get_db)):
#     return get_call(db, call_id)

async def llm_generate_data(data):

    co = cohere.Client("BCxkxzdkBAiA9Ey0mS7csgHSRxaV2YHcYu6mtTrg") 
    call_date= data.get('created_at')
    call_transcript =  data.get('concatenated_transcript')

    prompt = f"""
    You are an AI assistant that analyzes customer service call transcripts. Based on the transcript and the call date, extract the following details:

    1. **Summary**: A brief summary of the conversation (3-5 lines).
    2. **Customer Reaction**: Categorize the customer's overall reaction to the product as one of: `Positive`, `Negative`, or `Neutral`.
    3. **Next Call Scheduled Datetime**: Extract the date and time of the next scheduled call, if mentioned. Format it as an ISO 8601 string (e.g., "2025-07-19T15:00:00").
    4. **Timezone**: The timezone associated with the next scheduled call, if available (e.g., "Asia/Kolkata", "UTC", etc.). If not explicitly mentioned, infer from context or return `Unknown`.
    5. **Is Call Scheduled?**: Return `True` if a follow-up call is scheduled, otherwise `False`.

    ### Input:
    **Call Date**: {call_date}

    **Transcript**:
    '''
    {call_transcript}
    '''

    ### Output Format (in JSON):
    ```json
    {{
    "summary": "<summary_here>",
    "customer_reaction": "<Positive/Negative/Neutral>",
    "next_call_datetime": "<ISO_8601_datetime_or_null>",
    "timezone": "<timezone_or_unknown>",
    "is_call_scheduled": <true_or_false>
    }}
    """

    response = co.chat(
        model="command-r-plus",
        message=prompt,
        temperature=0.5,
        chat_history=[],
        connectors=[],
    )

    answer = (response.text).strip('```').lstrip('json')
    data = json.loads(answer)

    return data


async def delete_scheduler():
    try:
        scheduler.remove_all_jobs()
        logger.info("Emptied Scheduler")
        return {"status":"successful"}
    except:
        raise HTTPException(500)


async def get_postcall_data(request: Request, db: Session):
    """Receive and process webhook callbacks from Bland AI"""
    try:
        data =  await request.json()
        llm_data = await llm_generate_data(data)
        logger.info(f"📥 Incoming Webhook Payload: {data}")
        # thread_id = get_call_thread_id(db,data)
        call_id = str(data.get("call_id"))
        transcript = str(data.get("concatenated_transcript"))
        summary = str(data.get("summary"))
        # metdata = str(data.get("metadata", {}))
        call_to = str(data.get("to"))
        call_from = str(data.get("from"))

        logger.info(f"🆔 Call ID: {call_id}")
        logger.info(f"📄 Summary: {summary}")
        

        if not call_id:
            logger.error("❌ Missing call_id in webhook payload")
            raise HTTPException(status_code=400, detail="Missing call_id")

        if not isinstance(transcript, str):
            logger.error("❌ Invalid transcript format")
            raise HTTPException(status_code=400, detail="Invalid transcript format")
        
        logger.info(f"📝 Transcript Text: {transcript}")

        # Call Bland AI analysis endpoint
        analysis_data = None
        bland_api_key = settings.BLAND_API_KEY
        
        if bland_api_key and call_id:
            try:
                headers = {"Authorization": f"Bearer {bland_api_key}"}
                analysis_url = f"https://api.bland.ai/v1/calls/{call_id}/analyze"
                analysis_payload = {
                    "goal": "Understand the customer's interest in the product and pay attention to whether they want to schedule another call",
                    "questions": [
                        ["Did customer answer","boolean"],
                        ["what was the customer's reaction to the product", " 'positive' or 'negative' or 'neutral' "],
                        ["Is call scheduled, Return True if a follow-up call is scheduled, otherwise False.", "boolean"],
                        ["Next Call Schedule Data, give timestamp if specified,Extract the date and time of the next scheduled call, if mentioned. Format it as an ISO 8601 string (e.g., '2025-07-19T15:00:00').","string"],
                        ["Next Call Schedule Data, give Timezone if specified","string"]
                    ]
                }

                analysis_response = requests.post(
                    analysis_url, 
                    json=analysis_payload, 
                    headers=headers,
                    timeout=30
                )
                
                if analysis_response.status_code == 200:
                    analysis_data =  analysis_response.json()
                    logger.info(f"📊 Analysis successful: {analysis_data}")
                    logger.info(f"📊 LLM Data: ",llm_data)
                else:
                    logger.error(f"❌ Analysis API error: {analysis_response.status_code} - {analysis_response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Analysis request failed: {e}")
            except Exception as e:
                logger.error(f"❌ Analysis processing error: {e}")

        # Prepare call record
        print(data.get('batch_id',"None"))
        
        call_data = CallCreate(
            # call_thread_id=thread_id,
            batch_id= data.get('batch_id',"None"),
            created_at=data.get('created_at'),
            is_call_scheduled=analysis_data['answers'][2],
            timezone=analysis_data['answers'][4],
            scheduled_call_datetime=analysis_data['answers'][3],
            emotion=analysis_data['answers'][1],
            status=data.get('status'),
            summary=summary,
            from_phone=call_from,
            to_phone=call_to,
            call_id=call_id,
            call_transcript=str(transcript)
        )
        if call_data.is_call_scheduled == "True":
            schedule_call(call_data)
        for i in get_scheduled_call(db):
            print(i.call_id,i.to_phone,i.from_phone)

       
        try:
            result =  create_call(db,call_data)
            logger.info(f"✅ Inserted into PostgresDB with ID: {result.call_id}")
        except Exception as e:
            logger.error(f"❌ PostgresDB insert error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

        return {
            "status": "success", 
            "message": "Call processed successfully",
            "call_id": call_id,
            "analysis_available": analysis_data is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in webhook processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


async def create_single_call(request):
    """Send a single AI phone call"""
    print(request)
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
            "pathway_id": request.pathway_id
        }

        # Optional fields
        if request.task:
            payload["task"] = request.task
        if request.record is not None:
            payload["record"] = request.record
        if request.webhook:
            payload["webhook"] = request.webhook

        # Follow-up support
        # if request.call_thread_id:
        #     payload["call_thread_id"] = request.call_thread_id
        # if request.is_followup:
        #     payload["is_followup"] = request.is_followup
        # if request.followup_to_call_id:
        #     payload["followup_to_call_id"] = request.followup_to_call_id

        logger.info(f"📞 Sending call to {request.to_phone}")
        print(type(payload))
        print(payload)
    
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


async def get_calls_from_db(limit, skip,db):
    """Get call history from database"""
    try:
        calls = get_all_calls(db)
        calls_serialized = [CallRead.model_validate(call) for call in calls]
        
        return {"calls": calls_serialized, "count": len(calls_serialized)}
    
    
    except Exception as e:
        logger.error(f"❌ Error fetching calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")
    
