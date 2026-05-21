# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

# Collections
users_collection = db["users"]
students_collection = db["students"]
courses_collection = db["courses"]
grades_collection = db["grades"]
results_collection = db["results"]