from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from fastapi.responses import HTMLResponse
from app.schemas.call_data_schemas import( 
    CallCreate,
    CallBase
)
from app.schemas.requests_model import(
    SendCallRequest,
    BatchCallRequest,
    SendScheduledCallRequest,
    PromptBusiness,
    TTSRequest
)

from app.schemas.create_models import (
    CreateContact
)
from app.schemas.form_model import (
    EditCampaignForm
)

from app.services.stop_delete import(
    stop_call_from_call_id,
    stop_batch_calls
)
from app.services.call_service import (
    create_single_call,
    create_batch_call,
    # call_scheduler,
    stop_active_call_from_id
)
from app.services.webhook import (
    get_postcall_data
)
from app.services.get_services import (
    get_calls_from_db,
    get_call_from_id,
    get_call_recording_by_id,
    get_call_recording_from_id,
    campaigns_of_userID,
    contacts_of_campaigns
)
from app.services.delete_services import (
    delete_call_from_id,
    # delete_scheduler
)
from app.services.prompt_gen import (
    create_prompt_for_business
)
from app.services.edit import (
    changeCampaign
)
from app.services.create import (
    create_new_contact
)
from app.core.templates import templates 
from app.services.call_agent import ai_TTS
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the dashboard homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bland-ai-dashboard"}


@router.get("/calls")
async def get_calls(limit: int = 50, skip: int = 0,db: Session = Depends(get_db)):
    return await get_calls_from_db(limit, skip, db)

@router.get("/calls/{call_id}")
async def get_single_call(call_id:str,db:Session = Depends(get_db)):
    return await get_call_from_id(call_id,db)

@router.get("/call-recording/{call_id}")
async def get_call_recording(call_id:str):
    return await get_call_recording_by_id(call_id)


@router.get('/campaign/{user_id}/active')
async def get_active_campaigns_by_userID(user_id:int,db:Session = Depends(get_db)):
    return await campaigns_of_userID(user_id,db)

@router.get('/campaign/{campaign_thread_id}/contact-list')
async def get_campaign_contacts(campaign_thread_id:str,db:Session = Depends(get_db)):
    return await contacts_of_campaigns(campaign_thread_id,db)

@router.put("/campaign/{batch_id}/edit")
async def editCampaign(data:EditCampaignForm,batch_id:str,db:Session = Depends(get_db)):
    return await changeCampaign(batch_id,data,db)


@router.post("/create-contact/{user_id}")
def create_contact(user_id:str,contact_data:CreateContact,db:Session = Depends(get_db)):
    return create_new_contact(user_id,contact_data,db)

@router.post("/bland/postcall")
async def receive_postcall(request: Request,db: Session = Depends(get_db)):
    return await get_postcall_data(request,db)

@router.post("/bland/sendcall")
async def send_call(request: SendCallRequest):
    return await create_single_call(request)

@router.post("/bland/sendbatch")
async def send_batch(request: BatchCallRequest):
    return await create_batch_call(request)



@router.post("/stop-active-calls/{call_id}")
def stop_active_call_by_id(call_id:str):
    return stop_active_call_from_id(call_id)


@router.post("/create-prompt/business")
async def create_prompt(request:PromptBusiness):
    return await create_prompt_for_business(request)


@router.post("/speak-AI")
async def ai_speak(req:TTSRequest):
    return await ai_TTS(req)



@router.delete("/call/{id}")
async def delete_call_by_id(id:str,db:Session = Depends(get_db)):
    return await delete_call_from_id(id,db)

@router.delete('/stop/call/{call_id}')
def stop_call(call_id:str):
    return stop_call_from_call_id(call_id)

@router.delete('/stop/batch/{batch_id}')
def stop_batch(batch_id:str):
    return stop_batch_calls(batch_id)