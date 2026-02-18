# app/routers/users.py

from ..schemas.users import UserCreate, UserRead
from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_session
from sqlalchemy.future import select
from ..models.users import User
from ..utils.security import (
    hash_password,
    is_strong_password,
    create_email_verification_token
)
from ..services.user_service import UserService


# Create a router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to register a new user
@router.post("/register", response_model=UserRead, status_code=201)
async def register_new_user(user_data: UserCreate, db=Depends(get_session)):
    user_service = UserService(db)
    new_user = await user_service.register_user(user_data)
    # Generate email verification token (for demonstration, we just print it)
    verification_token = create_email_verification_token(new_user.email)
    print(f"Verification token for {new_user.email}: {verification_token}")
    return new_user
