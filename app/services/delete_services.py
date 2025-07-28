from app.crud.db_call import  delete_by_call_id
# from app.services.scheduler import scheduler
from app.core.database import logger
from fastapi import HTTPException

async def delete_call_from_id(id,db):
    return delete_by_call_id(id,db)


# async def delete_scheduler():
#     try:
#         scheduler.remove_all_jobs()
#         logger.info("Emptied Scheduler")
#         return {"status":"successful"}
#     except:
#         raise HTTPException(500)
