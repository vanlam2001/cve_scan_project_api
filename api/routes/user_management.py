from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.register import User_Info, User_Type, User_Login
from ..models.register import hash_password, verify_password
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
    

    
    # Kiểm tra mật khẩu trùng khớp 
    if user_data["password"] != user_data["confirm_password"]:
        return {"message": "Mật khẩu không khớp nhau"}

    # Mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu
    hashed_password = hash_password(user_data["password"])
    user_data["password"] = hashed_password
    del user_data["confirm_password"]
    
    # Thêm giá trị mặc định cho maLoaiNguoiDung và tenLoai
    user_data["maLoaiNguoiDung"] = "user"
    user_data["tenLoai"] = "Người dùng"

     # Lưu thông tin người dùng vào MongoDB
    await db.users.insert_one(user_data)
    return {"message": "Đăng ký thành công"}

@router.post("/api/Dang-nhap", tags=[tags_auth])
async def login(user_login: User_Login, db: AsyncIOMotorClient = Depends(get_database)):
    # Lấy thông tin người dùng dựa trên tên người dùng
    user_data = await db.users.find_one({"username": user_login.username})
    
    if user_data is None:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")
    
    # Kiểm tra mật khẩu
    if not verify_password(user_login.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")

    # Ở đây, bạn có thể trả về thông tin người dùng sau khi đăng nhập thành công
    # Chẳng hạn, trả về dữ liệu của người dùng trừ đi mật khẩu
    user_data.pop("password", None)
    
    return user_data


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