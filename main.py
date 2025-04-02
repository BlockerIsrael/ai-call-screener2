from fastapi import FastAPI, Request
import openai
import os

# יצירת השרת
app = FastAPI()

# טעינת מפתח ה-GPT מהמערכת (הסברנו ל-Render לשמור אותו בשם OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY")

# יצירת מסלול (Route) ששמו /screen_call שמקבל שיחה לבדיקה
@app.post("/screen_call")
async def screen_call(request: Request):
    data = await request.json()
    phone_number = data.get("phone_number", "")
    simulated_text = data.get("caller_text", "")

    # הכנה של הטקסט שנשלח ל-GPT
    prompt = f"""
    אתה מסנן שיחות לקשישים.
    מטרתך להחליט אם מדובר בשיחה בטוחה, חשודה או הונאה.

    תוכן השיחה:
    "{simulated_text}"

    החזר רק אחת מהמילים: בטוחה, חשודה, הונאה.
    """

    # שליחת הבקשה ל-GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "user", "content": prompt }
        ]
    )

    # קבלת התשובה וחזרה אל המשתמש
    verdict = response.choices[0].message.content.strip()
    return { "verdict": verdict }
