from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field, validator
from passlib.context import CryptContext
from ..utils.db import get_database
from motor.motor_asyncio import AsyncIOMotorClient
import re

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class User_Info(BaseModel):
    username: str
    password: str 
    confirm_password: str
    email: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and confirm_password != values["password"]:
            raise HTTPException(status_code=401, detail="Mật khẩu không khớp")
        return confirm_password
    
    @validator("password")
    def password_validations(cls, password):
        if len(password) < 8:
            raise HTTPException(status_code=401, detail="Mật khẩu phải có ít nhất 8 ký tự")
        common_passwords = ["12345678", "123456789", "1234567890"]
        if password in common_passwords:
            raise HTTPException(status_code=401, detail="Vui lòng chọn một mật khẩu mạnh hơn")
        return password
    
    @validator("email")
    def validate_email_format(cls, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise HTTPException(status_code=401, detail="Email không hợp lệ")
        return email

class User_Login(BaseModel):
    username: str
    password: str 
        

class User_Type(BaseModel):
    maLoaiNguoiDung: str
    tenLoai: str


# Hàm để tạo mật khẩu mã hóa Argon2 
def hash_password(password: str):
    return pwd_context.hash(password)

# Hàm để kiểm tra mật khẩu 
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

