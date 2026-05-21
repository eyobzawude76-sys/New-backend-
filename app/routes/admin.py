from fastapi import APIRouter, HTTPException, Depends, Query
from app.database import students_collection, users_collection, courses_collection
from app.routes.auth import require_role
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["Admin"])

# ── Student registrations hunda ilaala ─────────────────
@router.get("/registrations")
async def get_registrations(
    status: str = "pending",
    admin=Depends(require_role("admin"))
):
    registrations = await students_collection.find(
        {"status": status}
    ).to_list(length=100)

    for r in registrations:
        r["_id"] = str(r["_id"])
    return registrations

# ── Student approve godhi ───────────────────────────────
@router.patch("/registrations/{reg_id}/approve")
async def approve_registration(
    reg_id: str,
    class_assigned: str = Query(...), # Query parameter ta'uu isaa ifatti gooneerra
    admin=Depends(require_role("admin"))
):
    # Student info argadhu
    student = await students_collection.find_one({"_id": ObjectId(reg_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Barataan database keessa hin jiru")
    
    # Database irratti update godhi
    await students_collection.update_one(
        {"_id": ObjectId(reg_id)},
        {"$set": {
            "status": "approved",
            "class_assigned": class_assigned,
            "approved_by": str(admin["_id"])
        }}
    )
    
    # Email ergi (Kallattiidhaan akka lixu gooneerra)
    if student.get("email"):
        try:
            from app.core.email import send_approval_email
            await send_approval_email(
                student_email=student["email"],
                student_name=student["full_name"],
                class_assigned=class_assigned
            )
            print(f"✅ Email nagaadhan gara {student['email']} tti ergameera!")
        except Exception as e:
            print(f"❌ Email error uumame: {e}")
    
    return {"message": "Student approved successfully and email sent!"}

# ── Student reject godhi ────────────────────────────────
@router.patch("/registrations/{reg_id}/reject")
async def reject_registration(
    reg_id: str,
    reason: str = Query(...),
    admin=Depends(require_role("admin"))
):
    student = await students_collection.find_one({"_id": ObjectId(reg_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Barataan database keessa hin jiru")
    
    await students_collection.update_one(
        {"_id": ObjectId(reg_id)},
        {"$set": {
            "status": "rejected",
            "rejection_reason": reason,
            "approved_by": str(admin["_id"])
        }}
    )

    if student.get("email"):
        try:
            from app.core.email import send_rejection_email
            await send_rejection_email(
                student_email=student["email"],
                student_name=student["full_name"],
                reason=reason
            )
            print(f"✅ Rejection Email gara {student['email']} tti ergameera!")
        except Exception as e:
            print(f"❌ Email error uumame: {e}")

    return {"message": "Student rejected successfully!"}

# ── Course uumi ─────────────────────────────────────────
@router.post("/courses")
async def create_course(
    course_data: dict,
    admin=Depends(require_role("admin"))
):
    result = await courses_collection.insert_one(course_data)
    return {"message": "Course created!", "id": str(result.inserted_id)}

# ── Course hunda ilaala ─────────────────────────────────
@router.get("/courses")
async def get_courses(admin=Depends(require_role("admin"))):
    courses = await courses_collection.find().to_list(length=100)
    for c in courses:
        c["_id"] = str(c["_id"])
    return courses

# ── Student Info ────────────────────────────────────────
@router.get("/student-info/{student_id}")
async def get_student_info(
    student_id: str,
    committee=Depends(require_role("committee"))
):
    try:
        student = await students_collection.find_one(
            {"user_id": student_id}
        )
        if not student:
            student = await students_collection.find_one(
                {"_id": ObjectId(student_id)}
            )
        if not student:
            return {"full_name": "Unknown", "class_assigned": "-", "department": "-"}
        
        student["_id"] = str(student["_id"])
        return student
    except:
        return {"full_name": "Unknown", "class_assigned": "-", "department": "-"}

# ── Teacher Uumi ────────────────────────────────────────
@router.post("/teachers")
async def create_teacher(
    teacher_data: dict,
    admin=Depends(require_role("admin"))
):
    from app.core.security import get_password_hash

    existing = await users_collection.find_one({"email": teacher_data["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    course = await courses_collection.find_one({
        "department": teacher_data["department"],
        "level": teacher_data["level"],
        "year": teacher_data["year"]
    })

    user = {
        "full_name": teacher_data["full_name"],
        "email": teacher_data["email"],
        "password": get_password_hash(teacher_data["password"]),
        "role": "teacher",
        "department": teacher_data["department"],
        "level": teacher_data["level"],
        "year": teacher_data["year"],
        "course_id": course["code"] if course else None,
    }
    result = await users_collection.insert_one(user)
    
    if course:
        await courses_collection.update_one(
            {"_id": course["_id"]},
            {"$set": {"teacher_id": str(result.inserted_id)}}
        )
    
    return {
        "message": "✅ Teacher uumame!",
        "id": str(result.inserted_id),
        "course_id": course["code"] if course else None
    }

# ── Teachers Hunda Ilaala ───────────────────────────────
@router.get("/teachers")
async def get_teachers(admin=Depends(require_role("admin"))):
    teachers = await users_collection.find({"role": "teacher"}).to_list(length=100)
    for t in teachers:
        t["_id"] = str(t["_id"])
        t.pop("password", None)
    return teachers
