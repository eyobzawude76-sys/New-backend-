from fastapi import APIRouter, HTTPException, Depends
from app.database import grades_collection, students_collection
from app.routes.auth import require_role
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/teacher", tags=["Teacher"])

# ── Course kee students ilaala ──────────────────────────
@router.get("/my-students")
async def get_my_students(teacher=Depends(require_role("teacher"))):
    students = await students_collection.find({
        "course_id": teacher["course_id"],
        "status": "approved"
    }).to_list(length=100)

    for s in students:
        s["_id"] = str(s["_id"])
    return students

# ── Qabxii galmeessi ────────────────────────────────────
@router.post("/grades")
async def add_grade(
    grade_data: dict,
    teacher=Depends(require_role("teacher"))
):
    # 1. Dursa Id'n dhufe sirrii ta'uu isaa check godhi
    student_id_str = str(grade_data["student_id"])
    
    # 2. Barsiisaan course isaa qofa galmeessuu danda'a (SEERA KEE)
    # Check yeroo goonu ObjectId fi String lamaaniyyu akka laalluuf $or gargaaramneera
    query_filter = {
        "course_id": teacher["course_id"],
        "$or": [
            {"user_id": student_id_str},
            {"_id": ObjectId(student_id_str) if ObjectId.is_valid(student_id_str) else student_id_str}
        ]
    }
    
    student = await students_collection.find_one(query_filter)
    if not student:
        raise HTTPException(
            status_code=403,
            detail="Barataan kun course kee keessa hin jiru!"
        )

    # 3. Ragaalee kuufaman qindeessi (Id wal-simachuu akka danda'uuf)
    # Barataa keessaa user_id yoo jiraate fudhata, yoo kaan _id bifa string godhee kuusa
    final_student_id = student.get("user_id", str(student["_id"]))

    grade_data["student_id"] = final_student_id  # <--- Koomitee fi barataa waliin kan wal-simu
    grade_data["teacher_id"] = str(teacher["_id"])
    grade_data["course_id"] = teacher["course_id"]
    grade_data["status"] = "pending"
    grade_data["date"] = datetime.now()

    # Score fi max_score int/float ta'uu mirkaneessi (Calculation akka hin dhowwineef)
    if "score" in grade_data:
        grade_data["score"] = float(grade_data["score"])
    if "max_score" in grade_data:
        grade_data["max_score"] = float(grade_data["max_score"])

    result = await grades_collection.insert_one(grade_data)
    return {"message": "Qabxii galmeeffame!", "id": str(result.inserted_id)}

# ── Grades kee hunda ilaala ─────────────────────────────
@router.get("/my-grades")
async def get_my_grades(teacher=Depends(require_role("teacher"))):
    grades = await grades_collection.find({
        "teacher_id": str(teacher["_id"])
    }).to_list(length=200)

    for g in grades:
        g["_id"] = str(g["_id"])
    return grades