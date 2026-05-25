from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings
import asyncio

# 🔥 AMMAA FI ISA DHUMAA: Port 587 fi STARTTLS Render irratti akka nagaan darbuuf
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,                      # 🔥 465 irraa gara 587 jijjiirameera
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,                 # 🔥 Kun TLS akka ta'u True godhame
    MAIL_SSL_TLS=False,                 # 🔥 Kun False ta'uu qaba Port 587'f
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30                          # Sekondii 30 eega
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
    
    # 🚀 NETWORK RENDER IRRA DEDDEEBI'EE AKKA CABSUF (Retry 3 Times)
    fm = FastMail(conf)
    for attempt in range(3):
        try:
            await fm.send_message(message)
            print("✅ Email approval sent successfully to student!")
            return # Yoo ergame hojii xumura
        except Exception as e:
            print(f"⚠️ Yaalii {attempt + 1}ffaa irratti network sitti dide: {e}")
            if attempt < 2:
                await asyncio.sleep(3) # Sekondii 3 eeggatee lammata yaala
            else:
                print("❌ Email dhumarratti dhowwameera.")

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
    
    # 🚀 NETWORK RENDER IRRA DEDDEEBI'EE AKKA CABSUF (Retry 3 Times)
    fm = FastMail(conf)
    for attempt in range(3):
        try:
            await fm.send_message(message)
            print("✅ Email rejection sent successfully to student!")
            return # Yoo ergame hojii xumura
        except Exception as e:
            print(f"⚠️ Yaalii {attempt + 1}ffaa irratti network sitti dide: {e}")
            if attempt < 2:
                await asyncio.sleep(3) # Sekondii 3 eeggatee lammata yaala
            else:
                print("❌ Email dhumarratti dhowwameera.")