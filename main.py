from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from openai import OpenAI
from twilio.twiml.voice_response import VoiceResponse
import os

app = FastAPI()

# לקוח GPT
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/voice")
async def voice(
    request: Request,
    SpeechResult: str = Form(None)
):
    response = VoiceResponse()

    if SpeechResult:
        # יש תמלול - שולחים ל-GPT
        verdict = await analyze_call(SpeechResult)
        response.say(f"השיחה מסווגת כ: {verdict}", language="he-IL", voice="Polly.Carmit")
    else:
        # תחילת שיחה - מבקשים מהמתקשר לדבר
        gather = response.gather(
            input='speech',
            timeout=5,
            speech_timeout='auto',
            action='/voice',
            method='POST'
        )
        gather.say("שלום, בבקשה תגיד את תוכן השיחה", language="he-IL", voice="Polly.Carmit")

    return Response(content=str(response), media_type="application/xml")


async def analyze_call(transcript):
    prompt = f"""
    אתה מסנן שיחות לקשישים.
    מטרתך להחליט אם מדובר בשיחה בטוחה, חשודה או הונאה.

    תוכן השיחה:
    "{transcript}"

    החזר רק אחת מהמילים: בטוחה, חשודה, הונאה.
    """

    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return chat.choices[0].message.content.strip()
