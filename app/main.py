from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# 1. Dursa APP uumna
app = FastAPI(title="University Management System")

# 2. ISAA BOODA CORS daddafnee gaddaan lakkifna (Eeyyama hundaaf saaqna)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. KUNIS AMMA JALLATTI DHUFA: Erga CORS qophaa'ee booda route-wwan import ta'u
from app.routes import auth, admin, teacher, committee, student

os.makedirs("uploads", exist_ok=True)

@app.get("/public/courses")
async def get_public_courses():
    from app.database import courses_collection
    courses = await courses_collection.find().to_list(length=100)
    for c in courses:
        c["_id"] = str(c["_id"])
    return courses

# 4. Route-wwan include gochuu
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(teacher.router)
app.include_router(committee.router)
app.include_router(student.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "University System API Running! 🚀"}