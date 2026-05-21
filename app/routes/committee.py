from fastapi import APIRouter, HTTPException, Depends
from app.database import grades_collection, results_collection, students_collection
from app.routes.auth import require_role
from bson import ObjectId

router = APIRouter(prefix="/committee", tags=["Committee"])

# ── Pending grades hunda ilaala ─────────────────────────
@router.get("/pending-grades")
async def get_pending_grades(
    committee=Depends(require_role("committee"))
):
    grades = await grades_collection.find(
        {"status": "pending"}
    ).to_list(length=200)

    for g in grades:
        g["_id"] = str(g["_id"])
    return grades

# ── Grade Approve fi Final Result Calculate (Walitti Makameera) ──
@router.patch("/grades/{grade_id}/approve")
async def approve_grade(
    grade_id: str,
    committee=Depends(require_role("committee"))
):
    # 1. Grade database irraa argadhu
    grade = await grades_collection.find_one({"_id": ObjectId(grade_id)})
    if not grade:
        raise HTTPException(status_code=404, detail="Grade hin argamne")

    # 2. Haala isaa "approved" godhi
    await grades_collection.update_one(
        {"_id": ObjectId(grade_id)},
        {"$set": {
            "status": "approved",
            "approved_by": str(committee["_id"])
        }}
    )

    # 3. Ragaalee barbaachisan fudhadhu (Bifa String ta'uun isaanii ni mirkanaa'a)
    student_id = str(grade["student_id"])
    course_id = str(grade["course_id"])
    semester = grade.get("semester", "y1_s1")

    # 4. Qabxiilee barataa kanaa kan koorsii kana irratti approved ta'an hunda fidi
    # MongoDB irratti query'n kee String fi ObjectId lamaaniyyu akka laalluuf $in gargaaramneera
    grades = await grades_collection.find({
        "student_id": {"$in": [student_id, ObjectId(student_id) if ObjectId.is_valid(student_id) else student_id]},
        "course_id": {"$in": [course_id, ObjectId(course_id) if ObjectId.is_valid(course_id) else course_id]},
        "semester": semester,
        "status": "approved"
    }).to_list(length=100)

    if grades:
        total = sum(float(g["score"]) for g in grades)
        max_total = sum(float(g.get("max_score", 100)) for g in grades)
        percentage = (total / max_total) * 100 if max_total > 0 else 0

        # Seera Grade Letter kee odoo hin tuqin
        if percentage == 100: grade_letter = "A+"
        elif percentage >= 90: grade_letter = "A"
        elif percentage >= 80: grade_letter = "B+"
        elif percentage >= 70: grade_letter = "B"
        elif percentage >= 60: grade_letter = "C"
        elif percentage >= 50: grade_letter = "D"
        else: grade_letter = "F"

        # Result kanaan dura kuufamee jiraa?
        existing = await results_collection.find_one({
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester,
        })

        if existing:
            # Kan jiru update godhi
            await results_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "total_score": float(total),
                    "max_score": float(max_total),
                    "percentage": round(float(percentage), 2),
                    "average": round(float(percentage), 2),
                    "grade": grade_letter,
                    "is_published": True,
                }}
            )
        else:
            # Haaraa uumi
            await results_collection.insert_one({
                "student_id": student_id,
                "course_id": course_id,
                "semester": semester,
                "total_score": float(total),
                "max_score": float(max_total),
                "percentage": round(float(percentage), 2),
                "average": round(float(percentage), 2),
                "grade": grade_letter,
                "is_published": True,
                "approved_by": str(committee["_id"])
            })

    return {"message": "✅ Qabxii approved fi result updated!"}

# ── Grade reject godhi ──────────────────────────────────
@router.patch("/grades/{grade_id}/reject")
async def reject_grade(
    grade_id: str,
    reason: str,
    committee=Depends(require_role("committee"))
):
    await grades_collection.update_one(
        {"_id": ObjectId(grade_id)},
        {"$set": {
            "status": "rejected",
            "rejection_reason": reason
        }}
    )
    return {"message": "Qabxii rejected!"}

# ── All students ilaali ─────────────────────────────────
@router.get("/all-students")
async def get_all_students(
    committee=Depends(require_role("committee"))
):
    students = await students_collection.find(
        {"status": "approved"}
    ).to_list(length=500)

    result = []
    for s in students:
        result.append({
            "_id": str(s["_id"]),
            "full_name": s.get("full_name", ""),
            "email": s.get("email", ""),
            "course_id": s.get("course_id", ""),
            "course_name": s.get("course_name", ""),
            "department": s.get("department", ""),
            "year": s.get("year", ""),
            "level": s.get("level", ""),
            "session": s.get("session", ""),
            "class_assigned": s.get("class_assigned", ""),
            "user_id": s.get("user_id", ""),
        })
    return result

# ── Student info argadhu ────────────────────────────────
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