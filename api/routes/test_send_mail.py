from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText


router = APIRouter()

class EmailData(BaseModel):
    subject: str
    recipient_email: str
    message: str

@router.post("/send_email")
async def send_email(email_data: EmailData):
    # Thông tin tài khoản email của bạn
    sender_email = "lam213181@gmail.com"
    sender_password = ""

    # Tạo nội dung email
    msg = MIMEText(email_data.message)
    msg["Subject"] = email_data.subject
    msg["From"] = sender_email
    msg["To"] = email_data.recipient_email

    try:
        # Kết nối đến máy chủ email và gửi thư
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [email_data.recipient_email], msg.as_string())

        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")