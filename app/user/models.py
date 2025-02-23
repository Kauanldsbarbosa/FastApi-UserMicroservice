import uuid

from sqlalchemy import Column, Date, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class User(Base):
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    social_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    password = Column(String, nullable=False)
