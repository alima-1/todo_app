from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, DateTime
)
from sqlalchemy.sql import func
from ..database import Base


class TrustedDevice(Base):
    __tablename__ = "trusted_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    device_id = Column(String, nullable=False)
    device_type = Column(String)
    browser = Column(String)
    os = Column(String)
    biometric_enabled = Column(Boolean, default=False)
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
