from jose import jwt, JWTError
from fastapi import HTTPException
from .auth_service import create_access_token
from config import settings


def decode_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

def generate_new_access_token(user_email: str):
    return create_access_token(data={"sub": user_email})
