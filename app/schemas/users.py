# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr                  # required
    password: str                    # raw password from user


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    created_at: str
    last_login: Optional[str] = None

    # Enable ORM mode to work with SQLAlchemy models
    class Config:
        orm_mode = True
