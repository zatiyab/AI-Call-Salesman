from sqlalchemy import select, func
from app.models.call_table import (
    Call,
    Campaign,
    Contact,
    User
)

def campaigns_by_userID(user_id,db):
    return db.execute(
        select(Campaign).where(Campaign.user_id == user_id)
        ).scalars().all()

def get_number_of_calls_from_campaignID(campaign_thread_ID,db):
    return db.execute(
        select(func.count(Call.call_id))
        .where(Call.campaign_thread_id == campaign_thread_ID)
    ).scalars().all()
def get_contacts_from_campaign_id(campaign_thread_id,db):
    subquery = select(Call.contact_id).where(Call.campaign_thread_id == campaign_thread_id).subquery()
    return db.execute(
        select(Contact).where(Contact.contact_id.in_(subquery))
    ).scalars().all()