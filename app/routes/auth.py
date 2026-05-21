from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from app.database import users_collection
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)
from app.core.config import settings
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Current user argachuuf ──────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sirrii miti"
        )
    user = await users_collection.find_one({"email": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=404, detail="User hin argamne")
    return user

# ── Role check ──────────────────────────────────────────
def require_role(*roles):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail="Permission hin qabdu"
            )
        return current_user
    return role_checker

# ── Register ────────────────────────────────────────────
@router.post("/register")
async def register(user_data: dict):
    existing = await users_collection.find_one({"email": user_data["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_data["password"] = get_password_hash(user_data["password"])
    result = await users_collection.insert_one(user_data)
    return {"message": "User created", "id": str(result.inserted_id)}

# ── Login ───────────────────────────────────────────────
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Email ykn password dogoggora"
        )

    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["full_name"]
    }
@router.post("/change-password")
async def change_password(
    data: dict,
    current_user=Depends(get_current_user)
):
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Password hunda galchi!")

    if not verify_password(old_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="Password durii dogoggora!")

    hashed = get_password_hash(new_password)

    from app.database import users_collection
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"password": hashed}}
    )

    return {"message": "✅ Password jijjiirrame!"}