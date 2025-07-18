from sqlalchemy.orm import Session
from app.models.call_table import Call
from app.schemas.call_data_schemas import CallCreate
import uuid

def create_call(db: Session, call: CallCreate):
    db_call = Call(**call.model_dump())
    db.add(db_call)
    db.commit()
    db.refresh(db_call) 
    return db_call

def get_scheduled_call(db:Session):
    return db.query(Call).filter(Call.is_call_scheduled == True).all()


def get_all_calls(db: Session):
    return db.query(Call).all()

def get_call_by_id(db: Session, call_id: str):
    return db.query(Call).filter(Call.call_id == call_id).first()


def get_call_thread_id(db:Session,data):
    metadata = data.get("metadata")
    if metadata:
        if metadata.get("is_followup") and metadata.get("followup_to_call_id"):
            # Fetch the thread ID from the original call
            original_call = db.query(Call).filter(Call.id == metadata.get("followup_to_call_id")).first()
            if not original_call:
                raise ValueError("Original call for follow-up not found.")
            thread_id = original_call.call_thread_id
        else:
            # Create a new thread ID for the initial call
            thread_id = uuid.uuid4()
    else:
        # Create a new thread ID for the initial call
        thread_id = uuid.uuid4()
    return thread_id