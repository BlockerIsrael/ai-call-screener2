from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.post("/twilio/voice")
async def handle_call(request: Request):
    # נחזיר ל-Twilio הנחיה להשמיע הודעה מוקלטת
    response = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="woman" language="he-IL">שלום, אנא המתן בזמן שאנחנו בודקים את מטרת השיחה</Say>
        <Pause length="1"/>
        <Say>Connecting to virtual assistant...</Say>
    </Response>
    """
    return Response(content=response, media_type="application/xml")
