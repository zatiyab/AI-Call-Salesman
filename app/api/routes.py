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
    get_call_recording_from_id
)
from app.services.delete_services import (
    delete_call_from_id,
    # delete_scheduler
)
from app.services.prompt_gen import (
    create_prompt_for_business
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

@router.get("/call-recording/{call_id}")
async def get_call_recording_by_id(call_id:str):
    return await get_call_recording_from_id(call_id)


@router.get("/calls")
async def get_calls(limit: int = 50, skip: int = 0,db: Session = Depends(get_db)):
    return await get_calls_from_db(limit, skip, db)

@router.get("/calls/{call_id}")
async def get_single_call(call_id:str,db:Session = Depends(get_db)):
    return await get_call_from_id(call_id,db)

@router.get("/call-recording/{call_id}")
async def get_call_recording(call_id:str):
    return await get_call_recording_by_id(call_id)


@router.post("/bland/postcall")
async def receive_postcall(request: Request,db: Session = Depends(get_db)):
    return await get_postcall_data(request,db)

@router.post("/bland/sendcall")
async def send_call(request: SendCallRequest):
    return await create_single_call(request)

@router.post("/bland/sendbatch")
async def send_batch(request: BatchCallRequest):
    return await create_batch_call(request)

# @router.post("/schedule-calls")
# async def schedule_calls(db:Session = Depends(get_db)):
#     return await call_scheduler(db)

@router.post("/stop-active-calls/{call_id}")
async def stop_active_call_by_id(call_id:str):
    return await stop_active_call_from_id(call_id)


@router.post("/create-prompt/business")
async def create_prompt(request:PromptBusiness):
    return await create_prompt_for_business(request)



@router.delete("/call/{id}")
async def delete_call_by_id(id:str,db:Session = Depends(get_db)):
    return await delete_call_from_id(id,db)


@router.post("/speak-AI")
async def ai_speak(req:TTSRequest):
    return await ai_TTS(req)

# @router.delete("/scheduler")
# async def empty_scheduler():
#     return await delete_scheduler()