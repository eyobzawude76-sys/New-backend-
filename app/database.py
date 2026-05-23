# app/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Env dubbisuuf
load_dotenv()

# Render irraas ta'e .env irraa kallattiin fida
MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DATABASE_NAME", "university_db")

# Client kaasuuf
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections kee guutuu
users_collection = db["users"]
students_collection = db["students"]
courses_collection = db["courses"]
grades_collection = db["grades"]
results_collection = db["results"]