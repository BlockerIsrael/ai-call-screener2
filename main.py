from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from openai import OpenAI
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# משתנים זמניים לשמירת תוכן התשובות
call_data = {}

@app.post("/voice")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(None),
    step: str = Form(default="start"),
    CallSid: str = Form(default=None)
):
    response = VoiceResponse()
    sid = CallSid or "temp"

    if sid not in call_data:
        call_data[sid] = {"name": "", "company": "", "purpose": ""}

    if step == "start":
        gather = Gather(input="speech", action="/voice", method="POST", speechTimeout="auto")
        gather.say("שלום, כאן העוזר של בר. מה שמך בבקשה?", language="he-IL", voice="Polly.Carmit")
        response.append(gather)

    elif step == "name":
        call_data[sid]["name"] = SpeechResult or ""
        gather = Gather(input="speech", action="/voice", method="POST", speechTimeout="auto")
        gather.say("מאיזו חברה אתה מתקשר או מטעם מי?", language="he-IL", voice="Polly.Carmit")
        response.append(gather)

    elif step == "company":
        call_data[sid]["company"] = SpeechResult or ""
        gather = Gather(input="speech", action="/voice", method="POST", speechTimeout="auto")
        gather.say("מה מטרת השיחה שלך?", language="he-IL", voice="Polly.Carmit")
        response.append(gather)

    elif step == "purpose":
        call_data[sid]["purpose"] = SpeechResult or ""

        # שליחת הכל ל-GPT
        full_text = f"""
        שם המתקשר: {call_data[sid]['name']}
        החברה או הגורם: {call_data[sid]['company']}
        מטרת השיחה: {call_data[sid]['purpose']}
        """

        verdict = await analyze_call(full_text)

        if verdict == "בטוחה":
            response.say("תודה. השיחה סווגה כבטוחה. אנו מחברים אותך עכשיו.", language="he-IL", voice="Polly.Carmit")
        elif verdict == "חשודה":
            response.say("השיחה מסווגת כחשודה. מחזיקים את השיחה לבדיקה נוספת.", language="he-IL", voice="Polly.Carmit")
        elif verdict == "הונאה":
            response.say("השיחה סווגה כהונאה. מנתקים את השיחה.", language="he-IL", voice="Polly.Carmit")
            response.hangup()
        else:
            response.say("לא ניתן לקבוע את טיב השיחה. סיום.", language="he-IL", voice="Polly.Carmit")
            response.hangup()

        call_data.pop(sid, None)  # מנקה מהזיכרון

    return Response(content=str(response), media_type="application/xml")


async def analyze_call(transcript):
    prompt = f"""
אתה עוזר קול שמסנן שיחות עבור קשישים. עליך להעריך האם מדובר בשיחה בטוחה, חשודה או הונאה – לפי שלושה פרטים:

{transcript}

ענה רק באחת מהמילים: בטוחה, חשודה, הונאה.
    """

    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return chat.choices[0].message.content.strip()
