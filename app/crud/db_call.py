from sqlalchemy.orm import Session
from app.models.call_table import (
    Call,
    Campaign,
    Contact
    )
from app.schemas.call_data_schemas import CallCreate
from sqlalchemy import select
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
    metadata = data.get("metadata",{})
    if metadata:
        if metadata.get("is_followup",False) and metadata.get("followup_to_call_id",None):
            # Fetch the thread ID from the original call
            original_call = db.query(Call).filter(Call.call_id == metadata.get("followup_to_call_id")).first()
            if not original_call:
                raise ValueError("Original call for follow-up not found.")
            thread_id = original_call.call_thread_id
        else:
            print('else')
            # Create a new thread ID for the initial call
            thread_id = uuid.uuid4()
    else:
        # Create a new thread ID for the initial call
        print('Main-else')
        thread_id = uuid.uuid4()
    return thread_id

def delete_by_call_id(id,db):
    return db.query(Call).filter(Call.call_id == id).delete()

def get_calls_by_batch_id(batch_id,db):
    return db.execute(select(Call).where(Call.batch_id == batch_id)).scalars().all()

def get_campaign_thread_by_batch_id(batch_id, db):
    return db.execute(
        select(Call.campaign_thread_id).where(Call.batch_id == batch_id)
    ).scalars().all() 

def get_contact_by_contact_id(contact_id,db):
    return db.execute(
        select(Contact).where(Contact.contact_id == contact_id)
    ).scalar_one()

def get_curr_campaign(batch_id,db):
    return db.execute(
        select(Campaign).where(Campaign.batch_id == batch_id)
        ).scalar_one()

def create_campaign(campaign_data,db):
    db_campaign = Campaign(**campaign_data.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign) 
    return db_campaign

