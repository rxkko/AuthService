from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.future import select
from models import User
from database import get_db
from services.token_service import decode_refresh_token, generate_new_access_token
from jose import jwt, JWTError
from config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if access_token:
            try:
                payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                email = payload.get("sub")
                if email:
                    async for db in get_db():
                        result = await db.execute(select(User).where(User.email == email))
                        user = result.scalars().first()
                        if user:
                            request.state.user = user
            except JWTError:
                pass  

        
        if not request.state.user and refresh_token:
            try:
                payload = decode_refresh_token(refresh_token)
                email = payload.get("sub")
                if email:
                    async for db in get_db():
                        result = await db.execute(select(User).where(User.email == email))
                        user = result.scalars().first()
                        if user:
                            request.state.user = user
                            new_access_token = generate_new_access_token(email)
                            response = await call_next(request)
                            response.set_cookie(
                                key="access_token",
                                value=new_access_token,
                                httponly=True,
                                secure=True,
                                samesite="lax",
                                max_age=1800
                            )
                            return response
            except HTTPException:
                pass

        return await call_next(request)
