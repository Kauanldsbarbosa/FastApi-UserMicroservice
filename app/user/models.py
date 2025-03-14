import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.user.utils.calculate_expires_date import expires_date

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    social_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    password = Column(String, nullable=False)

    reset_tokens = relationship("ResetPasswordToken", back_populates="user", cascade="all, delete-orphan")

class ResetPasswordToken(Base):
    __tablename__ = 'reset_password_tokens'

    token = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: expires_date(token_expires_in=10))

    user = relationship("User", back_populates="reset_tokens")
