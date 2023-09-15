from pydantic import BaseModel

# Tạo một model để đại diện cho trang web đã lưu trữ
class Website(BaseModel):
    url: str
    status: str