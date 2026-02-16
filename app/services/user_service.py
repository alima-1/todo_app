# service.py
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy import select
from app.exceptions import UserAlreadyExistsError, WeakPasswordError
from app.models.users import User
from ..schemas.users import UserCreate, UserRead
from ..utils.security import hash_password, is_strong_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> UserRead:
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise UserAlreadyExistsError(user_data.email)

        if not is_strong_password(user_data.password):
            raise WeakPasswordError

        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password
        )
        self.db.add(new_user)
        self.db.flush()  # flush to get the new user's ID
        self.db.refresh(new_user)  # refresh to get the new user's data
        return UserRead.model_validate(new_user)
