# # celery.py
# from celery import Celery

# celery_app = Celery(
#     "call_scheduler",
#     broker="redis://localhost:6379/0",      # Task queue
#     backend="redis://localhost:6379/1"      # Optional: result backend
# )

# celery_app.conf.update(
#     task_serializer="json",
#     result_serializer="json",
#     accept_content=["json"],
#     timezone="Asia/Kolkata",
#     enable_utc=True,
# )

# celery_app.autodiscover_tasks(["app.services"])
