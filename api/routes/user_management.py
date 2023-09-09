from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.register import User_Info, User_Type
from ..models.register import verify_password, get_password_hash
from ..utils.db import get_database
from ..utils.security import get_token_authorization
from typing import List
router = APIRouter()

tags_auth = "Đăng nhập & Đăng ký"
tags_user = "Quản lý người dùng"

@router.post("/api/Dang-ky", tags=[tags_auth])
async def register(user: User_Info, token: str = Depends(get_token_authorization), db: AsyncIOMotorClient = Depends(get_database)):
    user_data = user.dict()

    # Kiểm tra xem tài khoản đã tồn tại chưa 
    existing_user = await db.users.find_one({"username": user_data["username"]})
    if existing_user:
        return {"message": "Tài khoản đã tồn tại"}
    
    # Kiểm tra xem email đã tồn tại chưa 
    existing_email = await db.users.find_one({"email": user_data["email"]})
    if existing_email:
        return {"message": "Email đã tồn tại"}
    # Kiểm tra xem phone_number đã tồn tại chưa 
    existing_phone_number = await db.users.find_one({"phone_number": user_data["phone_number"]})
    if existing_phone_number:
        return {"message": "Số điện thoại đã tồn tại"}
    
    # Kiểm tra mật khẩu trùng khớp 
    if user_data["password"] != user_data["confirm_password"]:
        return {"message": "Mật khẩu không khớp nhau"}

    # Mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu
    hashed_password = get_password_hash(user_data["password"])
    user_data["password"] = hashed_password
    del user_data["confirm_password"]

    # Lấy thông tin loại người dùng từ cơ sở dữ liệu
    user_type = await db.loai_nguoi_dung.find_one({"maLoaiNguoiDung": user_data["maLoaiNguoiDung"]})
    if user_type:
        user_data["tenLoai"] = user_type["tenLoai"]

        # Lưu thông tin người dùng vào MongoDB
        await db.users.insert_one(user_data)
        return {"message": "Đăng ký thành công"}
    else:
        return {"message": "Loại người dùng không hợp lệ"}
    

@router.post("/api/Tao-loai-nguoi-dung", tags=[tags_user])
async def create_loai_nguoi_dung(loai_nguoi_dung: User_Type, db: AsyncIOMotorClient = Depends(get_database)):
    collection = db['loai_nguoi_dung']
    list_data = loai_nguoi_dung.dict()
    result = await collection.insert_one(list_data)

    if result:
        return {"message": "Đã tạo loại người dùng", "loai_nguoi_dung_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Không thể tạo loại người dùng")


@router.get("/api/Loai-nguoi-dung", response_model=List[User_Type], tags=[tags_user])
async def get_user_types_endpoint(database: AsyncIOMotorClient = Depends(get_database)):
    user_types_collection = database["loai_nguoi_dung"]
    user_types = []
    async for user_type in user_types_collection.find():
        user_types.append(User_Type(**user_type))
    return user_types