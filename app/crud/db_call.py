from sqlalchemy.orm import Session
from app.models.call_table import Call
from app.schemas.call_data_schemas import CallCreate

def create_call(db: Session, call: CallCreate):
    db_call = Call(**call.model_dump())
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def get_call(db: Session, call_id: str):
    return db.query(Call).filter(Call.call_id == call_id).first()
