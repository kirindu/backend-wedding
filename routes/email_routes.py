# routes/email_routes.py
from fastapi import APIRouter, BackgroundTasks, HTTPException, Form
from utils.email_utils import send_email

router = APIRouter()

@router.post("/send-email")
async def send_test_email(
    background_tasks: BackgroundTasks,
    to: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    try:
        background_tasks.add_task(send_email, to, subject, message)
        return {"message": f"Envío de correo programado a {to}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))