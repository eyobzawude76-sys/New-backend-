# app/models/user.py
from pydantic import BaseModel, EmailStr,Field,ConfigDict
from typing import Optional
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    COMMITTEE = "committee"
    STUDENT = "student"

class UserModel(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Role
    is_active: bool = True