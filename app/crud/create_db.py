from sqlalchemy import select, insert
from app.models.call_table import (
    User,
    Contact,
    Campaign
)

def create_new_contact_db(user_id,contact_data,db):
    contact = Contact(name=contact_data.contact_name,
                      email = contact_data.email,
                      phone_number = contact_data.phone_number,
                      company_name = contact_data.company_name,
                      tags = contact_data.tags,
                      user_id = user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact