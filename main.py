from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
from twilio.twiml.voice_response import VoiceResponse
import os

app = FastAPI()

# יצירת לקוח GPT עם המפתח שלך מהסביבה
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# מסלול API עיקרי שמקבל טקסט לבדיקה
@app.post("/screen_call")
async def screen_call(request: Request):
    data = await request.json()
    phone_number = data.get("phone_number", "")
    simulated_text = data.get("caller_text", "")

    prompt = f"""
    אתה מסנן שיחות לקשישים.
    מטרתך להחליט אם מדובר בשיחה בטוחה, חשודה או הונאה.

    תוכן השיחה:
    "{simulated_text}"

    החזר רק אחת מהמילים: בטוחה, חשודה, הונאה.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    verdict = response.choices[0].message.content.strip()
    return { "verdict": verdict }

# מסלול ש-Twilio יקרא לו כשהתקבלה שיחה
@app.post("/voice")
async def voice_webhook():
    response = VoiceResponse()
    response.say(
        "שלום, השיחה מנותבת דרך מערכת סינון שיחות חכמה. אנא המתן.",
        language="he-IL",
        voice="Polly.Carmit"
    )
    return PlainTextResponse(content=str(response), media_type="application/xml")
