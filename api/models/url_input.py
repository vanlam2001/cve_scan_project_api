from pydantic import BaseModel, validator
from fastapi import HTTPException

class Url_Input(BaseModel):
    url: str

    @validator('url')
    def validate_url(cls, value):
        if not value.startswith(('http://', 'https://')):
            raise HTTPException(status_code=401, detail="Vui lòng nhập URL hợp lệ bắt đầu bằng 'http://' hoặc 'https://'")
        return value

  