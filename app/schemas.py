from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str