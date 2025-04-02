from fastapi import FastAPI, Request
from openai import OpenAI
import os

app = FastAPI()

# יצירת לקוח עם המפתח שלך
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
