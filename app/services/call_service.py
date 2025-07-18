from app.core.database import logger
from fastapi import Request, HTTPException
import requests
import logging
from app.core.config import settings
from app.core.database import conn, cur
from app.crud.db_call import create_call

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.call_data_schemas import CallCreate, CallRead
from app.crud.db_call import create_call, get_call

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# @router.post("/calls", response_model=CallRead)
# def create_call_route(call: CallCreate, db: Session = Depends(get_db)):
#     return create_call(db, call)

# @router.get("/calls/{call_id}", response_model=CallRead)
# def get_call_route(call_id: str, db: Session = Depends(get_db)):
#     return get_call(db, call_id)




async def get_postcall_data(request: Request, db: Session):
    """Receive and process webhook callbacks from Bland AI"""
    try:
        data =  await request.json()
        logger.info(f"📥 Incoming Webhook Payload: {data}")

        call_id = str(data.get("call_id"))
        transcript = str(data.get("concatenated_transcript"))
        summary = str(data.get("summary"))
        # variables = str(data.get("variables", {}))
        call_to = str(data.get("to"))
        call_from = str(data.get("from"))

        logger.info(f"🆔 Call ID: {call_id}")
        logger.info(f"📄 Summary: {summary}")
        # logger.info(f"📦 Variables: {variables}")

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
                    "goal": "Understand customer's interest in real estate projects and satisfaction level",
                    "questions": [
                        ["Did customer answer","boolean"],
                        ["what was the customer's reaction to the product", " 'positive' or 'negative' or 'neutral' "],
                        ["Follow-up required", "boolean"],
                        ["Next Call Schedule Data, give data and time if specified","string"]
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
                else:
                    logger.error(f"❌ Analysis API error: {analysis_response.status_code} - {analysis_response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Analysis request failed: {e}")
            except Exception as e:
                logger.error(f"❌ Analysis processing error: {e}")

        # Prepare call record
        call_data = CallCreate(
            emotion=analysis_data['answers'][1],
            completed=True,
            summary=summary,
            from_phone=call_from,
            to_phone=call_to,
            call_id=call_id,
            call_transcript=str(transcript)
        )


       
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
            "phone_number": request.phone_number,
            "pathway_id": request.pathway_id,
            "variables": request.variables or {}
        }

        # Add optional fields only if they have values
        if request.task:
            payload["task"] = request.task
        if request.record is not None:
            payload["record"] = request.record
        if request.webhook:
            payload["webhook"] = request.webhook

        logger.info(f"📞 Sending call to {request.phone_number}")
        
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
                    "variables": call.variables or {}
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


async def get_calls_from_db(limit: int = 50, skip: int = 0):
    """Get call history from database"""
    try:
        cursor = calls_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        calls = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for call in calls:
            if "_id" in call:
                call["_id"] = str(call["_id"])
        
        return {"calls": calls, "count": len(calls)}
    
    except Exception as e:
        logger.error(f"❌ Error fetching calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")
    
