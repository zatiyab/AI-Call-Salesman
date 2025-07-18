from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import requests
from app.core.database import logger
from datetime import datetime
import pytz
from app.crud.db_call import create_call, get_all_calls,get_call_by_id, get_scheduled_call
from app.schemas.call_data_schemas import (CallCreate, CallRead, CallBase)


scheduler = BackgroundScheduler()
scheduler.start()
followup_call_id = None

def send_call_post(payload):
    for key, value in payload.items():
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
    print('Actual Payload')
    print(type(payload))
    requests.post("https://e60889698168.ngrok-free.app/bland/sendcall", json=payload)


def schedule_call(payload):
    from apscheduler.triggers.date import DateTrigger
    from datetime import datetime

    scheduled_time = datetime.fromisoformat(str(payload['scheduled_call_datetime']))

    # Ensure it’s in the future
    if scheduled_time <= datetime.now(scheduled_time.tzinfo):
        logger.error(f"Scheduled time is in the past for call id: {payload["call_id"]}")
        return

    job_id = f"call_{payload['call_id']}"  # Unique ID per call

    if scheduler.get_job(job_id):
        logger.info(f"Job {job_id} already scheduled.")
        return
    # payload["metadata"] = {'followup_to_call_id': payload["call_id"], "is_followup" : True}


    trigger = DateTrigger(run_date=scheduled_time)
    scheduler.add_job(send_call_post, trigger=trigger, args=[payload], id=job_id)
    logger.info(f"Scheduled job {job_id} at {scheduled_time}")




