from app.crud.create_db import create_new_contact_db

def create_new_contact(user_id,contact_data,db):
    return create_new_contact_db(user_id,contact_data,db)