from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from openai import OpenAI
from twilio.twiml.voice_response import VoiceResponse
import os

app = FastAPI()

# יצירת לקוח GPT עם המפתח שלך
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/voice")
async def voice(
    request: Request,
    SpeechResult: str = Form(None)
):
    response = VoiceResponse()

    if SpeechResult:
        # יש תמלול – שולחים ל-GPT
        verdict = await analyze_call(SpeechResult)
        response.say(f"השיחה מסווגת כ: {verdict}", language="he-IL", voice="Polly.Carmit")
    else:
        # תחילת שיחה – מבקשים מהמתקשר לדבר
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
אתה בוט קולי שמטרתו לסנן שיחות עבור קשישים. מדובר באוכלוסייה רגישה, והאחריות על כתפיך כבדה מאוד.

תפקידך הוא לנהל את השיחה ולהוביל אותה בצורה ברורה, חדה, קצרה ועניינית – מבלי לאפשר למתקשר להסיט את הנושא. אתה שואל, הוא עונה. בשום שלב אתה לא נותן לו לנהל את השיחה.

יש לשאול את השאלות הבאות, ברצף, בשפה ברורה ונוקשה:
1. מה שמך?
2. מאיזו חברה אתה מתקשר, או מטעם מי?
3. מה מטרת השיחה?

אם המתקשר לא עונה תשובות ברורות – יש לציין שהשיחה לא מאושרת.

אם התשובה קשורה לנושאים פיננסיים כגון בנק, פנסיה, ביטוח או מידע אישי רגיש – יש להזהיר את המשתמש שהשיחה חשודה, ולהמליץ שלא להמשיך את השיחה אלא רק לקבל הודעה.

השיחה צריכה להתנהל בהובלתך בלבד. כל ניסיון להסיט את השיחה, לשאול שאלות חזרה, להתחמק – צריך להיחשב כנורת אזהרה.

לאחר סיום השיחה, יש לנתח את מטרתה ולהחזיר אחת מהתשובות הבאות בלבד:
- בטוחה
- חשודה
- הונאה

תוכן השיחה כולה:
\"{transcript}\"

החזר רק אחת מהמילים: בטוחה, חשודה, הונאה בהתאם למה שהחלטת בשיחה.
"""

    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return chat.choices[0].message.content.strip()
