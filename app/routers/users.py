# app/routers/users.py

from ..schemas.users import UserCreate, UserRead
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from ..config.database import get_session
from ..utils.security import (
    create_email_verification_token,
    create_vefication_link,
    send_verification_email,
    decode_email_verification_token
)
from ..services.user_service import UserService


# Create a router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to register a new user
@router.post("/register", response_model=UserRead, status_code=201)
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
        user_id = decode_email_verification_token(token)
        await user_service.verify_user_email(user_id)
        return {"message": "Email verified successfully!"}
    except ValueError as e:
        return {"error": str(e)}


@router.post("/send-verification-email/{user_id}")
async def resend_verification_email(
    user_id: int,
    db=Depends(get_session)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate email verification token and link
    verification_token = create_email_verification_token(user.email)
    verification_link = create_vefication_link(verification_token)

    # Send the verification email
    try:
        await send_verification_email(user.email, verification_link)
        return {"message": "Verification email sent!"}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email"
        )
