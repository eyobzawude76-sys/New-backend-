from fastapi import APIRouter, HTTPException, Depends, Response, File, UploadFile
from app.database import students_collection, results_collection, courses_collection
from app.routes.auth import require_role, get_current_user
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from bson import ObjectId
import io, os, shutil

router = APIRouter(prefix="/student", tags=["Student"])

# ── Register godhi ──────────────────────────────────────
@router.post("/register")
async def register_student(student_data: dict):
    student_data["status"] = "pending"
    result = await students_collection.insert_one(student_data)
    return {"message": "Registration galmeeffame! Admin irraa eegi.", "id": str(result.inserted_id)}

# ── Result ilaali ───────────────────────────────────────
@router.get("/my-result")
async def get_my_result(
    semester: str,
    student=Depends(require_role("student"))
):
    student_id = str(student["_id"])
    student_email = student.get("email", "")

    # Student record argadhu
    student_record = await students_collection.find_one({
        "$or": [
            {"email": student_email},
            {"user_id": student_id},
        ]
    })

    # IDs hunda collect godhi
    ids_to_check = [student_id]
    if student_record:
        ids_to_check.append(str(student_record.get("_id", "")))
        ids_to_check.append(str(student_record.get("user_id", "")))

    results = await results_collection.find({
        "semester": semester,
        "is_published": True,
        "student_id": {"$in": ids_to_check}
    }).to_list(length=50)

    if not results:
        results = await results_collection.find({
            "semester": semester,
            "student_id": {"$in": ids_to_check}
        }).to_list(length=50)

    for r in results:
        r["_id"] = str(r["_id"])
    return results

# ── PDF Download ────────────────────────────────────────
@router.get("/download-result")
async def download_result(
    semester: str,
    token: str = None
):
    from app.core.security import decode_token
    from app.database import users_collection

    if not token:
        raise HTTPException(status_code=401, detail="Token hin jiru")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token sirrii miti")

    user = await users_collection.find_one({"email": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=404, detail="User hin argamne")

    student_id = str(user["_id"])
    student_email = user.get("email", "")

    student_record = await students_collection.find_one({
        "$or": [
            {"email": student_email},
            {"user_id": student_id},
        ]
    })

    ids_to_check = [student_id]
    if student_record:
        ids_to_check.append(str(student_record.get("_id", "")))
        ids_to_check.append(str(student_record.get("user_id", "")))

    results = await results_collection.find({
        "semester": semester,
        "student_id": {"$in": ids_to_check}
    }).to_list(length=50)

    if not results:
        raise HTTPException(status_code=404, detail="Result hin argamne")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, height - 60, "UNIVERSITY RESULT CARD")
    p.setFont("Helvetica", 14)
    p.drawCentredString(width/2, height - 90, f"Semester: {semester}")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, height - 140, f"Student: {user['full_name']}")

    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, height - 200, "Course")
    p.drawString(250, height - 200, "Score")
    p.drawString(330, height - 200, "Percentage")
    p.drawString(450, height - 200, "Grade")
    p.line(60, height - 210, width - 60, height - 210)

    y = height - 230
    p.setFont("Helvetica", 11)
    for r in results:
        p.drawString(60, y, str(r.get("course_id", "")))
        p.drawString(250, y, f"{r.get('total_score', '')}/{r.get('max_score', '')}")
        p.drawString(330, y, f"{r.get('percentage', '')}%")
        p.drawString(450, y, str(r.get("grade", "")))
        y -= 25

    p.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=result_{semester}.pdf"}
    )

# ── Documents Upload ────────────────────────────────────
@router.post("/upload-documents")
async def upload_documents(
    national_id_photo: UploadFile = File(...),
    grade12_result: UploadFile = File(...),
    bank_receipt: UploadFile = File(...),
    email: str = None,
):
    import uuid
    upload_id = str(uuid.uuid4())[:8]
    folder_name = email.replace("@", "_").replace(".", "_") if email else upload_id
    upload_dir = f"uploads/{folder_name}"
    os.makedirs(upload_dir, exist_ok=True)

    paths = {}
    for file, filename in [
        (national_id_photo, "national_id"),
        (grade12_result, "grade12_result"),
        (bank_receipt, "bank_receipt"),
    ]:
        ext = file.filename.split(".")[-1]
        full_filename = f"{filename}.{ext}"
        path = os.path.join(upload_dir, full_filename).replace("\\", "/")
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        paths[filename] = path

    if email:
        await students_collection.update_one(
            {"email": email},
            {"$set": {
                "documents_uploaded": True,
                "national_id_photo": paths["national_id"],
                "grade12_result": paths["grade12_result"],
                "bank_receipt": paths["bank_receipt"],
            }}
        )

    return {
        "message": "✅ Documents galmeeffaman!",
        "paths": paths
    }