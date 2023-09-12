from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.register import User_Info, User_Type, User_Login
from ..models.register import hash_password, verify_password
from ..utils.db import get_database
from ..utils.security import get_token_authorization
from typing import List
import smtplib
import random
import string 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from datetime import datetime, timedelta

router = APIRouter()

tags_auth = "Đăng nhập & Đăng ký"
tags_user = "Quản lý người dùng"

# Hàm để tạo mã xác minh ngẫu nhiên (ví dụ: mã OTP)
def generate_verification_code():
    code = ''.join(random.choice(string.digits) for _ in range(6))
    return code

# Hàm để gửi email xác minh qua Gmail 
def send_verification_email(to_email, verification_code):
    # Thông tin đăng nhập vào tài khoản gmail 
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "lam213181@gmail.com"
    smtp_password = "iovkjbicmemaisjf"

    # Tạo đối tượng SMTP 
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)

    # Tạo nội dung email 
    subject = "Xác minh tài khoản"
    from_email = "lam213181@gmail.com"
    to_email = to_email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Nội dung email
    body = f"Chào mừng bạn đến với ứng dụng của chúng tôi. Mã xác minh của bạn là: {verification_code}"
    msg.attach(MIMEText(body, "plain"))

    # Gửi email
    smtp.sendmail(from_email, to_email, msg.as_string())

    # Đóng kết nối SMTP 
    smtp.quit()

# Hàm để tạo mã OTP mới và cập nhật thời gian hết hạn 
def generate_and_update_otp(db, email):
    otp_code = generate_verification_code() # Tạo mã otp mới 
    expiry_time = datetime.now() + timedelta(minutes=5) # Thời gian hết hạn là sau 5 phút 

    # Cập nhật mã OTP và thời gian hết hạn vào database 
    db.users.update_one({"email": email}, {"$set": {"otp_code": otp_code, "otp_expiry_time": expiry_time}})

    # Gửi mã OTP mới qua mail
    send_verification_email(email, otp_code)




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

    # Tạo và gửi mã xác minh qua email 
    verification_code = generate_verification_code()
    try:
        send_verification_email(user_data["email"], verification_code)
        # Lưu mã OTP và thời gian hết hạn vào database  
        generate_and_update_otp(db, user_data["email"])
    except Exception as e:
        return {"message": "Đã có lỗi xảy ra khi gửi email xác minh. Vui lòng thử lại sau."}

    return {"message": "Đăng ký thành công, Mã xác nhận đã được gửi qua email"}

@router.post("/api/Xac-minh", tags=[tags_auth])
async def verify_account(email: str, verification_code: str, token: str = Depends(get_token_authorization) ,db: AsyncIOMotorClient = Depends(get_database)):
    # Kiểm tra xem email và mã xác minh có hợp lệ không
    user_data = await db.users.find_one({"email": email})
    if user_data:
        if user_data.get("otp_code") and user_data.get("otp_expiry_time") > datetime.now() and user_data.get("otp_code") == verification_code:
           # Đánh dấu tài khoản là đã xác minh không cần xác minh lại 
           await db.users.update_one({"email": email}, {"$set": {"verified": True, "otp_code": None, "otp_expiry_time": None}})
           return {"message": "Xác minh tài khoản thành công"}
        else:
            return {"message": "Mã xác minh không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu gửi lại mã OTP mới."}
    else: 
        return {"message": "Không tìm thấy tài khoản với địa chỉ email này."}
    
@router.post("/api/Gui-lai-OTP", tags=[tags_auth])
async def resend_otp(email: str,token: str = Depends(get_token_authorization) , db: AsyncIOMotorClient = Depends(get_database)):
    user_data = await db.users.find_one({"email": email})
    if user_data:
        if user_data.get("otp_code") and user_data.get("otp_expiry_time") > datetime.now():
            return {"message": "Mã OTP hiện vẫn còn hiệu lực."}
        else:
            generate_and_update_otp(db, email)
            return {"message": "Đã gửi mã OTP mới qua email."}
    else:
        return {"message": "Không tìm thấy tài khoản với địa chỉ email này."}


@router.post("/api/Dang-nhap", tags=[tags_auth])
async def login(user_data: User_Login,token: str = Depends(get_token_authorization) ,db: AsyncIOMotorClient = Depends(get_database)):
    

    # Tìm người dùng trong cơ sở dữ liệu bằng tên đăng nhập
    collection = db['users']
    user = await collection.find_one({"username": user_data.username})
    if user is None:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")

    # Xác minh mật khẩu
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")
    
    # Xác thực thành công, trả về thông tin tài khoản 
    user_info = {
        "username": user["username"],
        "password": user["password"],
        "email": user["email"],
        "maLoaiNguoiDung": user["maLoaiNguoiDung"],
        "tenLoai": user["tenLoai"],
        "message": "Đăng nhập thành công"
    }

    return user_info





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