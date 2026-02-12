# models.py
from sqlalchemy import (
    Column, Integer, String, Boolean,
    DateTime
)
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)