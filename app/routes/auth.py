from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import UserRead, UserLogin, UserCreate
from services.user_service import create_user
from services.auth_service import User, authenticate_user, create_access_token, create_refresh_token
from database import get_db
from services.token_service import decode_refresh_token, generate_new_access_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_user = await create_user(db, user.email, user.username, user.password)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=604800)

    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out"}

@router.get("/me")
async def get_me(request: Request):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return f"Привет {request.state.user.username}"

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = decode_refresh_token(refresh_token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = generate_new_access_token(user.email)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=1800,
        secure=True,
        samesite="lax"
    )

    return {"access_token": new_access_token}
