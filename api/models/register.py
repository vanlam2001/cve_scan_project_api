from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext

class User_Info(BaseModel):
    username: str
    password: str
    confirm_password: str
    phone_number: str
    email: str
    maLoaiNguoiDung: Optional[str]
    tenLoai: Optional[str]

class User_Type(BaseModel):
    maLoaiNguoiDung: str
    tenLoai: str

class HashedPassword:
    def __init__(self, hashed_password: str):
        self.hashed_password = hashed_password

class UserInDB(User_Info, HashedPassword):
    pass 

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_context.hash(password)