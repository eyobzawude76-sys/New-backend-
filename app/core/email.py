from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
)

async def send_approval_email(student_email: str, student_name: str, class_assigned: str):
    message = MessageSchema(
        subject="✅ Galmaa'uu Mirkanaa'e — University System",
        recipients=[student_email],
        body=f"""
        Nagaatti {student_name}!

        Galmaa'uun kee mirkanaa'e! 🎉

        Kutaa kee: Class {class_assigned}

        Baga milkaa'e!
        University System
        """,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_rejection_email(student_email: str, student_name: str, reason: str):
    message = MessageSchema(
        subject="❌ Galmaa'uu Didan — University System",
        recipients=[student_email],
        body=f"""
        Nagaatti {student_name}!

        Dhiifama — galmaa'uun kee hin mirkanaa'in.

        Sababaa: {reason}

        Gaaffii yoo qabatte admin qunnamuu dandeessa.
        University System
        """,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)