from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, admin, teacher, committee, student
import os

os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="University Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/public/courses")
async def get_public_courses():
    from app.database import courses_collection
    courses = await courses_collection.find().to_list(length=100)
    for c in courses:
        c["_id"] = str(c["_id"])
    return courses

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(teacher.router)
app.include_router(committee.router)
app.include_router(student.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "University System API Running! 🚀"}