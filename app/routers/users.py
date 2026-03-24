# app/routers/users.py

import datetime

import jwt
import
from ..schemas.users import UserCreate, UserRegisterResponse
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from ..config.database import get_session
from ..utils.security import (
    create_email_verification_token,
    create_vefication_link,
    send_verification_email,
    verify_token
)
from ..services.user_service import UserService
from datetime import timedelta, timezone
from app.exceptions.exceptions import UserNotFoundError

# Create a router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to register a new user
@router.post("/register", response_model=UserRegisterResponse, status_code=201)
async def register_new_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db=Depends(get_session),
):
    # instantiate the user service and register the user
    user_service = UserService(db)

    # Register the user and get the new user object
    new_user = await user_service.register_user(user_data)

    # Generate email verification token and link
    verification_token = create_email_verification_token(new_user.email)
    verification_link = create_vefication_link(verification_token)

    # Send the verification email in the background
    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        verification_link
    )
    return {
        "user": new_user,
        "msg": (
            "User registered successfully! "
            "Please check your email to verify your account."
        )
    }


# Endpoint to verify email
@router.get("/verify-email")
async def verify_email(token: str, db=Depends(get_session)):
    user_service = UserService(db)
    try:
        user_id = verify_token(token)
        await user_service.verify_user_email(user_id)
        return {"message": "Email verified successfully!"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Verification token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid verification token")   
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)              
    
    
@router.post("/send-verification-email/{user_id}")
async def resend_verification_email(
    user_id: int,
    db=Depends(get_session)
):
    cooldown_period = timedelta(minutes=1)
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.last_verification_email_sent_at:
        time_since_last = datetime.now(timezone.utc) - user.last_verification_email_sent_at
        if time_since_last < cooldown_period:
            raise HTTPException(
                status_code=429,
                detail="Please wait before requesting another verification email"
            )

    # Generate email verification token and link
    verification_token = create_email_verification_token(user.id)
    print(f"Generated verification token: {verification_token}")  # Debugging log
    verification_link = create_vefication_link(verification_token)

    # Send the verification email
    try:
        await send_verification_email(user.email, verification_link)
        # Ensure this is also UTC to match your DB column type
        user.last_verification_email_sent_at = datetime.now(timezone.utc)
        await db.commit()
        return {"message": "Verification email sent!"}
    except Exception as e:
        await db.rollback()  # Always rollback on failure to clean up the transaction
        print(f"Update failed: {e}")  # Log the actual error to your terminal
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email"
        )
