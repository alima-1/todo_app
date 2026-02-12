# app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr                  # required
    password: str                    # raw password from user


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    created_at: str
    last_login: str | None = None

    # Enable ORM mode to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)