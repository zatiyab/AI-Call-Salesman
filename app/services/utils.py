import cohere
import json
from app.core.config import settings

def format_datetime(iso_str):
    from datetime import datetime
    import pytz

    dt_utc = datetime.fromisoformat(iso_str)

    ist = pytz.timezone("Asia/Kolkata")
    dt_ist = dt_utc.astimezone(ist)

    formatted = dt_ist.strftime("%Y-%m-%d %H:%M:%S %z")

    final_time = formatted[:-2] + ":" + formatted[-2:]

    print(final_time)
    return final_time


def llm_generate_data(data):

    co = cohere.Client(api_key=settings.COHERE_API_KEY) 
    call_date= data.get('created_at')
    call_transcript =  data.get('concatenated_transcript')

    prompt = f"""
    You are an AI assistant that analyzes customer service call transcripts. Based on the transcript and the call date, extract the following details:

    1. **Summary**: A brief summary of the conversation (3-5 lines).
    2. **Customer Reaction**: Categorize the customer's overall reaction to the product as one of: `Positive`, `Negative`, or `Neutral`.
    3. **Next Call Scheduled Datetime**: Extract the date and time of the next scheduled call, if mentioned. Format it as an ISO 8601 string (e.g., "2025-07-19T15:00:00").
    4. **Timezone**: The timezone associated with the next scheduled call, if available (e.g., "Asia/Kolkata", "UTC", etc.). If not explicitly mentioned, infer from context or return `Unknown`.
    5. **Is Call Scheduled?**: Return `True` if a follow-up call is scheduled, otherwise `False`.

    ### Input:
    **Call Date**: {call_date}

    **Transcript**:
    '''
    {call_transcript}
    '''

    ### Output Format (in JSON):
    ```json
    {{
    "summary": "<summary_here>",
    "customer_reaction": "<Positive/Negative/Neutral>",
    "next_call_datetime": "<ISO_8601_datetime_or_null>",
    "timezone": "<timezone_or_unknown>",
    "is_call_scheduled": <true_or_false>
    }}
    """

    response = co.chat(
        model="command-r-plus",
        message=prompt,
        temperature=0.5,
        chat_history=[],
        connectors=[],
    )

    answer = (response.text).strip('```').lstrip('json')
    print(answer)
    data = json.loads(answer)
    print("JSON:",json.loads(answer))
    print(data)
    return data


from datetime import datetime

def serialize_datetimes(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetimes(i) for i in obj]
    return obj
