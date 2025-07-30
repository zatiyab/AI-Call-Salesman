# # from app.services.scheduler import (
# #     schedule_call,
# #     scheduler    
# #     )


# # async def call_scheduler(db):
# #     calls = get_scheduled_call(db)
# #     calls_serialized = [SendScheduledCallRequest.model_validate(call) for call in calls]
# #     try:
# #         for call in calls_serialized:
# #             schedule_call(call.model_dump())
# #         return {"message":"Calls scheduled"}
    
# #     except Exception as e:
# #         logger.error(f"Error in call scheduler: {e}")


# from app.core.config import llm
# from app.schemas.llm_data import SalesCallResult



# async def create_prompt_for_business(req):
#     customer_name = 'Ali Atiyab Husain'
#     customer_email = "aliatiyab.husain@gmail.com"
#     business_name = req.business_name
#     product_description = req.product_desc
#     business_description = req.business_desc
#     prompt = f'''
# Goal:
# Call potential customers to introduce a product on behalf of a business. Explain the value of the product or service, ask if they would like more information via email, and offer to schedule a future call if they’re currently unavailable.

# Call Flow:

# Introduce yourself as an AI assistant calling on behalf of the business.

# Confirm you're speaking with {customer_name}.

# Briefly explain the business and product.

# Ask if they’d like more information via email (e.g., brochures, documents, or a link).

# If yes, confirm their email address: {customer_email}.

# If they’re busy, ask for a more convenient time to follow up and schedule accordingly.

# Thank them for their time, regardless of the outcome.

# After the call, return a JSON response summarizing the interaction.

# Background:
# You are an AI assistant created to make sales calls for companies. Your job is to present the product in a friendly, informative way, gauge interest, and collect customer preferences (email or callback scheduling). These calls improve outreach and increase conversion. Be polite, helpful, and concise — keeping the call under 2 minutes where possible.

# You will be provided dynamically with:

# Business Description: {business_description}

# Product Description: {product_description}

# Customer Name: {customer_name}

# Customer Email: {customer_email}

# Example Call Snippet:

# You: Hi, this is Alex, an AI assistant calling on behalf of {business_name}. Am I speaking with {customer_name}?

# Customer: Yes.

# You: Awesome! Just a quick moment — I’d love to share something with you. We offer {product_description}, which might be helpful for you. Would you be interested in receiving a brochure or more details via email?

# Customer: Sure, that sounds good.

# You: Great! I have {customer_email} on file. Is that correct?

# Customer: Yes.

# You: Perfect — I’ll send that over after the call. If you have any questions, feel free to reply to the email. Thanks for your time, and have a great day!

# If customer is busy:

# You: No problem at all — would there be a better time this week I could call you back?

# Customer: Maybe Friday morning?

# You: Got it, I’ll schedule a call for Friday morning. Thanks again — talk soon!

# 📦 At the end of the call, respond with a JSON object like this:

# {{
#   "summary": "<summary of what happened in the call>",
#   "customer_reaction": "<Positive | Negative | Neutral>",
#   "next_call_datetime": "<ISO_8601_datetime_or_null>",  
#   "timezone": "<timezone_or_unknown>",
#   "is_call_scheduled": <true_or_false>,
#   "need_email": <true_or_false>,
#   "cust_email": "<customer_email_or_null>"
# }}
# Example JSON Output:

# {{
#   "summary": "Customer was interested in the product and agreed to receive more information via email.",
#   "customer_reaction": "Positive",
#   "next_call_datetime": null,
#   "timezone": "Asia/Kolkata",
#   "is_call_scheduled": false,
#   "need_email": true,
#   "cust_email": "johndoe@example.com"
# }}
# '''


#     response = llm.chat(
#         model="command-r-plus",
#         message=prompt,
#         temperature=0.5,
#         chat_history=[],
#         connectors=[],
#     )
#     print(response.text)
#     # result = SalesCallResult.model_validate_json(response.choices[0].text)
#     return {"response":response.text}


# scheduler = BackgroundScheduler()
# scheduler.start()
# followup_call_id = None

# def send_call_post(payload):
#     for key, value in payload.items():
#         if isinstance(value, datetime):
#             payload[key] = value.isoformat()
#     print('Actual Payload')
#     print(type(payload))
#     requests.post("https://e60889698168.ngrok-free.app/bland/sendcall", json=payload)


# def schedule_call(payload):
#     from apscheduler.triggers.date import DateTrigger
#     from datetime import datetime

#     scheduled_time = datetime.fromisoformat(str(payload['scheduled_call_datetime']))

#     # Ensure it’s in the future
#     if scheduled_time <= datetime.now(scheduled_time.tzinfo):
#         logger.error(f"Scheduled time is in the past for call id: {payload["call_id"]}")
#         return

#     job_id = f"call_{payload['call_id']}"  # Unique ID per call

#     if scheduler.get_job(job_id):
#         logger.info(f"Job {job_id} already scheduled.")
#         return
#     # payload["metadata"] = {'followup_to_call_id': payload["call_id"], "is_followup" : True}


#     trigger = DateTrigger(run_date=scheduled_time)
#     scheduler.add_job(send_call_post, trigger=trigger, args=[payload], id=job_id)
#     logger.info(f"Scheduled job {job_id} at {scheduled_time}")



# # def schedule_next_call(data:SendCallRequest,date,followup_to_call_id):
# #     print('After Validation Data: ')
# #     payload = data.model_dump()
# #     payload['start_time'] = format_datetime(date)
# #     payload['metadata'] = {
# #         "is_followup":True,
# #         "followup_to_call_id":followup_to_call_id}
# #     print('Giving scheduled call payload: ',payload)
# #     response = requests.post("https://e60889698168.ngrok-free.app/bland/sendcall", json=payload ,timeout=30)
# #     response = response.json()
# #     logger.info(f"Scheduled call id: {response.get('call_id',None)} from call id: {followup_to_call_id}")


# # import asyncio




# @router.delete("/scheduler")
# async def empty_scheduler():
#     return await delete_scheduler()


# @router.post("/schedule-calls")
# async def schedule_calls(db:Session = Depends(get_db)):
#     return await call_scheduler(db)