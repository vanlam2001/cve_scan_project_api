from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field, validator
from argon2 import PasswordHasher
from ..utils.db import get_database


ph = PasswordHasher()

class User_Info(BaseModel):
    username: str
    password: str 
    confirm_password: str

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
    
    

class User_Login(BaseModel):
    username: str
    password: str 
        

class User_Type(BaseModel):
    maLoaiNguoiDung: str
    tenLoai: str


# Hàm để tạo mật khẩu mã hóa Argon2 
def hash_password(password: str):
    return ph.hash(password)

# Hàm để kiểm tra mật khẩu 
def verify_password(plain_password: str, hashed_password: str):
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except:
        return False

