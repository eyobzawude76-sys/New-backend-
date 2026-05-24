# app/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Env variables fiduuf (.env fi Render irraa)
load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DATABASE_NAME", "university_db")

# 🔥 RAKKOO ATLAS IRRA TURTE HIKUOF:
# 'w=1' itti dabaluun dogoggora WriteConcernError 'majority' sana guutummaatti dhabamsiisa.
client = AsyncIOMotorClient(MONGO_URL, w=1)
db = client[DB_NAME]

# Collections kee guutuu bifa kanaan kaayyarra
users_collection = db["users"]
students_collection = db["students"]
courses_collection = db["courses"]
grades_collection = db["grades"]
results_collection = db["results"]