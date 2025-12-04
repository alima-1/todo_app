# app/routers/users.py
from ..schemas.users import UserCreate, UserRead
from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_session
from sqlalchemy.future import select
from ..models.users import User
from ..utils.security import hash_password, is_strong_password
from ..utils.unit_of_work import UnitOfWork

# Create a router for user-related endpoints
router = APIRouter()


# Endpoint to register a new user
@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(payload: UserCreate, db=Depends(get_session)):

    # create a unit of work instance
    uow = UnitOfWork(session=db)

    # check if user with email already exists
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # check password strength
    if not is_strong_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet strength requirements"
        )

    # hash the password
    hashed_password = hash_password(payload.password)

    # create new user instance
    new_user = User(
        email=payload.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    await uow.commit()

    await db.refresh(new_user)
    return new_user
