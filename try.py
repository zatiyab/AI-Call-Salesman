import cohere
import json

co = cohere.Client("BCxkxzdkBAiA9Ey0mS7csgHSRxaV2YHcYu6mtTrg")  




call_date= "2025-07-18 09:40:48.402291+00"
call_transcript = """assistant: Good day, my name is Jeff and I'm part of the RetainIQ team. Can you please confirm if I've reached the correct person, and if you don't mind, could you please spell out your name for me? 
 user: Hello?  
 user: Yeah. You've reached the correct course. 
 user: My name is. 
 assistant: I think you started to say your name, but it got cut off. Could you please spell out your name for me so I can make sure I get it right? 
 user: My name is Aliyah Hossein. 
 assistant: Thank you, Aliyah Hossein. I pronounce that as Ah-lee-yah Ho-sayn, is that correct? I'm Jeff from RetainI- 
 user: Yes. 
 assistant: I'm Jeff from RetainIQ, an AI email technology company that helps e-commerce brands increase their email revenue. We've worked with over 100 brands in the last year, helping them boost their email revenue by up to 40%. Are you the right person to discuss how RetainIQ can help your e-commerce business? 
 user: Yes. I am the right person for it. 
 assistant: RetainIQ is an AI email technology company that helps e-commerce brands increase their email revenue by using AI-powered personalization to automatically add dynamic content elements in emails. RetainIQ directly integrates with most email service providers like Klaviyo, Omnisend and it is Klaviyo's gold partner. Would you like me to expand on anything specific, Aliyah? 
 user: Not really. 
 assistant: I'd like to offer you a 15-minute call with one of our AI specialists to discuss how RetainIQ can help your e-commerce business increase its email revenue. We can also conduct a free live audit of your current email strategy during this call. Would you be interested in booking a call? 
 user: Yeah. I'd be interested, but not right now. 
 user: Can I book a call later? 
 assistant: That's completely understandable, Aliyah. I'd be happy to help you book a call at a later time that's more convenient for you. When would you be available for a 15-minute call, would it be sometime next week? 
 user: I'm available on first of August. 
 user: At three PM. 
 user: EST. 
 assistant: Great, I've got you down for August 1st at 3 PM EST. Just to confirm, you're available at 3 PM on August 1st in the Eastern Standard Time timezone, correct? 
 user: No. In Indian standard time zone. 
 assistant: You mentioned August 1s- 
 user: Yes. 
 assistant: You mentioned August 1st at 3 PM, but in Indian Standard Time. I just want to confirm that 3 PM IST might not be the best time for our call since it's outside of our usual operating hours. Would you be available at a different time, perhaps between 5 PM and 2 AM IST on August 1st? 
 user: Yeah. 
 user: Let's do a call on six PM. 
 assistant: We have a call scheduled for August 1st at 6 PM IST. Before I send over a formal invite, I just want to confirm your email address. 
 """
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
data = json.loads(answer)
print(data)

