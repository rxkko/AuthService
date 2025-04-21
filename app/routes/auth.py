from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import UserRead, UserLogin, UserCreate
from auth import User, authenticate_user, create_access_token, hash_password
from database import get_db

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
    return token

@router.get("/me")
async def get_me(request: Request):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return f"Привет {request.state.user.username}"