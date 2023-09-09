from fastapi import Header, HTTPException

def get_token_authorization(Token: str = Header(..., description="Nhập token")) -> str:
    if Token != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c":
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    return Token