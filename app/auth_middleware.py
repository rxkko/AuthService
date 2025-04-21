from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import JWTError, jwt
from fastapi import status
from auth import SECRET_KEY, ALGORITHM
from database import get_db
from models import User
from sqlalchemy.future import select


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        token = request.cookies.get("access_token")
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                if email:
                    async for db in get_db():
                        result = await db.execute(select(User).where(User.email == email))
                        user = result.scalars().first()
                        request.state.user = user
            except JWTError:
                pass
        return await call_next(request)