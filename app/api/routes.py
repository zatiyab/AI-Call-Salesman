from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from fastapi.responses import HTMLResponse
from app.schemas.call_data_schemas import( 
    CallCreate,
    CallBase,
    SendCallRequest,
    BatchCallRequest,
    SendScheduledCallRequest
)
from app.services.call_service import (
    get_postcall_data,
    create_single_call,
    create_batch_call,
    get_calls_from_db,
    call_scheduler,
    delete_scheduler
)
from app.core.templates import templates  # Assuming you set up Jinja2Templates here

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

@router.post("/bland/postcall")
async def receive_postcall(request: Request,db: Session = Depends(get_db)):
    return await get_postcall_data(request,db)

@router.post("/bland/sendcall")
async def send_call(request: SendCallRequest):
    return await create_single_call(request)

@router.post("/bland/sendbatch")
async def send_batch(request: BatchCallRequest):
    return await create_batch_call(request)

@router.get("/calls")
async def get_calls(limit: int = 50, skip: int = 0,db: Session = Depends(get_db)):
    return await get_calls_from_db(limit, skip, db)

@router.post("/schedule-calls")
async def schedule_calls(db:Session = Depends(get_db)):
    return await call_scheduler(db)


@router.delete("/scheduler")
async def empty_scheduler():
    return await delete_scheduler()

# @router.get("/calls/{call_id}", response_model=CallRead)