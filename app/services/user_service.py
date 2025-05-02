from models import User
from fastapi import HTTPException
from sqlalchemy.future import select
from .auth_service import hash_password

async def create_user(db, email: str, username: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(password)
    new_user = User(email=email, username=username, hashed_password=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
